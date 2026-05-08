# 04-langgraph — LangGraph 从入门到实战

来源：《LangGraph 从入门到实战课堂代码》。本目录按 6 个课程模块分层组织，每个知识点独立成 `.py`。

## 目录组织

```
01_module_basics/          模块一：核心概念与生态系统（环境配置 + Hello World）
02_module_graph/           模块二：图结构设计与状态管理（反思循环 / 并行 / 子图 / 客服综合实战）
03_module_tools/           模块三：工具系统与 Agent 增强（@tool / ToolRuntime / create_agent / Middleware / MCP）
04_module_persistence/     模块四：持久化与内存管理（Checkpointer / Store / 消息策略 / 完整案例）
05_module_human_in_loop/   模块五：人机协作与流式输出（研报助手 V4）
06_module_multi_agent/     模块六：多 Agent 系统（Subagents / Handoffs / Skills / Router 四大模式）
```

## 准备工作

1. 仓库根目录已通过 uv 配置好所有依赖（`langgraph` + `mcp` + `langgraph-checkpoint-postgres` 等都在 dep group 中）。在仓库根跑 `uv sync` 即可。
2. 复制 `.env.example` 为 `.env`，填入 `DASHSCOPE_API_KEY`。Postgres / Redis 示例需要额外的 `DB_URI` / `REDIS_*`；Tavily 示例（研报助手）需要 `TAVILY_API_KEY`。
3. `langgraph dev` 命令依赖 `langgraph-cli[inmem]`，已包含在依赖里。

## 运行单个示例

```bash
uv run python stage2-advanced/04-langgraph/01_module_basics/02_hello_world/01_simplest_graph.py
```

## 模块进度对照

| 模块 | 路径 | 核心知识点 |
|------|------|-----------|
| 一 | `01_module_basics/` | 环境配置、ChatTongyi 千问模型、最简 StateGraph |
| 二 | `02_module_graph/` | 反思循环、Fan-out/Fan-in、Hierarchical 子图、综合客服 |
| 三 | `03_module_tools/` | @tool / DocString / Pydantic args / ToolRuntime / create_agent / ToolNode / Middleware / MCP（FastMCP server + adapters client + 拦截器）|
| 四 | `04_module_persistence/` | InMemorySaver / Postgres / Redis / Store + 语义搜索 / Trim/Remove/Summarize / 完整 Postgres 案例 |
| 五 | `05_module_human_in_loop/` | `interrupt_before` + `update_state` 实现人工审核闭环 |
| 六 | `06_module_multi_agent/` | Subagents（电商）/ Handoffs（旅行）/ Skills（SQL）/ Router（多源知识库）|
