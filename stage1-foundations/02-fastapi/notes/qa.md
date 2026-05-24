# FastAPI 10 问 — 工程视角 + LLM 应用层视角

精选 10 个学完整章 FastAPI 后**值得反复推敲**的问题。
判断标准：**深入核心 · 接近实战 · LLM 应用层在用 · SDE 视角而非 leetcoder 视角**。

每题给出 Q + 简洁但有干货的 A，可作为面试自测 / Code Review 自检 / 设计决策清单。

---

## Q1. 同步 `def` vs 异步 `async def` — 路由函数到底用哪个？

很多人随手写 `async def`，结果在里头调 `requests.get()` / `time.sleep()` / `cv2.imread()`，**直接把整个事件循环卡住**，并发数瞬间退化成 1。

### 决策表

| 路由里调用的是 | 用什么 | 为什么 |
|---|---|---|
| `await ...` (httpx.AsyncClient / asyncpg / aiosqlite) | `async def` | 真正异步 IO，event loop 期间能服务其他请求 |
| 同步阻塞调用 (`requests`, `psycopg2`, `time.sleep`, 文件 IO) | `def` (普通函数) | FastAPI 自动放到 **threadpool** 里跑，不阻塞 event loop |
| 纯 CPU 密集 (matrix 计算 / 大字符串处理) | `def` + 考虑 `asyncio.to_thread` 或外部 worker | threadpool 但 GIL 限制；重活上 Celery/进程池 |

### LLM 场景具体落地

```python
# ✗ 反例：async def 里调同步 SDK，整个 worker 卡死
@app.post("/chat-bad")
async def chat_bad(req: ChatRequest):
    resp = openai.chat.completions.create(...)   # 同步阻塞！
    return resp

# ✓ 正例 A：用 AsyncOpenAI 客户端 + await
@app.post("/chat-async")
async def chat_async(req: ChatRequest):
    resp = await async_openai.chat.completions.create(...)
    return resp

# ✓ 正例 B：用普通 def，让 FastAPI 把它扔进 threadpool
@app.post("/chat-sync")
def chat_sync(req: ChatRequest):
    resp = openai.chat.completions.create(...)
    return resp
```

### 一句话

> **能 await 就用 `async def`，不能就用 `def`**。绝不要在 `async def` 里调阻塞函数。

---

## Q2. LLM 流式输出 — `StreamingResponse` / SSE / WebSocket 怎么选？

LLM 生成 token 时常用流式输出降首字延迟。三种方案：

| 方案 | 协议 | 浏览器原生支持 | 双向 | 典型场景 |
|---|---|---|---|---|
| `StreamingResponse` (chunked) | HTTP/1.1 transfer-encoding | ✓ (fetch) | ✗ 单向 | 命令行 / 后端调后端 |
| **SSE (Server-Sent Events)** | HTTP + `text/event-stream` | ✓ (EventSource) | ✗ 服务器→客户端 | **聊天界面 token 流（最常见）** |
| WebSocket | ws:// | ✓ | ✓ 双向 | 多轮对话 + 中途打断 / 工具确认 |

### SSE 最常用 — 因为它就是 HTTP

```python
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(req: ChatRequest):
    async def event_stream():
        async for chunk in llm.astream(req.messages):
            # SSE 协议格式：每条消息以 "data: " 开头，"\n\n" 结尾
            yield f"data: {chunk.content}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

前端 `EventSource("/chat")` 直接订阅，无需 WebSocket 握手开销，**且能穿越大多数 CDN/代理**（WebSocket 经常被企业防火墙拦）。

### 什么时候上 WebSocket

- 需要中途打断 LLM 生成（用户改主意） → 客户端发消息打断
- Agent 工具调用需要用户实时审批（HITL） → 双向交互
- 多客户端协作（多人共编辑） → 服务器 push 给所有人

### 一句话

> **聊天界面默认 SSE，需要双向交互才上 WebSocket，纯后端流就 StreamingResponse**。

---

## Q3. 同一 Pydantic 模型既做请求校验又做 LLM 结构化输出 — 是反模式还是最佳实践？

是**最佳实践**。这恰恰是 FastAPI + LLM 的甜蜜点。

### 工程价值

```python
class ExtractedInfo(BaseModel):
    name: str = Field(description="联系人姓名")
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    intent: Literal["complaint", "inquiry", "feedback"]

# 1. LLM 结构化输出 (LangChain)
chain = prompt | llm.with_structured_output(ExtractedInfo)
result: ExtractedInfo = await chain.ainvoke({"text": user_input})

# 2. 同一个模型校验 LLM 返回 — pattern / Literal 都生效
#    LLM 偶尔返回格式不对的手机号，这里直接 ValidationError

# 3. 同一个模型作 FastAPI 响应 schema — 文档自动生成
@app.post("/extract", response_model=ExtractedInfo)
async def extract(req: ExtractRequest) -> ExtractedInfo:
    return await chain.ainvoke(req.dict())
```

**一份 Pydantic 模型 = JSON Schema 给 LLM + 校验 LLM 输出 + OpenAPI 文档 + 前端 SDK 类型** — 四件事一份声明搞定。

### 注意区分纯 Pydantic vs SQLModel(table=True)

table 模式会跳过运行时 Pydantic 校验（参考 `ch06/library-magmt-system/README.md` 的"已知 quirk"）。生产规则：

- LLM 输出 / API 请求体 → 用 `BaseModel` 或 `SQLModel`（不带 `table=True`）
- 数据库表 → 用 `SQLModel(..., table=True)`
- 两者通过 `BookCreate` / `Book` 拆开

### 一句话

> Pydantic 模型是 **"统一类型契约"**，让 LLM、API、DB、文档、SDK 五个方向共用一份声明。

---

## Q4. 鉴权放中间件还是依赖项？两者怎么协作？

**默认放依赖项** (`Depends(get_current_user)`)，中间件只做横切的边缘工作。

### 对比

| 维度 | 中间件 | 依赖项 (Depends) |
|---|---|---|
| 粒度 | 全局 (或路径前缀) | 单路由 / router-level / 全局可选 |
| 拿用户对象 | 难（要塞 `request.state`） | 直接 `current_user: User = Depends(get_current_user)` |
| 跳过某些路由 | 难（黑名单写代码里） | 简单（路由不声明依赖即免鉴权） |
| 复用其他依赖 | ✗ 中间件层级在 Depends 之前 | ✓ 链式依赖 |

### 推荐分工

```python
# 中间件：日志、计时、Request-ID、CORS、GZip
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(GZipMiddleware, ...)

@app.middleware("http")
async def request_id(request, call_next):
    request.state.req_id = str(uuid.uuid4())
    return await call_next(request)

# 依赖项：鉴权、限流、租户隔离
router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_jwt)])

@router.get("/me")
async def me(user: User = Depends(get_current_user)):  # 路由能拿到 user 对象
    return user
```

### 一个微妙陷阱

CORS 中间件必须**早于鉴权依赖**处理 OPTIONS preflight（preflight 不带 Authorization），否则跨域请求永远 401。`add_middleware` 顺序是 LIFO —— CORS 应该**最后注册**（最外层先处理 OPTIONS）。

### 一句话

> **中间件管横切（CORS / 日志 / GZip），依赖项管业务（鉴权 / 限流 / 租户）**。

---

## Q5. LLM 调用 30 秒才返回 — BackgroundTasks 够吗？什么时候必须上 Celery？

**不够**。FastAPI 的 `BackgroundTasks` 适合 < 几秒、失败可丢的副作用（邮件 / 日志），LLM 长任务必须用真正的任务队列。

### 三档方案

| 任务类型 | 方案 | 客户端拿结果方式 |
|---|---|---|
| < 5s 实时 LLM 调用 | 路由内直接 await | 同步等响应 |
| 5-30s 中等任务（RAG + 生成） | **SSE 流式** | 边生成边推送 |
| > 30s 重任务（深度研究 / 批量推理） | **任务队列（Celery/Arq/Dramatiq）** | 提交后返回 task_id，客户端轮询 /tasks/{id} 或订阅 webhook |

### 长任务的工程范式

```python
# 1. 提交任务，立即返回 task_id
@app.post("/research")
async def submit(req: ResearchRequest):
    task = celery.send_task("deep_research", args=[req.query])
    return {"task_id": task.id, "status_url": f"/research/{task.id}"}

# 2. 客户端轮询状态
@app.get("/research/{task_id}")
async def status(task_id: str):
    res = celery.AsyncResult(task_id)
    return {"state": res.state, "result": res.result if res.ready() else None}
```

### 为什么 BackgroundTasks 不行

- 跟主进程同事件循环，重启就丢
- 没重试、没持久化、没限速、没监控
- worker 重启 = 所有飞行中任务消失（用户付了钱的 LLM 调用直接蒸发）

### 一句话

> **BackgroundTasks 是"打完仗扫战场"，不是"真打仗"**。LLM 长任务用 Celery + Redis 起步；轻一点的可以 Arq（纯 async + Redis）。

---

## Q6. FastAPI 测试 — `TestClient` 和 `httpx.AsyncClient` 各适用什么场景？

```python
# 方式 A: starlette TestClient (同步)
from fastapi.testclient import TestClient
def test_x():
    client = TestClient(app)
    resp = client.post("/foo", json={...})
    assert resp.status_code == 200

# 方式 B: httpx.AsyncClient + ASGITransport (异步)
import httpx, pytest

@pytest.mark.asyncio
async def test_x():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://t",
    ) as ac:
        resp = await ac.post("/foo", json={...})
```

### 怎么选

| 场景 | 选 |
|---|---|
| 简单单元测试，路由没有 async-only 依赖 | **TestClient**（语法简单） |
| 测试代码本身需要并发（多请求并发起、超时控制） | **AsyncClient** |
| 路由内部依赖项是 `async def get_session()` 这类生成器 | **AsyncClient** + `pytest-asyncio` |
| 想 mock httpx 调下游 LLM API | **AsyncClient** + `respx` 套件 |

### LLM 场景特别注意

LLM 调用慢、有 cost、有限速，测试必须 mock。两种典型路子：

```python
# 1. Patch SDK 客户端
def test_chat(monkeypatch):
    async def fake_complete(*a, **k):
        return MockResponse(content="hello")
    monkeypatch.setattr(async_openai.chat.completions, "create", fake_complete)
    ...

# 2. 用 respx 拦 HTTP 层
@respx.mock
def test_via_http():
    respx.post("https://api.openai.com/v1/chat/completions").respond(json={...})
    ...
```

### 一句话

> **简单同步测试用 TestClient，涉及 async 依赖 / 并发测试 / mock LLM 都用 httpx.AsyncClient**。

---

## Q7. 把 LLM Agent 包成 HTTP 服务 — 新人必踩的坑

按踩坑顺序（从浅到深）：

1. **超时没设** — uvicorn 默认无超时，长任务卡住 worker，新请求排队。配 `uvicorn --timeout-keep-alive 30` + `httpx.Timeout(60)` 调下游。

2. **没限并发** — 一个用户 100 个并发请求把 OpenAI 额度刷爆。用 `slowapi` 或 token bucket（Redis）。

3. **Token 成本失控** — 不限 prompt 长度。**必加** `max_tokens` 校验 + Pydantic 用 `max_length` 截断输入。

4. **Prompt Injection** — 用户输入直接拼进 system prompt，被 "ignore previous instructions" 攻陷。**用结构化模板**，把用户输入限制在 user message 内。

5. **响应没流式** — 同步返回 30s 用户必走。要么 SSE 流式，要么提交任务返回 task_id。

6. **错误暴露内部** — `try` 不包 LLM 调用，500 把 API key / SDK 报错 stacktrace 一股脑返给前端。**统一异常处理器** + 用户友好错误码。

7. **没记 trace** — LangSmith / OpenTelemetry 没接，问题来了无法复现。**每个请求挂 trace_id，从入口贯穿到 LLM 调用**。

8. **PII 入 prompt** — 用户提交的"帮我看下我的身份证号 110xxx"被原样发给第三方 LLM。**入口处脱敏**（详见 Q10）。

### 一句话

> **超时 + 限流 + token 上限 + 注入防护 + 流式 + 异常拦截 + trace + 脱敏** —— 这八条是把玩具变产品的及格线。

---

## Q8. API 版本演进 — `/v1/chat` 路径前缀 vs Header 协商 vs 单点切换？

LLM 模型迭代频繁（每月都可能有新版本），版本策略直接影响客户端能不能"无痛升级"。

### 三种方案

| 方式 | 形式 | 优点 | 缺点 |
|---|---|---|---|
| 路径前缀 | `/v1/chat` | URL 可读、便于路由、CDN 缓存友好 | URL 显式带版本，"破坏 RESTful 资源观" |
| Header 协商 | `Accept: application/vnd.myapp.v2+json` | URL 干净，资源观纯粹 | 难调试、curl 不友好、CDN 难缓存 |
| Query 参数 | `/chat?version=v2` | 简单 | 不推荐，污染查询参数语义 |

**实战上：路径前缀完胜，几乎所有真实 API 都用 `/v1/...`**（OpenAI、Anthropic、Stripe、GitHub 全是）。

### FastAPI 怎么落地

```python
# routers/v1/chat.py
v1 = APIRouter(prefix="/v1", tags=["v1"])

# routers/v2/chat.py
v2 = APIRouter(prefix="/v2", tags=["v2"])

# main.py
app.include_router(v1)
app.include_router(v2)
```

新版本平行运行，老版本标 `deprecated=True` 一段时间后下线。

### LLM 场景的具体考量

- **模型版本暴露在 URL 还是参数？** 推荐 `/v1/chat`（API 版本）+ body 里 `{"model": "claude-opus-4-5"}`（模型版本）。两者解耦。
- **prompt 模板版本** 也要管 — 模板改了输出形状变了，等于隐式破坏性变更。每个模板存版本号，请求里指定。

### 一句话

> **URL 路径前缀是事实标准**；老版本保留 6 个月，标 deprecated + 在响应头里加 `Sunset` header 提示客户端迁移。

---

## Q9. 配置和密钥管理 — `python-dotenv` / `pydantic-settings` / 云 Secret Manager 三层用法

```
开发期: .env 文件 + python-dotenv
   ↓
工程化: pydantic-settings (自动从 env 读 + 类型校验 + 默认值)
   ↓
生产: 云 Secret Manager (AWS Secrets / GCP Secret / Azure KeyVault / Vault)
```

### `pydantic-settings` 推荐写法

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 通用
    app_name: str = "my-llm-app"
    debug: bool = False

    # LLM 相关
    openai_api_key: str           # 必填，没设环境变量启动就崩
    anthropic_api_key: str | None = None
    default_model: str = "claude-opus-4-5"

    # JWT
    jwt_secret_key: str
    access_token_expire_minutes: int = 30

    # DB
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

# 用法
@app.get("/x")
def x(settings: Settings = Depends(get_settings)):
    ...
```

### 三个工程关键点

1. **必填字段不给默认值** — `openai_api_key: str` 而不是 `= ""`，没设环境变量启动就崩，避免线上"调 LLM 才发现 API key 是空字符串"。

2. **`@lru_cache` 单例化** — settings 读一次就缓存，每次 Depends 命中缓存。

3. **生产用 Secret Manager 不用 `.env`** — `.env` 进容器需要挂卷，密钥换轮要重启。正解：
   ```python
   # 启动时从云 Secret Manager 拉，写进 env
   import boto3, json, os
   sm = boto3.client("secretsmanager").get_secret_value(SecretId="prod/openai")
   os.environ["OPENAI_API_KEY"] = json.loads(sm["SecretString"])["api_key"]
   # 然后 pydantic-settings 照常读 env
   ```

### 一句话

> **本地 `.env` + 工程 `pydantic-settings` + 生产 Secret Manager**，三层组合既开发方便又安全合规。

---

## Q10. PII / 敏感数据脱敏 — FastAPI 哪一层最合适？

LLM 应用常见场景：用户输入含手机号 / 身份证 / 邮箱 / 公司内部 ID。直接发给第三方 LLM = 数据泄露 + 合规风险。

### 四层防御（从外到内）

```
请求进入
  │
  ▼
1. CORS / WAF              ← 网关层 (Cloudflare/Nginx) 防注入、限速
  │
  ▼
2. Middleware              ← 日志层脱敏 — 写 log 之前先 mask
  │
  ▼
3. Pydantic Validator      ← 入参校验 + 脱敏 — 模型字段层面处理
  │
  ▼
4. 业务层 LLM 调用前        ← 真正发给 LLM 的字符串再过一道
```

### 推荐落点：**Pydantic Validator + LLM 调用前再过一道**

```python
import re
from pydantic import BaseModel, field_validator

# 通用脱敏函数
PHONE_RE = re.compile(r"1[3-9]\d{9}")
EMAIL_RE = re.compile(r"[\w.-]+@[\w.-]+")

def mask_pii(text: str) -> str:
    text = PHONE_RE.sub(lambda m: m.group()[:3] + "****" + m.group()[-4:], text)
    text = EMAIL_RE.sub(lambda m: m.group().split("@")[0][:3] + "***@" + m.group().split("@")[1], text)
    return text

class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def strip_pii(cls, v: str) -> str:
        return mask_pii(v)   # ← 入口处自动脱敏
```

### 中间件做日志脱敏

```python
@app.middleware("http")
async def log_with_mask(request: Request, call_next):
    body = await request.body()
    safe = mask_pii(body.decode("utf-8", errors="ignore"))
    logger.info(f"req={safe}")   # 进日志的是脱敏后的
    return await call_next(request)
```

### 进阶：可逆脱敏 (tokenization)

- LLM 看到的是 `<phone_1>` 占位符 → 输出回来后用真值替回
- 真值存 Redis，键是占位符，TTL 短
- 优势：LLM 能正确理解上下文，但**真值永远不离开你的服务器**

### 一句话

> **Pydantic Validator 做入口脱敏 + Middleware 做日志脱敏 + LLM 调用前可逆 tokenization** —— 三道防线把 PII 严格控制在你自己的边界内。

---

## 学完这 10 题，你应该能回答这些"现实问题"

- 同事说"FastAPI 慢得很"，怎么定位是路由阻塞 event loop 还是 LLM 调用慢？
- 老板问"为什么不用 Flask？"，怎么从 async + Pydantic + OpenAPI 三角度回答？
- 安全团队说"你们 API 没有限流"，怎么 30 行代码加上 token bucket？
- 客户说"接口 30 秒太慢"，你能列出从同步 → SSE → Celery 的三档方案吗？
- 新人提交的 PR 用 `requests.get` 在 `async def` 里，你能一眼指出问题吗？

这 10 题不是"FastAPI 八股"，是**把 FastAPI 当生产工具使**所必须的判断力。
