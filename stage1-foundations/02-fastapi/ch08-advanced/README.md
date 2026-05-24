# ch08 — FastAPI 高级特性

三大主题：**中间件 (Middleware)** · **后台任务 (BackgroundTasks)** · **文件上传 (UploadFile)**。
每个文件独立可跑，从其本目录直接 `uv run uvicorn xx:app --reload` 启动。

## 文件清单

| 文件 | 主题 | 关键点 |
|---|---|---|
| `01_middleware.py` | 自定义中间件 | `@app.middleware("http")` 装饰器 · request.state · 中间件 LIFO 洋葱模型 · 请求计时 + Request-ID |
| `02_cors_gzip.py` | 内置中间件 | `CORSMiddleware` (跨域) + `GZipMiddleware` (响应压缩) |
| `03_background_tasks.py` | 后台任务 | `BackgroundTasks.add_task` · 先返回响应再执行副作用 · 何时该上 Celery |
| `04_file_upload_single.py` | 单文件上传 | `bytes` vs `UploadFile` · MIME/大小校验 · 流式落盘 |
| `05_file_upload_multi_form.py` | 多文件 + Form 综合 | multipart/form-data · `Form()` + `File()` 混用 · 多附件 |

## 运行约定

```bash
cd stage1-foundations/02-fastapi/ch08-advanced/
uv run uvicorn 01_middleware:app --reload      # 然后 / docs / hello / slow
uv run uvicorn 02_cors_gzip:app --reload       # /data /big
uv run uvicorn 03_background_tasks:app --reload  # POST /register /action/{name}
uv run uvicorn 04_file_upload_single:app --reload  # POST /upload /upload-image
uv run uvicorn 05_file_upload_multi_form:app --reload  # POST /articles /upload-many
```

文档 (每个示例都有)：

- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## 速测命令

```bash
# 中间件：观察 X-Process-Time / X-Request-ID 头
curl -i http://127.0.0.1:8000/hello

# CORS preflight 模拟
curl -i -X OPTIONS http://127.0.0.1:8000/data \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET"

# GZip 压缩 (注意响应头里的 Content-Encoding)
curl -i --compressed http://127.0.0.1:8000/big -H "Accept-Encoding: gzip"

# 后台任务 — 立即返回，但服务器日志会延迟 2 秒看到邮件发送
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com"}'

# 单文件上传
curl -F "file=@README.md" http://127.0.0.1:8000/upload

# 多文件 + Form 字段
curl -X POST http://127.0.0.1:8000/articles \
  -F "title=Hello" \
  -F "description=My first article" \
  -F "cover=@README.md" \
  -F "attachments=@README.md" -F "attachments=@.gitignore"
```

## 文件上传落盘位置

所有上传的文件统一落到 `02-fastapi/data/uploads/` 下（已在 `.gitignore`），不会污染仓库。
子目录划分：
- `data/uploads/covers/`     封面图
- `data/uploads/attachments/` 附件
- `data/uploads/batch/`       批量上传

## 三个核心要点

### 中间件 — 洋葱模型 (LIFO)

```
请求方向 →    [外层 mw3]
            [中层 mw2]
            [内层 mw1]      ← 最后注册的最先包路由
            [route handler]
响应方向 ←    一层层往外返回，刚好倒序
```

注册顺序 → 执行顺序：**后注册的先进入请求，最后处理响应**。

### BackgroundTasks 适用边界

✅ 适合：邮件 / 审计日志 / webhook / 缓存预热（轻量、失败可丢、< 几秒）
❌ 不合适：长任务（> 30s）/ 必须重试 / 定时调度 / 跨服务消费 → 上 Celery/Arq/Dramatiq

### 文件上传必知

| 误区 | 正解 |
|---|---|
| 用 `application/json` 传文件 | **必须** `multipart/form-data` |
| 文件直接 `bytes` 收 | 大文件改用 `UploadFile` 流式 |
| 信任客户端传的 content_type | 双校验：MIME + magic bytes (生产用 python-magic) |
| 用户上传的文件名直接当存储路径 | **必须** sanitize（防 path traversal: `../../etc/passwd`） |

本章示例为教学简化，生产环境上传还需要：杀毒扫描 / OSS 替代本地盘 / CDN 分发 / 防盗链等。
