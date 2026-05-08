# 01-langchain — LangChain 入门与实战

来源：《LangChain入门与实战课程代码》。本目录按 7 章组织，每个知识点独立成 `.py`。

## 目录组织

```
01_basics/        第二章：环境配置 + 第一个 LangChain 程序（ChatTongyi）
02_models/        第三章：LLM/ChatModel、参数、多 Provider、流式、批量
03_prompts/       第四章：PromptTemplate / ChatPromptTemplate / Few-shot / 最佳实践
04_parsers/       第五章：Output Parsers / Structured Output / 高级解析（纠错/抽取）
05_lcel/          第六章：LCEL Runnables（Sequence / Parallel / Branch / Lambda / 调试）
06_memory/        第七章：短期记忆（MessageHistory / Redis / Postgres）+ 长期记忆（VectorStore / Profile）
07_tools/         第八章：@tool / args_schema / bind_tools / Function Calling / 多工具助手
```

## 准备工作

1. 仓库根目录已通过 uv 配好所有依赖（`langchain` group 默认安装）。复制 `.env.example` 为 `.env`，填入 `DASHSCOPE_API_KEY`。
2. 第七章 Redis / Postgres 示例需要本地起对应服务，并填 `REDIS_*` / `PG_*` 环境变量。
3. 第三章多 Provider 示例（`02_models/07_multi_provider.py`）若想跑 OpenAI / Anthropic / Google，需要额外的 API Key；只跑 Qwen 路径不用。

## 运行单个示例

```bash
uv run python stage2-advanced/01-langchain/01_basics/02_first_program.py
```
