# 02 — FastAPI 从入门到实战

源文档：`FastAPI 从入门到实战课程代码.docx`
所有代码已按章节拆分到对应子目录，可直接 `uv run` 跑。

## 章节结构

| 章节 | 主题 | 关键文件 |
|---|---|---|
| `ch01-python-basics/` | 类型提示 · Pydantic · 异步基础 | 5 个独立 demo |
| `ch02-hello-fastapi/` | Hello World · 启动调试 | `01_hello_world.py`, `02_practice.py` |
| `ch03-params-validation/` | 路径参数 · 查询参数 · Pydantic 请求体 · 进阶校验 · 计算器 API | `05_calculator_api.py` 为本章实战 |
| `ch04-response-errors/` | response_model · HTTPException · 全局异常处理 · 计算器 v2 | `04_calculator_v2.py` 引入泛型响应 |
| `ch05-orm/` | SQLModel + 异步 SQLAlchemy + CRUD 测试 | `orm/`, `crud.py`, `test_crud.py` |
| `ch06-dependency-injection/` | Depends · yield 生命周期 · APIRouter · 分层架构 | 4 个子项目 (`apirouter_full/`, `apirouter_advanced/`, `layered_arch/`, `library-magmt-system/` 综合实践) + 单文件示例 |
| `ch07-auth-security/` | bcrypt · JWT · OAuth2 · 私密笔记本完整项目 | `jwt_app/` 是登录 demo，`notebook_app/` 是综合实战 |
| `ch08-advanced/` | 中间件 · 后台任务 · 文件上传 | 5 个独立示例 (`01_middleware.py` ~ `05_file_upload_multi_form.py`) |

## 运行约定

所有 FastAPI 单文件示例都用以下模式启动：

```bash
cd stage1-foundations/02-fastapi/<章节>/
uv run uvicorn <文件名去掉.py>:app --reload
# 文档: http://127.0.0.1:8000/docs
```

例：

```bash
# Hello World
cd stage1-foundations/02-fastapi/ch02-hello-fastapi/
uv run uvicorn 01_hello_world:app --reload

# 计算器 v2
cd stage1-foundations/02-fastapi/ch04-response-errors/
uv run uvicorn 04_calculator_v2:app --reload

# 私密笔记本完整项目 (ch07 实战)
cd stage1-foundations/02-fastapi/ch07-auth-security/notebook_app/
uv run uvicorn main:app --reload
```

含 `if __name__ == "__main__"` 的脚本也可以直接 `uv run python xxx.py` 跑。

## ch05 / ch06 数据库示例

数据库文件统一放在 `02-fastapi/data/books.db`（`ch05-orm/orm/database.py` 内用 `Path(__file__)` 算成绝对路径），ch05 单元测试与 ch06 路由共享同一份。`data/` 已在 `.gitignore`。

### ch05 CRUD 单元测试

```bash
cd stage1-foundations/02-fastapi/ch05-orm/
uv run pytest test_crud.py -v -s
```

### ch06 路由 + Depends(get_session) 注入

```bash
cd stage1-foundations/02-fastapi/ch06-dependency-injection/
uv run uvicorn 07_use_session_in_route:app --reload
# 文档: http://127.0.0.1:8000/docs
```

`07_use_session_in_route.py` 顶部用 `sys.path.insert` 把 `ch05-orm/` 加进模块搜索路径，所以可以直接 `from orm.models import Book`，**不需要设 `PYTHONPATH` 也不需要 cd 到别处**。Pylance 在 IDE 里会对这两个 import 划红线（静态分析看不到 sys.path 操作），运行时无影响。

测试 POST 一本书：

```bash
curl -X POST http://127.0.0.1:8000/books/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Effective Python","author":"Brett Slatkin","price":59.0,"description":"59 specific ways"}'

# 看一下落库结果
sqlite3 stage1-foundations/02-fastapi/data/books.db "SELECT id,title,price FROM book;"
```

## 依赖

本目录用到的依赖都已加入仓库根的 `pyproject.toml` 中 `[dependency-groups.fastapi]`：

- `fastapi` / `uvicorn[standard]` / `python-multipart`
- `sqlmodel` / `aiosqlite` / `greenlet` (ch05, ch06)
- `python-jose[cryptography]` / `bcrypt` (ch07)
- `pytest-asyncio` 在 `dev` 组中

默认 `uv sync` 已包含 `fastapi` 组。如需补装：

```bash
uv sync --group fastapi
```

## 章节间依赖

- `ch06/07_use_session_in_route.py` 引用 `ch05-orm/orm/` 下的 `models.py` 和 `database.py`（教学连续性）。文件顶部用 `sys.path.insert(0, ".../ch05-orm")` 自动接入，无需手动设环境变量。
- `ch06/06_session_dep_pattern.py` 只是教学片段，展示如何把 `get_session()` 追加到 `database.py`（实际已经在了）。
- `ch07/jwt_app/main.py` 引用 `ch07/jwt_app/utils/security.py`，自成一体。
- 其他每个文件/子项目都自包含，可独立运行。

## 与原 docx 的偏差

| 偏差 | 说明 |
|---|---|
| ch04 `04_calculator_v2.py` 补全了 imports/Pydantic 模型 | 原 docx 表 17 是片段，不能直接运行；用 ch03 的 `Operation`/`CalcRequest` 补全 |
| ch05 `crud.py` 补充了 `get_book_by_id` | 原 docx 测试代码引用了这个函数但未给出实现 |
| ch05 `crud.py` `get_books()` 用 `result.scalars().all()` | 原 docx 是 `result.all()`，SQLAlchemy 2.x 返回 Row 而非 Book，需要 `.scalars()` 解包 |
| ch02 `02_practice.py` 去掉了 `+ res` (未定义变量) 和多余缩进 | 原 docx 表 8 有源代码 bug |
| ch04 `01_response_model.py` 修正装饰器缩进 | 原 docx 表 14 中 `@app.post` 错位在类体内 |
| 删掉了与 `apirouter_full/` 内容重复的 `apirouter_intro/` 目录 | 原 docx 2.4.2 "三步骤"与 2.4.3 "完整示例" 是同一份代码的两次呈现，去重后只保留完整版 |
