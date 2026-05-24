# 图书管理系统后端 (ch06 综合实践)

ch06 三个关键原则的综合落地：

1. **Depends(get_session)** —— 每个路由函数都通过依赖注入获取 Session，绝不全局持有
2. **yield 生成器** —— `get_session` 用 yield 保证请求结束后 Session 必定被关闭
3. **lifespan** —— 替代已废弃的 `@app.on_event("startup")`，启动时自动建表

## 项目结构

```
library-magmt-system/
├── main.py                  # 主应用入口 (lifespan + include_router)
├── orm/
│   ├── __init__.py          # 包标识 + 对外导出
│   ├── models.py            # Book 数据模型
│   └── database.py          # engine / async_session / init_db / get_session
├── routers/
│   ├── __init__.py
│   └── books.py             # APIRouter: POST/GET/PUT/DELETE 接口
├── services/
│   ├── __init__.py
│   └── book_crud.py         # 纯业务逻辑 (不依赖 HTTP)
└── data/
    └── books.db             # SQLite 文件 (运行时自动创建，已 .gitignore)
```

## 运行

```bash
cd stage1-foundations/02-fastapi/ch06-dependency-injection/library-magmt-system
uv run uvicorn main:app --reload
```

文档：
- Swagger UI → <http://127.0.0.1:8000/docs>
- ReDoc → <http://127.0.0.1:8000/redoc>

## 接口清单

| 方法 | 路径 | 用途 |
|---|---|---|
| POST | `/books/` | 录入新书 (201) |
| GET | `/books/` | 列表（支持 `?title=` 模糊搜索、`?skip=&limit=` 分页）|
| GET | `/books/{id}` | 查询单本 (找不到 404) |
| PUT | `/books/{id}` | 更新 (找不到 404) |
| DELETE | `/books/{id}` | 删除 (找不到 404) |

## curl 速测

```bash
# 录入
curl -X POST http://127.0.0.1:8000/books/ -H "Content-Type: application/json" \
  -d '{"title":"Effective Python","author":"Brett Slatkin","price":59,"publish_date":"2019-11-08"}'

# 模糊搜索
curl "http://127.0.0.1:8000/books/?title=Python"

# 分页
curl "http://127.0.0.1:8000/books/?skip=0&limit=2"

# 详情
curl http://127.0.0.1:8000/books/1

# 更新
curl -X PUT http://127.0.0.1:8000/books/1 -H "Content-Type: application/json" \
  -d '{"title":"Effective Python (2nd)","author":"Brett Slatkin","price":69}'

# 删除
curl -X DELETE http://127.0.0.1:8000/books/1
```

## 已知 SQLModel quirk

`Book(SQLModel, table=True)` 实例化时**会跳过 Pydantic 校验**（`gt`/`lt`/`max_length` 等约束在 `/docs` 文档里展示但运行时不强制）。这是 SQLAlchemy 的设计妥协 —— 需要能从 row 直接重建对象，不能强制走 Pydantic。

例如 `price=0` 违反 `gt=0`，但 POST 会成功返回 201（已实测过）。

**生产代码的正解** —— 拆两个模型：

```python
class BookCreate(SQLModel):              # 不带 table=True
    title: str
    price: float = Field(gt=0)           # ← 这里的 gt 会强制

class Book(SQLModel, table=True):        # 数据库表模型
    ...

# 路由签名换成 BookCreate
@router.post("/")
async def create(payload: BookCreate, session: AsyncSession = Depends(get_session)):
    book = Book(**payload.model_dump())  # 转成数据库模型
    return await book_crud.create_book(session, book)
```

本项目按教学文档保留单一 Book 模型，故意不修正这个 quirk。如需自己练手可以试着拆出 BookCreate。

## 与 ch06/layered_arch 的区别

| 项 | layered_arch | library-magmt-system |
|---|---|---|
| 路由数量 | 4 (CRUD) | 5 (CRUD + 列表 with 分页/模糊搜索) |
| 数据模型 | 复用 ch05-orm 的 Book | 自带独立 orm 包 |
| 分页参数 | 无 | 通过 `Depends(pagination_params)` 抽成依赖 |
| lifespan | ✓ | ✓ |
| 自包含 | 否（需 sys.path 注入）| 是 (无任何跨章节依赖) |

`layered_arch` 是分层架构最小示例，`library-magmt-system` 是综合应用 —— 加入了分页/搜索/lifespan/Pydantic 校验 quirk 等真实工程细节。
