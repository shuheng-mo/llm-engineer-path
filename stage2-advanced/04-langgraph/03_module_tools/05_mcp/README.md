# MCP 模块说明

## 文件分组

```
servers/                FastMCP 自建 server（每个文件可单独 `python xxx_server.py` 启动）
  math_server.py        4.3.1 stdio 本地服务
  weather_server.py     4.3.2 streamable-http 远程服务
  data_server.py        4.4.1 Tools + 结构化输出
  files_server.py       4.4.2 Resources（参数化路径）
  prompts_server.py     4.4.3 Prompts 模板
  elicitation_server.py 4.5.4 Elicitation 交互式输入

01_client_multi_server.py            客户端：MultiServerMCPClient 同时连 stdio + http
02_client_load_resources_prompts.py  客户端：get_resources / get_prompt
03_session_stateful.py               客户端：持久 session（保留状态）

advanced/                            扩展（4.5）—— 可跳过
  01_interceptor_inject_context.py   注入用户上下文
  02_interceptor_store.py            访问 Store
  03_interceptor_auth.py             基于 state 的权限控制
  04_interceptor_compose.py          洋葱模式组合
  05_interceptor_command.py          Command 状态更新与跳转
  06_progress_callback.py            进度通知
  07_logging_callback.py             日志记录
  08_elicitation_client.py           Elicitation 客户端处理
```

## 运行流程

1. 先启动 server：`uv run python servers/math_server.py`（stdio 由 client 自动启动子进程）。
2. 在另一终端跑 client：`uv run python 01_client_multi_server.py`。
