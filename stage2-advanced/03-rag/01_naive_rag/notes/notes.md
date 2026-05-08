# Naive RAG

1. 4代RAG范式演进: naive rag -> advanced rag -> graph rag -> agentic rag
2. RAG的基本流程：

```
文档 → Chunk → Embedding → Vector Store → Retrieve → Prompt → Model → Answer
```

需要注意的是Embedding Model在这个过程中很重要，文本片段向量化以及用户提问转查询向量化都依赖于Embedding Model的质量。

## 文件加载注意事项

1. 编码：确保文件编码正确，常见的编码格式有UTF-8、GBK等。错误的编码可能导致文本内容无法正确读取。
2. 大文件处理：大文件一次性加载内存可能溢出，懒加载、分批处理以及流式处理是常见的解决方案。
3. PDF中出现复杂结构：PDF文件可能包含表格、图像等复杂结构，使用专门的PDF解析库（如PyPDF2、pdfplumber、langchain的unstructured loader）可以更好地提取文本内容。
4. 网页动态内容：如果需要从网页加载数据，可能会遇到动态内容加载的问题，使用Selenium、Playwright等工具可以模拟浏览器行为，获取完整的网页内容跳过js渲染的内容无法获取的问题。

## 文本分割

三个问题：

1. 语义稀释，长文档直接embedding会导致语义稀释，无法捕捉到文档的细节信息。
2. 检索噪声，过大的文本块可能包含不相关的信息，增加检索的噪声。
3. 上下文限制，模型的输入长度有限，过长的文本块可能超出模型的输入限制，导致无法处理。

在使用splitter的过程中，chunk size和chunk overlap是两个重要的参数：

- chunk size：每个文本块的最大长度，通常根据模型的输入限制和文本内容的特点来设置。具体要看下游的Embedding Model或者其他模型的输入限制来设置，通常建议设置在模型输入限制的70%-80%左右，以留出足够的空间给其他输入内容。
- chunk overlap：文本块之间的重叠部分，通常设置为chunk size的10%-20%左右。重叠部分可以帮助模型更好地理解文本块之间的关系，减少信息丢失。

合适的separator可以帮助splitter更好地分割文本，常见的separator有换行符、句号、空格等。选择合适的separator可以根据文本内容的结构来决定，例如对于段落较长的文本，可以使用换行符作为separator，而对于句子较短的文本，可以使用句号作为separator。

## Embedding Model嵌入模型与嵌入的方式

简单理解： 嵌入是把文本转为高维向量的过程，嵌入模型是执行这个过程的工具，我们说的语义相似其实就是向量空间中的距离，高维向量在向量空间中约接近的文本在语义上也更相似。

主流的 Embedding 模型选择：

| 模型                    | 提供商      | 维度 | 特点               | 适用场景     |
| ----------------------- | ----------- | ---- | ------------------ | ------------ |
| text-embedding-3-small  | OpenAI      | 1536 | 性价比高，效果好   | 通用场景     |
| text-embedding-3-large  | OpenAI      | 3072 | 最高精度           | 高精度需求   |
| bge-large-zh            | HuggingFace | 1024 | 中文优化           | 中文场景     |
| bge-m3                  | HuggingFace | 1024 | 多语言支持         | 多语言场景   |
| DeepSeek Embedding      | DeepSeek    | 1024 | 成本极低           | 预算有限     |

## 向量数据库

向量数据库主要4件事：

1. 存储向量：将文本块的向量表示存储在数据库中，通常使用高效的数据结构来支持快速查询。
2. 索引构建：构建索引以加速向量检索，常见的索引方法包括树结构、哈希表等。
3. 向量检索：根据用户查询的向量表示，检索与之相似的文本块，通常使用距离度量（如欧氏距离、余弦相似度、点积）来衡量向量之间的相似度，最后返回Top K个最相似的文本块。
4. 更新和维护：支持向量的更新和维护，包括添加新的向量、删除旧的向量以及重新构建索引等操作。

主流向量数据库的对比：

| 数据库     | 类型         | 特点                  | 推荐场景                    |
| ---------- | ------------ | --------------------- | --------------------------- |
| Chroma     | 本地/嵌入式  | 简单易用，教学首选    | 开发调试、小规模应用        |
| FAISS      | 本地库       | Meta 开发，速度极快   | 大规模高性能场景            |
| Pinecone   | 云服务       | 全托管，开箱即用      | 生产环境                    |
| Milvus     | 分布式       | 开源，支持海量数据    | 企业级大规模部署            |
| Weaviate   | 云/自托管    | 支持混合搜索          | 需要关键词+向量混合检索     |

从上手的容用程度来说，Chroma是最简单的，FAISS需要一定的环境配置，Pinecone则完全免维护，Milvus和Weaviate适合有分布式需求的企业用户。该项目我们使用Chroma作为示例，后续可以根据需要切换到其他数据库。（参考`stage2-advanced/03-rag/01_naive_rag/04_vector_store/01_chroma_from_texts.py`等。）

### chroma四种构建索引方式的对比

| 构造方式                       | 一句话说明                  | 是否支持 metadata | 是否适合 RAG | 典型用途              |
| ------------------------------ | --------------------------- | ----------------- | ------------ | --------------------- |
| `from_texts()`                 | 直接从 string 构建向量库    | ×                 | 不推荐       | Demo、小测试          |
| `from_documents()`             | 从 Document 列表构建向量库  | ★★★★★             | 必需         | 实际项目、RAG         |
| `Chroma(persist_directory=…)`  | 加载已有向量库              | ★★★★              | 必需         | 持久化、生产环境      |
| `Chroma(client=…)`             | 使用 server 模式            | ★★★★              | 可选         | 大规模服务端部署      |

## Retriever检索器（或者叫召回器）

简单来说检索器将用户查询转为向量表示，并在向量数据库、BM25索引或者其他的数据源中检索与之相似的文本块。

### 检索器常见参数说明

| 参数 | 适用检索类型 | 作用说明 |
| --- | --- | --- |
| `k` | similarity / mmr | 返回 Top-k 个最相似文档（最常用） |
| `fetch_k` | mmr | 先从向量库取更多文档，再过滤成 k 个（提高结果多样性） |
| `lambda_mult` | mmr | 控制"相关性 vs 多样性"权重（MMR 专用，取值 0-1） |
| `filter` | similarity / mmr | 根据 metadata 过滤文档（例如筛选某个文件来源） |
| `score_threshold` | similarity | 设置相似度最低阈值（低于就不返回） |
| `distance_metric` | 部分向量库 | 指定向量距离算法（cosine / L2 / dot 等） |

### k 值的选择经验

| 场景 | k 推荐 |
| --- | --- |
| 结构清晰的内容（FAQ、定义类问答） | 2-4 |
| 数据较碎、chunk 很小，让 LLM 自行总结 | 5-8 |
| 需要广泛上下文 / 复杂查询多角度交叉引用 | 8-12 |

### MMR参数调优指南

| 参数 | 建议值 | 调优策略 |
| --- | --- | --- |
| `k` | 2-4 | 根据上下文窗口大小和 chunk 长度调整 |
| `lambda_mult` | 0.5-0.7 | 偏向相关性用 0.7+，偏向多样性用 0.3-0.5 |
| `score_threshold` | 0.6-0.8 | 宁缺毋滥用高阈值，召回优先用低阈值 |
| `fetch_k` | k 的 3-5 倍 | MMR 候选池大小，太小退化成 similarity，太大引入噪声 |

## RAG Runnable Pipeline

### 核心价值

LangChain 的 RAG 抽象不是"让 RAG 变聪明"，而是给一个充满胶水代码的领域提供 **"标准库 + 词汇表 + 生态系统"**。可以类比 Flask 之于 Web、pandas 之于数据。

它解决的四件事：

1. **词汇标准化** — `DocumentLoader / TextSplitter / Embeddings / VectorStore / Retriever / OutputParser / Tool` 全行业共识，协作、招聘、开源代码迁移成本骤降。
2. **集成生态** — 200+ Loader、几十个向量库、所有主流 LLM Provider 都有官方 wrapper。这是它真正的护城河。
3. **LCEL 组合范式** — `prompt | model | parser` 这个串联自带 stream / batch / async / astream_events，自己手写支持完整这四件套代码量会爆炸。
4. **端到端栈** — LangServe（部署）+ LangSmith（可观测性 / 评测）+ LangGraph（复杂工作流）原生集成，从 prototype 到 production 的路径相对完整。

它**不**解决的事：

- **RAG 本身的"智力"问题** — 切多大、用什么 embedding、要不要 reranker、混合检索权重 —— 全靠你自己。
- **评测与质量** — `RetrievalQA` 这种一行魔法链，效果几乎一定输给认真拼装的自定义 pipeline。
- **抽象税** — 栈深、import 路径乱、版本断代严重；只调一个 Provider 几个 endpoint 时裸 SDK 比 LangChain 更简洁。

### 什么时候用 / 不用

| 场景 | 该用 | 别用 |
| --- | --- | --- |
| Provider 数量 | 跨 ≥ 2 个 Provider | 只用一家 |
| 集成范围 | 用 ≥ 5 个 Loader / 数据源 | 自己一个 PDF parser 就够 |
| 工作流复杂度 | Agent / 多步链 / 人机协作 | 单次问答、纯生成 |
| 可观测性 | 已经用 LangSmith | 不在乎 trace |
| 性能 | 普通业务 | 性能敏感（抽象层有开销） |

### 一句话总结

**LangChain 给你砖，但不给你房子** —— 它的价值在协作层（工程化、标准化、生态）而非算法层（让 RAG 更准）。这个区分搞清楚了使用姿势就对了：拿它当 stdlib 用，别拿它当智能黑箱。
