# 笔记

## 为什么 OpenAPI (Swagger) 和 JSON Schema 在现代 Web 开发中重要

### 一句话本质

**它们是机器可读的"API 合同"** —— 把"接口长什么样"从模糊文档变成代码、工具、AI 都能直接消费的标准格式。一次定义，全栈受益。

### 七个关键价值

**1. 消除文档与代码漂移**
schema 从代码自动生成（FastAPI/NestJS/Spring 都支持），改字段时文档、校验、客户端代码同步变更。FastAPI 的 `/docs` 就是从函数签名 + Pydantic 模型推导出来的，不用手写一行文档。

**2. 系统边界的强制校验**
JSON Schema 是"边界处的类型系统"：
```
不可信外部输入 ──[JSON Schema 校验]──> 内部代码裸用，零防御
```
Pydantic `BaseModel` 本质就是 JSON Schema。校验在请求进入业务函数前完成，业务代码可以乐观假设数据合法。

**3. 跨语言代码生成**
一份 OpenAPI 可一键派生 N 种语言的客户端 SDK（TS/Go/Swift/Kotlin/…），前后端类型对齐零成本，可真正"合同优先"分头开发。

**4. 一整套生态工具的入口**
产出 OpenAPI 即免费获得：Swagger UI/ReDoc（文档）、Postman/Bruno（导入测试）、Prism（Mock 服务）、Kong/APISIX（网关路由）、Schemathesis（基于 schema 的 fuzzing）。

**5. AI/LLM 工具调用的协议基础（最重要！）**
- OpenAI / Anthropic / Gemini 的 tool definitions 都用 JSON Schema
- LangChain `@tool` 装饰器内部就是把函数签名转 JSON Schema
- MCP 的工具描述也用 JSON Schema
- `llm.with_structured_output(Pydantic模型)` 底层走 Pydantic → JSON Schema → 喂给 LLM

**一个 FastAPI 后端几乎不用改代码就能暴露成 LLM 可用的工具集** —— 这是它在 AI 工程领域的压倒性优势。

**6. 微服务的"通用语"**
明确契约 → 消费者订阅变更、schema diff 工具告警、`deprecated` 字段管灰度。没有 schema 的微服务就是"分布式的混乱"。

**7. 文档只是副产品**
真正价值是把 API 变成**可编程对象**：代码生成、校验、Mock、安全扫描、网关配置、监控、LLM 工具调用 —— 这些场景统统不再需要"人对人地约定"。

### 与本训练营的关联

FastAPI 这一节学的不是"怎么写 Web 后端"，而是**"怎么用类型系统约束系统边界"**。这套思路在 stage2 的 `05-mcp-a2a/` 和 `06-travel-assistant/` 里会反复出现 —— LLM Agent 工程的本质就是用 JSON Schema 给 LLM 划清"能调什么、要传什么、会返回什么"。

---

## Uvicorn 是什么？FastAPI 离得开它吗？

很多人学 FastAPI 时会跳过这层认知，但它是理解整个 Python 异步 Web 栈的关键。

### 职责分工

- **FastAPI = 应用框架**：定义路由、解析参数、调用业务、生成 OpenAPI。**它不会说 HTTP。**
- **Uvicorn = ASGI 服务器**：监听端口、解析 HTTP 协议、把请求转成 Python 对象**喂给** FastAPI。

类比：FastAPI 是厨师（处理订单），Uvicorn 是前台 + 跑堂（接客 + 送菜）。光有厨师不能开店。

### 分层结构

```
浏览器/HTTP 客户端
      │ TCP + HTTP/1.1 (HTTP/2, WebSocket)
      ▼
   Uvicorn       ← 协议层：headers/body、超时、keep-alive、TLS、WS 握手
      │ ASGI scope + receive/send (社区标准 async 接口)
      ▼
   FastAPI       ← 应用层：路由、Pydantic 校验、业务逻辑
```

**ASGI** (Asynchronous Server Gateway Interface) 是 Python 社区标准，规定"服务器和应用怎么对接"。这层抽象让两边都能独立演进、自由替换。类比 Java 世界：Spring (应用) vs Tomcat (Servlet 容器)。

### 必须用 Uvicorn 吗？

**不必须，但必须用某个 ASGI 服务器**。可替换选项：

| 服务器 | 特点 |
|---|---|
| **Uvicorn** | 最主流，基于 uvloop + httptools，社区最大 |
| **Hypercorn** | 支持 HTTP/2、HTTP/3 |
| **Daphne** | Django Channels 出品，WebSocket 场景常用 |
| **Granian** | Rust 写的 ASGI 服务器，目前最快 |

切换只改启动命令，代码一行不动：
```bash
uvicorn main:app --reload
hypercorn main:app --reload
granian --interface asgi main:app
```

### 为什么不像 Flask 那样 `python app.py`？

Flask 是 **WSGI（同步）** 框架，自带开发服务器；FastAPI 是 **ASGI（异步）** 框架，依赖 event loop —— 必须由 ASGI 服务器来跑。两种等价写法：

```bash
# 命令行
uvicorn main:app --reload

# 脚本里调（uvicorn.run 内部就是启动一个 Uvicorn）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

**`--reload` 只用于开发**（监听文件变化自动重启），生产严禁加 —— 拖慢性能 + 占内存。

### Gunicorn 又是什么？

`gunicorn -k uvicorn.workers.UvicornWorker` 这种写法里：

```
Gunicorn (进程管理 master/worker)  →  Uvicorn worker (ASGI 协议)  →  FastAPI
```

Gunicorn 是**进程管理器**（自己只会 WSGI）。但现代 Uvicorn 已内置 `--workers N`，单独 `uvicorn --workers 4 main:app` 就够，Gunicorn 这层在新项目越来越少见。

### 一句话收尾

> **FastAPI 是"怎么处理请求"的代码，Uvicorn 是"怎么收发请求"的进程。** ASGI 协议让两边都能独立演进 + 自由替换 —— 这是 Python Web 栈与 Node.js (`express` 自带 listen) 的关键差异之一。

---

## Swagger UI vs ReDoc —— 同源不同心

### 共同点

两者**消费同一份 OpenAPI JSON**（FastAPI 在 `/openapi.json` 暴露），只是渲染方式不同。内容完全一致，区别只在 UI 风格 + 使用场景。FastAPI 默认两套都给：

- `/docs` → Swagger UI
- `/redoc` → ReDoc

### 核心差异

| 维度 | Swagger UI | ReDoc |
|---|---|---|
| 定位 | 交互式调试 | 阅读式文档 |
| "Try it out" 发请求 | ✅ | ❌ 只读 |
| 布局 | 单列手风琴，紧凑 | 三栏布局，留白多 |
| Auth 面板（Bearer/API Key） | ✅ 右上角 Authorize | ❌ |
| 典型用户 | 后端开发、测试 | 外部开发者、合作伙伴 |

**怎么选**：开发期用 Swagger UI（能直接调接口，省 Postman）；对外开放 API 用 ReDoc（Stripe、Twilio 的公开文档就是 ReDoc 风格）。ch07 测 JWT 时点 Swagger UI 的 Authorize 按钮塞 Bearer token 最方便。

### 为什么叫 "Swagger"？

1. **2010 年** Tony Tam 在 Wordnik 创建了名为 **Swagger** 的工具（英文意为"昂首阔步"）。
2. **2015 年** SmartBear 收购 Swagger，把**规范本身捐给 Linux Foundation**，成立 OpenAPI Initiative。规范改名 **OpenAPI Specification (OAS)**，但工具名（Swagger UI/Editor/Codegen）保留 Swagger 品牌。
3. **2017 年起** OpenAPI 3.0/3.1 成为当今标准。

### 一句话辨析

> **OpenAPI 是规范（spec），Swagger 是 SmartBear 公司持有的工具品牌。**
> 你写的是 OpenAPI JSON，看的是 Swagger UI。口语混用没问题，严谨场合要区分。

**ReDoc** 是 Redocly 公司开源的另一个渲染器，跟 Swagger 没有品牌关系，**只是恰好读同一份 OpenAPI JSON** —— 这就是开放协议的好处：一份 schema，多家渲染。

---

## Python 泛型 —— `Generic[T]` 与中括号语法

### 完整三件套

```python
from typing import Generic, Optional, TypeVar

T = TypeVar("T")                                # ① 声明类型占位符
class StandardResponse(BaseModel, Generic[T]):  # ② 把 T 绑给这个类
    data: Optional[T] = None                    # ③ 字段中用 T

StandardResponse[float]                          # ④ 把 T 替换成 float
```

### 中括号是什么？—— `__class_getitem__`

`MyClass[X]` 本质是 `MyClass.__class_getitem__(X)`，**不是数组下标**，是"类型参数化"语法糖。`Generic` 基类提供了这套机制。同样的语法早就见过：

```python
list[int]         # → list.__class_getitem__(int)
dict[str, int]    # → dict.__class_getitem__((str, int))
Optional[float]   # → Optional.__class_getitem__(float)
```

内置类型自带这套，**自己写**泛型类时必须显式继承 `Generic[T]` 来接入。

### `TypeVar` 是什么

类型版的"函数参数"：

| 函数世界 | 类型世界 |
|---|---|
| `def f(x):` 中的 `x` 是参数 | `Generic[T]` 中的 `T` 是**类型参数** |
| 调用 `f(10)` 传入实参 | 实例化 `C[int]` 传入**类型实参** |

`T = TypeVar("T")` 创建占位符对象（变量名必须跟字符串名同名，社区约定）。可加约束：
- `TypeVar("U", bound=BaseModel)` —— 只能是 BaseModel 子类
- `TypeVar("V", int, float)` —— 只能是 int 或 float

### FastAPI 里的替换时机

```python
@app.post("/x", response_model=StandardResponse[float])
```

FastAPI 看到 `StandardResponse[float]` 会**在内部生成一个 T=float 的新模型**，等价于：

```python
class StandardResponse_float(BaseModel):
    data: Optional[float] = None
```

OpenAPI 文档里 `data` 字段类型就是明确的 `number` 而不是模糊的 `any`。

### Python 3.12+ 新写法（PEP 695）

本项目 Python 3.12，可以用更简洁的写法（不用 TypeVar，不用继承 Generic）：

```python
# 旧写法
T = TypeVar("T")
class StandardResponse(BaseModel, Generic[T]):
    data: Optional[T] = None

# 新写法 (3.12+)
class StandardResponse[T](BaseModel):
    data: Optional[T] = None
```

教学代码保留旧写法是为了兼容 3.10/3.11 用户。自己新代码直接用 PEP 695。

### 一句话本质

> **`Generic[T]` 是把"类型参数化"接入 Python 类型系统的钩子**：`T` 是占位符，`Generic[T]` 是绑定，`MyClass[X]` 用 `__class_getitem__` 把 X 代入占位符。中括号在类型语法里**专门表示"参数化"**，跟数组无关。

---

## SQLModel `Field()` 常用参数全梳理

参考 `ch05-orm/orm/models.py` 的 Book 模型。

### Field 的"双重身份"

```python
from sqlmodel import Field
```

SQLModel 的 `Field` 同时承担两类职责（**这是它跟纯 Pydantic Field、纯 SQLAlchemy Column 的关键区别**）：

```
   Pydantic Field（校验 + schema）  +  SQLAlchemy Column（数据库列）  =  SQLModel Field
```

一个声明既描述了"这个字段长什么样"，也描述了"建表时这一列怎么建"。

### 五类参数

#### 1. 默认值与可选性

| 参数 | 用途 | 示例 |
|---|---|---|
| `default` | 静态默认值 | `default=None`, `default=0` |
| `default_factory` | 工厂函数（每次实例化都调用）| `default_factory=datetime.now` |

注意：可变默认值（list/dict）**必须用 factory**，不能写 `default=[]`，否则所有实例共享同一个列表。

#### 2. 数据库列层面（SQLModel 专属，纯 Pydantic 没有）

| 参数 | 用途 | Book 模型示例 |
|---|---|---|
| `primary_key=True` | 主键 | `id` 字段 |
| `index=True` | 给该列建索引，加速查询 | `title` 字段 |
| `unique=True` | 唯一约束 | 如 `email` 字段常用 |
| `nullable=False` | 数据库层非空（与 `Optional` 配合）| `title` 字段 |
| `foreign_key="user.id"` | 外键，关联另一张表的主键 | `owner_id` 引用 user |
| `sa_column=Column(...)` | 直接传一个 SQLAlchemy Column 做高级控制（如自定义类型、server_default）| 需要数据库级 trigger 时 |
| `sa_column_kwargs={...}` | 给底层 Column 传额外参数 | `{"server_default": "now()"}` |

记忆口诀：**`primary_key` / `index` / `unique` / `nullable` / `foreign_key` 五个是数据库专属**，纯 Pydantic 模型用不到。

#### 3. 校验约束（来自 Pydantic）

| 类别 | 参数 | 含义 |
|---|---|---|
| 数值 | `gt` / `ge` / `lt` / `le` | 大于 / 大于等于 / 小于 / 小于等于 |
| 数值 | `multiple_of` | 必须是某数的倍数 |
| 数值 | `max_digits` / `decimal_places` | 总位数 / 小数位数（Decimal）|
| 字符串 | `min_length` / `max_length` | 长度范围 |
| 字符串 | `pattern` | 正则约束（如 `r"^\d{4}-\d{2}-\d{2}$"`）|

Book 模型里 `price = Field(gt=0)` 就是约束价格必须 > 0，请求传 `-1` 会被 Pydantic 直接 422 拒绝。

#### 4. 文档与 OpenAPI Schema

| 参数 | 用途 |
|---|---|
| `description` | 字段说明，进 `/docs` 文档（Book 每个字段都用了）|
| `title` | 字段标题（默认是字段名）|
| `examples=[...]` | 示例值，文档里渲染成 "Try it out" 默认值 |
| `alias="xxx"` | 输入/输出时换名（如 API 用驼峰、Python 用下划线）|
| `deprecated=True` | 标记弃用，文档里会划掉 |

#### 5. 行为控制（较少用，知道即可）

| 参数 | 用途 |
|---|---|
| `exclude=True` | 序列化（`.dict()` / JSON）时排除该字段 |
| `repr=False` | `print(obj)` 时不显示该字段 |
| `frozen=True` | 字段不可修改（赋值会报错）|
| `validate_default=True` | 连默认值也走校验 |

### Book 模型逐字段解读

```python
class Book(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,        # ← 新建时不用传，DB 自动生成
        primary_key=True,    # ← 数据库主键
        description="图书 ID",
    )

    title: str = Field(
        index=True,          # ← 加索引 (title 经常用来查询)
        nullable=False,      # ← 数据库非空
        description="图书标题",
    )

    author: str = Field(description="作者名称")    # 只加文档说明

    price: float = Field(
        gt=0,                # ← Pydantic 校验：价格必须 > 0
        description="图书价格",
    )

    description: Optional[str] = Field(
        default=None,        # ← 可选字段
        description="图书描述",
    )
```

一行声明同时定义了：**Python 类型 + Pydantic 校验 + 数据库列 + OpenAPI 文档**。

### Pydantic Field vs SQLModel Field 速辨

```python
# 纯 Pydantic（用于 ch03/ch04 的请求体/响应体）
from pydantic import Field
class CalcRequest(BaseModel):
    a: float = Field(gt=0, description="第一个数")

# SQLModel（用于 ch05 数据库表）
from sqlmodel import Field
class Book(SQLModel, table=True):
    id: int = Field(primary_key=True)
```

**导入路径不同，参数取并集，使用时根据场景选**。如果一个模型既要校验请求又要持久化（不常见，反模式），通常拆成两个：`BookCreate(BaseModel)` 收请求 + `Book(SQLModel, table=True)` 存数据库。

### 一句话本质

> **`Field()` 是字段元信息的统一入口**：默认值、约束、列属性、文档说明全塞进一个调用里。SQLModel 的 Field 把 Pydantic 校验和 SQLAlchemy 列属性合二为一，**一份声明同时服务校验、文档、建表三件事**。

---

## APIRouter 模块化路由 vs `app.xxx` 直挂

### 一句话本质

`app.xxx` 是把所有路由**直接挂在主应用上**（扁平 / 全揉一锅）；`APIRouter` 是**先在子路由对象上挂，再 `include_router` 到主应用**（可组合 / 分包再合并）。功能等价，**形态完全不同**。

### 大项目必用 APIRouter 的 8 个理由

**1. 业务领域强物理隔离（最重要）**
每个领域一个目录 + 一个 router (`routers/books.py`, `routers/users.py`, ...)。改一个模块不会影响另一个，CR diff 干净，main.py 永远只有 30 行做组装。`app.xxx` 直挂会把所有路由堆在 main.py，几千行起步谁也不敢动。

**2. 横切配置一次到位**
```python
APIRouter(prefix="/books", tags=["书籍"], dependencies=[Depends(verify_token)])
```
prefix / tags / dependencies / responses 四个参数对该 router 下所有路由生效。**新加的接口自动继承**，杜绝"新接口忘了加鉴权"事故。

**3. 同一 router 多处挂载**
```python
app.include_router(books_router, prefix="/v1")
app.include_router(books_router, prefix="/v2")              # 灰度对比
app.include_router(books_router, prefix="/admin", dependencies=[Depends(require_admin)])
```
装配时延迟决策；`app.xxx` 直挂焊死在 app 上做不到。

**4. 跟分层架构天然贴合**
```
routers/books.py  ←→  services/book_crud.py  ←→  orm/
```
**router 跟 service 一一对应**，对应 `ch06/layered_arch/` 那套写法。

**5. 团队并行开发零冲突**
5 人 owner 5 个 routers/xxx.py 文件，git 冲突概率几乎为零；都改 main.py 则天天合并冲突。

**6. 子应用独立测试**
```python
mini_app = FastAPI()
mini_app.include_router(books_router)
client = TestClient(mini_app)  # 只起 books，不拉起整个 monolith
```

**7. 微服务拆分零成本**
单体 → 微服务拆分时，把整个 `routers/books.py` 文件 `git mv` 到新服务即可。router 本身就是"可拔插的业务单元"。

**8. 路由元信息 → 文档 + SDK 分组**
`tags=["书籍管理"]` 让 Swagger UI 按领域分组；codegen 出来的 TS 客户端自动有 `client.BookManagement.xxx` 命名空间，前端用着舒服。

### 什么时候不用 APIRouter

| 场景 | 选 |
|---|---|
| 单文件 demo / 教学示例 / PoC | `app.xxx` |
| 一次性脚本式后端 | `app.xxx` |
| **接口 > 10 个 / 文件 > 200 行 / 团队 ≥ 2 人** | **APIRouter 起步** |

### 一句话收尾

> **`app.xxx` 把所有路由长在一棵主树上；`APIRouter` 是每个业务领域一棵子树，最后嫁接到主树。** 大项目用前者会让 main.py 变成"上帝文件"；用后者能让横切关注点（auth/prefix/tags/docs）一次配置批量生效，并把代码结构 × 业务领域 × 分层架构 × 团队组织四者对齐 —— 这就是企业级项目的工程价值所在。
