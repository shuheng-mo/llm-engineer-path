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
