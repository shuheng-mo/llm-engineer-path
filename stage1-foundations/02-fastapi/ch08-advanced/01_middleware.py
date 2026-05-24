"""8.1 自定义中间件 — 请求计时 + Request-ID 注入 + 中间件顺序

中间件 (middleware) 是 ASGI 层面的 "包裹层" — 包在路由处理函数外面，
请求进入路由之前 / 离开路由之后都会经过它，可以：
  - 给所有响应加 header
  - 记录日志、计时
  - 鉴权 (虽然这种场景更推荐用 Depends)
  - 修改请求/响应体 (慎用，性能成本高)

中间件顺序：**后注册的先执行** (LIFO)，类似洋葱模型：
  Request:  外层 ─→ 内层 ─→ 路由
  Response: 路由 ─→ 内层 ─→ 外层

运行: uv run uvicorn 01_middleware:app --reload
测试:
    curl -i http://127.0.0.1:8000/hello
    # 响应头里会看到:
    #   X-Process-Time: 0.0001
    #   X-Request-ID: <uuid>
"""

import time
import uuid

from fastapi import FastAPI, Request

app = FastAPI(title="Middleware Demo")


# ── 中间件 1: 请求计时 ──────────────────────────────────────────
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """记录每个请求的处理耗时，写到响应 header X-Process-Time"""
    start = time.perf_counter()
    response = await call_next(request)  # 调用下游中间件 / 路由
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.6f}"
    return response


# ── 中间件 2: 注入 Request-ID (分布式追踪用) ─────────────────────
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """给每个请求分配唯一 ID，写进响应 header；如果客户端传了就沿用 (链路追踪)"""
    req_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    # 把 req_id 挂到 request.state，路由函数可以通过 request.state.req_id 拿到
    request.state.req_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


# ── 路由 ──────────────────────────────────────────────────────────
@app.get("/hello")
async def hello(request: Request):
    """路由函数可以通过 request.state 访问中间件挂上的属性"""
    return {"message": "Hello", "request_id": request.state.req_id}


@app.get("/slow")
async def slow():
    """这个接口故意慢一点，方便观察 X-Process-Time"""
    time.sleep(0.5)
    return {"message": "slow done"}


# ── 中间件顺序演示 ────────────────────────────────────────────────
# 上面注册顺序: timing → request_id
# 实际执行顺序 (LIFO):
#   Request 进入: request_id 先执行 → timing → 路由
#   Response 返回: 路由 → timing → request_id 最后执行
# 所以 X-Request-ID 这个 header 是最后设置的 (最外层)
# 想验证：把 print 加到每个中间件的 start / end 就能看到洋葱嵌套
