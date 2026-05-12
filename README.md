# llm-engineer-path

大模型开发训练营学习仓库 — 按训练营三阶段组织的学习沙盒。每个编号目录是独立的学习模块，互不依赖。

> 仓库整体约定（Python 版本、`uv` 用法、依赖分组等）见 [CLAUDE.md](./CLAUDE.md)。

---

## Stage 1 — 夯实基础（[stage1-foundations/](./stage1-foundations))

Python / FastAPI / MySQL / LLM 概念 / Prompt 工程。

| 模块 | 内容 |
| --- | --- |
| [01-python](./stage1-foundations/01-python) | Python 语法与工程基础 |
| [02-fastapi](./stage1-foundations/02-fastapi) | FastAPI Web 框架 |
| [03-mysql](./stage1-foundations/03-mysql) | MySQL 数据库基础 |
| [04-llm-basics](./stage1-foundations/04-llm-basics) | 大模型核心概念 |
| [05-prompt-engineering](./stage1-foundations/05-prompt-engineering) | Prompt 工程 |

---

## Stage 2 — 系统进阶（[stage2-advanced/](./stage2-advanced))

LangChain → RAG → LangGraph → Capstone → Finetune → 算法。

### [01-langchain](./stage2-advanced/01-langchain) — LangChain 入门与实战

| 章节 | 跳转 |
| --- | --- |
| 基础 | [01_basics](./stage2-advanced/01-langchain/01_basics) |
| 模型 | [02_models](./stage2-advanced/01-langchain/02_models) |
| Prompt 模板 | [03_prompts](./stage2-advanced/01-langchain/03_prompts) |
| 输出解析器 | [04_parsers](./stage2-advanced/01-langchain/04_parsers) |
| LCEL 表达式语言 | [05_lcel](./stage2-advanced/01-langchain/05_lcel) |
| Memory 记忆 | [06_memory](./stage2-advanced/01-langchain/06_memory) |
| Tools 工具调用 | [07_tools](./stage2-advanced/01-langchain/07_tools) |

### [02-redis](./stage2-advanced/02-redis) — Redis（待开始）

### [03-rag](./stage2-advanced/03-rag) — RAG 应用开发

| 章节 | 跳转 |
| --- | --- |
| Naive RAG | [01_naive_rag](./stage2-advanced/03-rag/01_naive_rag) — Loaders / Splitting / Embedding / Vector Store / Retriever / Pipeline / PDF 助手 |
| Advanced RAG | [02_advanced_rag](./stage2-advanced/03-rag/02_advanced_rag) — 预检索分块、查询理解、混合检索、Rerank、上下文处理、生成、综合助手 |
| Graph RAG | [03_graph_rag](./stage2-advanced/03-rag/03_graph_rag) |
| Agentic RAG | [04_agentic_rag](./stage2-advanced/03-rag/04_agentic_rag) — Paradigm / MVP / Planning & Reflection / 企业 Demo |
| 课堂笔记 | [notes](./stage2-advanced/03-rag/notes) |

### [04-langgraph](./stage2-advanced/04-langgraph) — LangGraph 从入门到实战

| 模块 | 跳转 |
| --- | --- |
| 基础 | [01_module_basics](./stage2-advanced/04-langgraph/01_module_basics) |
| Graph 构图 | [02_module_graph](./stage2-advanced/04-langgraph/02_module_graph) |
| Tools 工具 | [03_module_tools](./stage2-advanced/04-langgraph/03_module_tools) — 含 [05_mcp](./stage2-advanced/04-langgraph/03_module_tools/05_mcp) |
| 持久化 | [04_module_persistence](./stage2-advanced/04-langgraph/04_module_persistence) — Checkpointer / Store / 消息策略 / 全流程 Demo |
| Human-in-the-loop | [05_module_human_in_loop](./stage2-advanced/04-langgraph/05_module_human_in_loop) |
| 多 Agent | [06_module_multi_agent](./stage2-advanced/04-langgraph/06_module_multi_agent) — Subagents / Handoffs / Skills / Router |

### [05-mcp-a2a](./stage2-advanced/05-mcp-a2a) — MCP & Agent-to-Agent（待开始）

### [06-travel-assistant](./stage2-advanced/06-travel-assistant) — 知行旅游助手（Capstone 综合项目）

### [07-finetune](./stage2-advanced/07-finetune) — 模型微调（Llama-Factory，使用前看 CLAUDE.md 说明）

### [08-algo](./stage2-advanced/08-algo) — 算法相关

---

## Stage 3 — 面试冲刺（[stage3-interview/](./stage3-interview))

| 模块 | 内容 |
| --- | --- |
| [01-qa-bank](./stage3-interview/01-qa-bank) | 八股 / 题库 |
| [02-resume](./stage3-interview/02-resume) | 简历 |
| [03-mock-interviews](./stage3-interview/03-mock-interviews) | 模拟面试记录 |

---

## 快速开始

```bash
uv sync                        # 默认依赖（除 finetune 外全部）
uv sync --group finetune       # 进入 stage2/07-finetune 时再装重型 ML 栈
uv run python <script.py>      # 不激活 venv 直接运行
```

详细命令与 dependency-group → 模块映射见 [CLAUDE.md](./CLAUDE.md)。

---

## Git 提交规范（pre-commit + Conventional Commits）

仓库通过 [pre-commit](https://pre-commit.com/) 在 git 钩子里跑两件事：

1. **`commit-msg` 阶段** —— 用 [`conventional-pre-commit`](https://github.com/compilerla/conventional-pre-commit) 校验 commit message 必须以 `feat: / fix: / chore: ...` 开头。
2. **`pre-commit` 阶段** —— 跑 `ruff-format`（代码格式化）+ 通用小检查（行尾空格、文件末尾换行、YAML/TOML 语法、超大文件守门）。

> 配置文件：[`.pre-commit-config.yaml`](./.pre-commit-config.yaml) · `pre-commit` 已写入 `pyproject.toml` 的 `dev` group。

### 一次性激活（克隆到新机器后必跑）

```bash
uv sync                                                              # 先把 dev 依赖装上（包含 pre-commit）
uv run pre-commit install --hook-type commit-msg --hook-type pre-commit  # 把钩子写进 .git/hooks/
uv run pre-commit run --all-files                                    # 可选：第一次对全仓库走一遍
```

> 第三步首次会比较慢，pre-commit 要拉取各 hook 仓库并建沙盒；之后都走缓存。

### 日常使用

```bash
git commit -m "随便写一句"
# ✗ subject does not start with conventional commit type — 被拒

git commit -m "feat: 添加 LangGraph 多 Agent 路由示例"
# ✓ 通过；同时 ruff-format 会自动格式化已 stage 的 .py 文件
```

如果 ruff-format **改了文件**，commit 会先失败、提示你把修改过的文件重新 `git add` 再 commit —— 这是 pre-commit 的正常行为，不是 bug。

### 允许的 commit type

`feat` / `fix` / `chore` / `docs` / `refactor` / `test` / `perf` / `style` / `build` / `ci` / `revert`

格式约定（来自 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)）：

```text
<type>(<可选 scope>): <祈使语气、小写、不带句号、≤72 字符>

<可选 body：解释为什么这么改，不是改了什么>
```

例：

- `feat(rag): 实现 RRF 融合算法`
- `fix(langgraph): checkpoint 在 Postgres 异步场景下漏写`
- `chore: 升级 langchain 到 0.3.20`
- `docs: 补充 Agentic RAG 笔记`

### 紧急绕过（不推荐）

```bash
git commit --no-verify -m "..."   # 跳过所有 hook
```

仅在你明确知道某个 hook 误报、且会马上修的场景用。**不要用 `--no-verify` 来"省事"**——规范靠绕过就崩了。

### 为什么 ruff lint 没开

本仓库是按编号顺序展开的**教学代码**：

- `05_run_demo.py` 故意引用 `04_supervisor.py` 里定义的名字 → ruff 报 `F821 Undefined name`，但其实是有意为之
- 大量文件先写长 docstring / `load_dotenv()` 再 import → ruff 报 `E402`，但这是教学风格

所以 `.pre-commit-config.yaml` 里**只跑 `ruff-format`，不跑 `ruff` lint**。想手动 lint 时：

```bash
uv run ruff check .          # 看一眼有什么问题
uv run ruff check . --fix    # 顺手自动修可修的
```

### 想给 GitLens / VS Code 的 AI Commit 也加上 Conventional Commits 模板

在 VS Code `settings.json` 里加：

```json
"gitlens.ai.generateCommitMessage.customInstructions": "Use Conventional Commits format. Start with one of: feat, fix, chore, docs, refactor, test, perf, style, build, ci, revert. Format: '<type>(<scope>): <imperative subject, lower case, no period, ≤72 chars>'. Body in Chinese if diff comments are Chinese, explain WHY not WHAT."
```

这样 AI 生成的 message 直接合规，pre-commit 也不会拒它。
