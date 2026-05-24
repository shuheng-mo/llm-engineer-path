"""8.5 多文件上传 + Form 字段混合 (multipart 综合场景)

最常见的真实场景：用户提交一个表单，里面同时有：
  - 文本字段：title, description
  - 文件：cover image
  - 多个附件：attachments[] (可选)

这种"表单 + 文件"组合必须用 multipart/form-data，
**不能用 application/json** (JSON 无法装二进制文件)。

声明方式：
  - 文本字段用 `Form(...)`           ← 注意不是 `Body`，因为整个请求是 multipart
  - 单文件用 `UploadFile = File(...)`
  - 多文件用 `list[UploadFile] = File(...)`

运行: uv run uvicorn 05_file_upload_multi_form:app --reload

测试:
    # 多个文件 + 表单字段 (-F 可以重复)
    curl -X POST http://127.0.0.1:8000/articles \\
      -F "title=My First Article" \\
      -F "description=Hello world" \\
      -F "cover=@README.md" \\
      -F "attachments=@README.md" \\
      -F "attachments=@.gitignore"
"""

import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

app = FastAPI(title="Multi-File + Form Demo")

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _save(file: UploadFile, sub: str = "") -> dict:
    """通用落盘 helper，返回元信息字典"""
    dest_dir = UPLOAD_DIR / sub if sub else UPLOAD_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (file.filename or "unnamed")
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": dest.stat().st_size,
    }


# ── 场景: 创建一篇文章 (含封面 + 多附件) ─────────────────────────
@app.post("/articles")
async def create_article(
    # ↓ 文本字段用 Form，不是 Body
    title: str = Form(..., min_length=1, max_length=200),
    description: str = Form(..., max_length=2000),
    # ↓ 单个文件 (必传)
    cover: UploadFile = File(..., description="封面图"),
    # ↓ 多个文件 (可选，可为空列表)
    attachments: Optional[List[UploadFile]] = File(default=None),
):
    """模拟"发布一篇文章"的接口 —— Form 字段 + 单图 + 多附件混合。

    注意：Pydantic 校验也作用在 Form 字段上 (min_length / max_length 都生效)。
    """
    if not cover.filename:
        raise HTTPException(status_code=400, detail="封面缺少文件名")

    saved_cover = _save(cover, sub="covers")
    saved_attachments = [_save(f, sub="attachments") for f in (attachments or [])]

    return {
        "article": {"title": title, "description": description},
        "cover": saved_cover,
        "attachments": saved_attachments,
        "attachment_count": len(saved_attachments),
    }


# ── 纯多文件上传 (无表单字段) ────────────────────────────────────
@app.post("/upload-many")
async def upload_many(files: List[UploadFile] = File(...)):
    """批量上传 N 个文件，落盘并返回每个的元信息"""
    return {"files": [_save(f, sub="batch") for f in files], "count": len(files)}
