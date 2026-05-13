# MCP 模块说明

## 文件分组

```
servers/                 FastMCP 自建 server（每个文件可单独 `python xxx_server.py` 启动）
  math_server.py         4.3.1 stdio 本地服务
  weather_server.py      4.3.2 streamable-http 远程服务
  data_server.py         4.4.1 Tools + 结构化输出
  files_server.py        4.4.2 Resources（参数化路径）
  prompts_server.py      4.4.3 Prompts 模板
  elicitation_server.py  4.5.4 Elicitation 交互式输入

clients/                 课程示例客户端（与上方 server 配对，演示标准用法）
  multi_server.py             MultiServerMCPClient 同时连 stdio + http
  load_resources_prompts.py   get_resources / get_prompt 综合演示
  session_stateful.py         持久 session（多次调用共享状态）
  fetch_files.py              ← 配 servers/files_server.py（拉取静态 + 参数化资源）
  fetch_user_profile.py       ← 配 servers/data_server.py（结构化输出工具）

advanced/                            扩展（4.5）—— 按重要度分两组：

  ▼ 生产必学（先看这三个）
    01_interceptor_inject_context.py   多租户上下文注入（user_id / api_key）★★★★★
    03_interceptor_auth.py             工具级权限控制（敏感工具 guardrail）★★★★★
    04_interceptor_compose.py          拦截器洋葱组合规则（>1 个拦截器必懂）★★★☆☆

  ▼ 按需查阅（用到再回头看）
    02_interceptor_store.py            个性化访问 Store
    05_interceptor_command.py          拦截器返回 Command 跳转 state
    06_progress_callback.py            进度通知（给前端进度条用）
    07_logging_callback.py             协议级日志（生产通常用 LangSmith / OTel 代替）
    08_elicitation_client.py           Elicitation 客户端处理（生态少用）
```

## 运行流程

1. 先启动 server：`uv run python servers/math_server.py`（stdio 由 client 自动启动子进程）。
2. 在另一终端跑 client：`uv run python clients/multi_server.py`。

## 注意

- `servers/` 下多个 streamable-http server 默认都监听 `:8000`，**同时只能跑一个**。
  如需并行，给其中一个加 `mcp.run(transport="streamable-http", port=8001)`。
- `clients/` 下的脚本都不带数字前缀，按文件名即可看出对应哪个 server / 演示什么能力。
