"""8.4 单文件上传 — UploadFile vs File(bytes)

两种声明方式，差异在"小文件 vs 大文件":

  1. file: bytes = File(...)         → 把整个文件一次读进内存 (适合小文件 < 1MB)
  2. file: UploadFile = File(...)    → 流式 IO，spool 到临时文件 (大文件首选)

UploadFile 提供了 file-like API:
  - file.filename            原始文件名
  - file.content_type        MIME 类型 (image/png 等)
  - await file.read([size])  读 bytes (异步)
  - await file.seek(0)       回到文件头
  - await file.close()       关闭 (FastAPI 会在请求结束自动关)
  - file.file                底层 SpooledTemporaryFile，可同步用

⚠️ Content-Type 必须是 multipart/form-data，不是 application/json！

运行: uv run uvicorn 04_file_upload_single:app --reload

测试:
    # 用 curl -F 自动设置 multipart Content-Type
    curl -F "file=@README.md" http://127.0.0.1:8000/upload
    curl -F "file=@some_image.png" http://127.0.0.1:8000/upload-image
"""

import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="File Upload Demo")

# 上传目录 (放在 02-fastapi/data/uploads/，已 .gitignore)
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── 方式 1: bytes — 简单但占内存 ─────────────────────────────────
@app.post("/upload-bytes")
async def upload_bytes(file: bytes = File(...)):
    """把整个文件读成 bytes — 只适合小文件 (< 1MB)。
    没有 filename / content_type 信息，只能拿到原始字节。
    """
    return {"size_bytes": len(file)}


# ── 方式 2: UploadFile — 推荐 ────────────────────────────────────
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """流式上传，落盘到 data/uploads/，返回元信息"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="缺少文件名")

    dest = UPLOAD_DIR / file.filename
    # shutil.copyfileobj 流式复制 — 不会把整个文件读进内存
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": dest.stat().st_size,
        "saved_to": str(dest.relative_to(UPLOAD_DIR.parent.parent)),
    }


# ── 带类型限制的图片上传 ──────────────────────────────────────────
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """图片专用上传 — 校验 MIME 类型 + 大小限制"""
    # 1. MIME 校验 (浏览器/客户端传的，可信度有限，仅作粗筛)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"不支持的类型 {file.content_type}; 仅允许 {ALLOWED_IMAGE_TYPES}",
        )

    # 2. 大小校验 (流式读取时累加，不超就继续；超了立即停)
    contents = await file.read()  # 一次性读 — 仅在已校验 content-type 后做
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail=f"文件超过 {MAX_IMAGE_SIZE} 字节")

    # 3. 落盘
    dest = UPLOAD_DIR / f"img_{file.filename}"
    dest.write_bytes(contents)

    return {
        "filename": file.filename,
        "size_bytes": len(contents),
        "url": f"/static/uploads/{dest.name}",  # 生产里配合 StaticFiles 服务
    }
