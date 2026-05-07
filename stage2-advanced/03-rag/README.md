# 03-rag — RAG 应用开发

来源：《RAG应用开发课程代码》(stage2-advanced 第 3 模块)。本目录按课程章节梳理为独立的 .py 文件，每个文件聚焦一个知识点，可以单独运行。

## 目录组织

```
01_naive_rag/       一、Naive RAG（基础链路：Loader → Splitter → Embedding → VectorStore → Retriever → Pipeline → 实战）
02_advanced_rag/    二、Advanced RAG（预检索 / 检索 / 后检索 / 生成 四阶段优化）
03_graph_rag/       三、GraphRAG（基于 graphrag CLI 的实战流程）
04_agentic_rag/     四、Agentic RAG（LangGraph + 工具调用 + 规划反思 + 企业级 Demo）
```

## 准备工作

1. 在仓库根目录已经用 uv 配好了所有依赖（rag/langchain/langgraph 几个 group 默认安装），无需在子目录再建 venv。
2. 复制 `.env.example` 为 `.env`，填入 `DASHSCOPE_API_KEY`（阿里云通义千问，课程默认用这个）。
3. 课程示例引用了 `docs/LangChain.pdf`、`docs/RAG课程大纲.md` 等本地资料。请把自己的 PDF / Markdown 放到 `data/` 目录下，并在脚本里把路径改成实际文件名。

## 运行单个示例

```bash
# 示例：在仓库根运行 — 注意工作目录决定相对路径如何解析
uv run python stage2-advanced/03-rag/01_naive_rag/06_rag_pipeline/06_full_pipeline.py
```

## 模块进度

| 章节 | 路径 | 关键技术 |
|------|------|---------|
| 一 / 2 | `01_naive_rag/01_loaders/` | PyPDFLoader, UnstructuredMarkdownLoader, WebBaseLoader, DirectoryLoader |
| 一 / 3 | `01_naive_rag/02_text_splitting/` | RecursiveCharacterTextSplitter, TokenTextSplitter |
| 一 / 4 | `01_naive_rag/03_embedding/` | OpenAIEmbeddings, DashScopeEmbeddings |
| 一 / 5 | `01_naive_rag/04_vector_store/` | Chroma 基础/持久化/Metadata 过滤 |
| 一 / 6 | `01_naive_rag/05_retriever/` | `vectorstore.as_retriever()` |
| 一 / 7 | `01_naive_rag/06_rag_pipeline/` | LCEL Runnable Pipeline, astream_events 调试 |
| 一 / 8 | `01_naive_rag/07_pdf_assistant/` | 本地 PDF 阅读助手（CLI 实战） |
| 二 / 1 | `02_advanced_rag/01_pre_retrieval_chunking/` | Sentence Window / Parent Document / Semantic Chunking |
| 二 / 2 | `02_advanced_rag/02_query_understanding/` | Query Rewriting / Multi-Query / HyDE / Decomposition |
| 二 / 3 | `02_advanced_rag/03_hybrid_retrieval/` | BM25, Ensemble, RRF, Multi-Route |
| 二 / 4 | `02_advanced_rag/04_reranking/` | Cross-Encoder (BGE) / LLM Reranker |
| 二 / 5 | `02_advanced_rag/05_context_processing/` | Long Context Reorder, Compression |
| 二 / 6 | `02_advanced_rag/06_generation/` | RAG Prompt 模板 / Self-RAG / Adaptive-RAG |
| 二 / 7 | `02_advanced_rag/07_advanced_assistant/` | Advanced RAG 综合助手 |
| 三 | `03_graph_rag/` | graphrag CLI（Local / Global / DRIFT search） |
| 四 / 1-2 | `04_agentic_rag/01_paradigm/`, `02_agent_rag_mvp/` | LangGraph + Tool MVP |
| 四 / 3 | `04_agentic_rag/03_planning_reflection/` | Planner + Executor + Reflector |
| 四 / 4 | `04_agentic_rag/04_enterprise_demo/` | 企业级（Planner + Corrective RAG SubGraph） |
