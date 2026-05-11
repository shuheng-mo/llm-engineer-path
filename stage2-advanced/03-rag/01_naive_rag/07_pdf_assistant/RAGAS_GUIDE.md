# Ragas — RAG 系统量化评测指南

> 适用版本：Ragas 0.4+（新版 API，从 `ragas.metrics.collections` 导入）

## 一、为什么需要 Ragas

Naive RAG 跑通之后，下一个问题就是 **"它好不好？"**。这个问题不能靠肉眼判断 — 50 个问题人工读一遍就 1 小时，无法持续优化。Ragas 解决的就是：

> 用 **LLM 给 LLM 判卷**，把 RAG 系统的好坏拆解成 4 个可量化的维度，让你**改一行参数就能跑出客观分数对比**。

它不是替代肉眼评估，而是把"凭感觉"变成"看数字"，让优化有方向。

---

## 二、四大核心指标

Ragas 把 RAG 流程拆成**检索阶段**和**生成阶段**两段，每段两个指标，共四个：

| 阶段 | 指标 | 衡量什么 | 需要的输入 | 直觉理解 |
| --- | --- | --- | --- | --- |
| 生成 | **Faithfulness（忠实度）** | 回答里的每句话能不能在检索结果里找到依据 | response + retrieved_contexts | "LLM 有没有编造？" |
| 生成 | **Answer Relevancy（回答相关性）** | 回答是不是切题，没有多余铺垫 | user_input + response | "LLM 有没有跑题？" |
| 检索 | **Context Precision（上下文精确率）** | 检索回来的 chunk 有多少是有用的 | user_input + reference + retrieved_contexts | "检索结果有没有噪音？" |
| 检索 | **Context Recall（上下文召回率）** | 标准答案的关键信息有多少被检索到 | user_input + reference + retrieved_contexts | "检索有没有漏？" |

**关键区分**：

- **Faithfulness / AnswerRelevancy** → 不需要标准答案（reference），只看 LLM 输出本身和检索结果
- **ContextPrecision / ContextRecall** → **必须有 reference**（人工标注的标准答案），用来判定"这个 chunk 是不是该被检索到"

所以**写测试集时必须人工写 reference**，这是 Ragas 评测最大的成本。

---

## 三、每个指标的内部算法

理解算法是为了知道分数怎么算出来的、低分时该改哪里。

### Faithfulness

1. 让 LLM 把 `response` 拆成 N 个 **claim（独立断言）**
2. 对每个 claim，让 LLM 判断"能否在 `retrieved_contexts` 里找到证据"
3. `Faithfulness = 有依据的 claim 数 / 总 claim 数`

**0.5 的典型场景**：5 句话回答，2 句有依据 3 句是模型自己加的。

### Answer Relevancy

1. 让 LLM 从 `response` **反推** N 个候选问题
2. 计算这 N 个候选问题与 `user_input` 的 **embedding 余弦相似度**
3. `AnswerRelevancy = 相似度的平均值`

**0.5 的典型场景**：回答前面有大段铺垫，最后一句才回答 — 反推出的候选问题里一半是铺垫话题。

### Context Precision

1. 对 `retrieved_contexts` 里的**每个 chunk**，让 LLM 判断"这个 chunk 对回答 user_input 有没有帮助"（用 reference 当依据）
2. 按排名加权计算（前几个 chunk 中有用占比的高低更影响分数）
3. `Precision = 加权后有用 chunk 比例`

**0.33 的典型场景**：检索回 3 个 chunk，只有 1 个真正相关。

### Context Recall

1. 让 LLM 把 `reference` 拆成 N 个 **fact（事实点）**
2. 对每个 fact，判断"能不能在 `retrieved_contexts` 里找到支撑"
3. `Recall = 有支撑的 fact 数 / 总 fact 数`

**0.5 的典型场景**：标准答案有 4 个关键事实，检索回的 chunk 只覆盖了 2 个。

---

## 四、把 Ragas 接入 PDF 助手 — 三步走

### Step 1：给助手加 `ask_with_contexts()` 方法

Ragas 需要 `retrieved_contexts`（检索回来的纯文本片段列表），而原始 `ask()` 只返回 LLM 答案。所以**不修改原有逻辑**，只**新增**一个方法：

```python
def ask_with_contexts(self, question: str) -> tuple[str, list[str]]:
    retrieved_docs = self.retriever.invoke(question)
    retrieved_contexts = [doc.page_content for doc in retrieved_docs]
    answer = self.ask(question)
    return answer, retrieved_contexts
```

✅ **已经加好了**，见 `pdf_reading_assistant.py:154`。

### Step 2：写测试集（**最贵的一步**）

`ragas/test_dataset.json` 格式：

```json
[
  {
    "user_input": "你的问题",
    "reference": "你人工标注的标准答案（请尽量覆盖关键事实点）"
  }
]
```

写 reference 的两个原则：

1. **不要太短** — 否则 Recall 永远满分（只有 1 个 fact）
2. **不要太啰嗦** — 否则 Recall 永远低（10 个 fact 检索能全覆盖的概率很低）

我已经预置了 10 条针对 `data/LangChain.pdf` 的测试题，可以直接跑或者按需修改。

### Step 3：跑评估

```bash
cd stage2-advanced/03-rag/01_naive_rag/07_pdf_assistant/ragas
uv run python run_evaluation.py
```

输出：

- 控制台打印整体平均分 + 逐题明细
- 写入 `evaluation_report.json` 完整数据（包含每题的 retrieved_contexts 用于二次分析）

---

## 五、报告解读 — 看到低分该改哪里

每个指标对应不同的改进方向。**这才是 Ragas 的最大价值** — 给你提示"该往哪儿优化"。

### Faithfulness 低 → 改 Prompt 和 temperature

LLM 在编造。三招：

1. **Prompt 加强约束**：明写"必须 100% 基于参考文档，文档没说的也不能说"
2. **temperature 调低**：从 0.3 → 0.1，让 LLM 更保守
3. **去掉"补充信息"类指令**：原 prompt 如果鼓励"展开""扩展"，要删掉

### Answer Relevancy 低 → 改 Prompt

LLM 在跑题或铺垫。在 system prompt 加一条：

```
直接回答用户问题，不要在回答前加任何背景介绍或铺垫。
```

如果回答里反复出现"首先，我们了解一下背景..."这种铺垫话术，就要严控。

### Context Precision 低 → 检索器返回了太多无关 chunk

1. **减小 `k`**：从 4 → 3，更严格过滤
2. **提高 `lambda_mult`**：从默认 0.5 → 0.7，MMR 更偏向相关性而非多样性
3. **加 reranker**：用 Cross-Encoder 对召回的 fetch_k 个候选精排（Advanced RAG 的标配）

### Context Recall 低 → 检索器漏了关键信息

1. **加大 `k`**：从 4 → 6，给 LLM 更多参考
2. **加大 `fetch_k`**：从 10 → 20，扩大候选池
3. **调小 `chunk_size`**：400 → 200，让关键信息更不容易被切到一起
4. **加大 `chunk_overlap`**：50 → 100，减少边界信息丢失
5. **改完 chunk_size 必须删除旧向量库**：`rm -rf data/pdf_assistant_db/` 重跑

> 注意 **Precision 和 Recall 互相博弈**：调大 k 召回更全但精确率下降，调小 k 反之。要找到平衡点（通常 k=4-6 是甜区）。

---

## 六、四大常见陷阱

1. **测试集太小不可信** — 至少 10 题，最好 30+，否则方差太大
2. **reference 自己写太草率** — Recall 直接受 reference 质量影响，不要随便写一行
3. **评估时忘了 clear_history** — 多轮对话历史会污染评估结果，每题独立时必须清
4. **判卷模型用同一个 LLM** — 如果生成和判卷都用 qwen-plus，可能存在"自己判自己分高"的偏差。生产中可以用 gpt-4o 当判卷模型，qwen-plus 当被评模型

---

## 七、本目录文件清单

```
07_pdf_assistant/
├── pdf_reading_assistant.py     # PDF 助手主类（已加 ask_with_contexts）
├── ANALYSIS.md                  # 助手能力对标 NotebookLM 的差距分析
├── RAGAS_GUIDE.md               # 本文档
└── ragas/                       # Ragas 评估子模块
    ├── __init__.py
    ├── 01_ragas_basics.py       # Faithfulness + AnswerRelevancy 演示
    ├── 02_ragas_metrics.py      # ContextPrecision + ContextRecall 演示
    ├── rag_evaluator.py         # 封装好的 RAGEvaluator 类
    ├── test_dataset.json        # 10 道针对 LangChain.pdf 的测试题
    └── run_evaluation.py        # 端到端入口，跑完产出 evaluation_report.json
```

## 八、推荐学习顺序

1. **先跑 `01_ragas_basics.py`** — 理解两个生成阶段指标，看好/坏样本的分数差
2. **再跑 `02_ragas_metrics.py`** — 理解两个检索阶段指标，看噪音/漏检的分数差
3. **跑 `rag_evaluator.py`** — 验证封装类能调通
4. **跑 `run_evaluation.py`** — 完整评估当前 PDF 助手，拿到 baseline 分数
5. **改一个参数（如 k=4 → 6）重跑** — 观察哪个指标变好、哪个变差，建立对参数的直觉

完成这 5 步之后，你就能用数字来驱动 RAG 优化，而不是凭感觉。这就是从"玩具 RAG"到"工程化 RAG"的分水岭。
