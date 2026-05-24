"""8.2 内置中间件 — CORS + GZip

FastAPI 内置一批常用中间件，无需自己写。最常用的两个：

1. CORSMiddleware — 浏览器跨域请求必备
   - SPA (React/Vue) 部署在 https://app.com，调 API https://api.com → 跨域
   - 浏览器默认会阻止跨域 fetch；服务端必须返回 Access-Control-Allow-* 头允许

2. GZipMiddleware — 自动压缩响应体
   - JSON 响应通常压缩率 80%+
   - LLM API 返回大段文本 / RAG 检索结果时收益巨大

运行: uv run uvicorn 02_cors_gzip:app --reload
测试 CORS:
    # 模拟跨域 preflight 请求
    curl -i -X OPTIONS http://127.0.0.1:8000/data \\
      -H "Origin: http://localhost:5173" \\
      -H "Access-Control-Request-Method: GET"
测试 GZip:
    curl -i --compressed http://127.0.0.1:8000/big -H "Accept-Encoding: gzip"
    # 响应头会有 Content-Encoding: gzip
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="Built-in Middleware Demo")

# ── CORS 中间件 ──────────────────────────────────────────────────
# allow_origins: 白名单。开发期可以 ["*"] 全允许，生产**严禁**用 *
#                因为 allow_credentials=True 时 Cookie 会被跨域携带，是安全风险。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite SPA 默认端口
        "http://localhost:3000",  # Next.js / CRA 默认端口
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET/POST/PUT/DELETE/OPTIONS...
    allow_headers=["*"],  # Authorization, Content-Type 等
    expose_headers=["X-Request-ID"],  # 让前端 JS 能读到这个自定义响应头
)

# ── GZip 中间件 ──────────────────────────────────────────────────
# minimum_size: 响应体超过这个字节才压缩 (小响应压缩反而浪费 CPU)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/data")
async def data():
    """普通 JSON 响应，方便测试 CORS preflight"""
    return {"items": [1, 2, 3]}


@app.get("/big")
async def big_response():
    """大响应触发 GZip 压缩 (重复 500 次字符串)"""
    return {"text": "FastAPI is awesome! " * 500}
