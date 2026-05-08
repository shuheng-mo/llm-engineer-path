"""图片型 / 扫描件 PDF 加载 — PyMuPDF 渲染 + RapidOCR 识别

对应课程章节：一 / 2.2.1 扩展（针对没有文字层的 PDF）

依赖:
    uv add --group rag rapidocr-onnxruntime
    PyMuPDF 已在 rag group 里（pymupdf>=1.27）

适用场景：
    - PyPDFLoader / PyMuPDFLoader 抽出来的 text 是空的
    - 在预览里选不中文字、说明 PDF 里只有图片
    - 中文扫描件、报告类 PDF（很多研究报告字体嵌入有问题，不 OCR 抽不出来）

性能：
    - dpi=200，每页 ~0.5-1s（够用）
    - dpi=300，每页 ~1-2s（推荐）
    - dpi=400，每页 ~2-4s（小字/表格）
"""
import logging
from pathlib import Path

import fitz  # PyMuPDF
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from rapidocr_onnxruntime import RapidOCR

logging.getLogger("pypdf").setLevel(logging.ERROR)


# ============================================================
# Part 1: 函数式 — 直接对 PDF 文件做 OCR
# ============================================================

def ocr_pdf_to_text(pdf_path: str | Path, dpi: int = 300) -> list[Document]:
    """把扫描型 PDF 转成 Document 列表。

    每页渲染成 PNG 图片 → 喂给 RapidOCR → 拼接每行文本。
    """
    ocr = RapidOCR()  # 首次调用会下载 ~50MB 模型到 ~/.cache/
    docs: list[Document] = []

    with fitz.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")

            # RapidOCR 返回：([(box, text, confidence), ...], elapse_dict)
            result, _ = ocr(img_bytes)
            page_text = "\n".join(line[1] for line in (result or []))

            docs.append(Document(
                page_content=page_text,
                metadata={"source": str(pdf_path), "page": i},
            ))
            print(f"  页 {i + 1}: 识别 {len(page_text)} 字")

    return docs


# ============================================================
# Part 2: 类封装 — 跟其他 LangChain Loader 用法一致
# ============================================================

class OCRPDFLoader(BaseLoader):
    """LangChain 风格的 OCR PDF Loader，用法和 PyPDFLoader 一致。

    Example:
        loader = OCRPDFLoader("scanned.pdf", dpi=300)
        pages = loader.load()
    """

    def __init__(self, path: str | Path, dpi: int = 300):
        self.path = Path(path)
        self.dpi = dpi
        self._ocr = RapidOCR()

    def load(self) -> list[Document]:
        return list(self.lazy_load())

    def lazy_load(self):
        with fitz.open(str(self.path)) as pdf:
            for i, page in enumerate(pdf):
                pix = page.get_pixmap(dpi=self.dpi)
                result, _ = self._ocr(pix.tobytes("png"))
                text = "\n".join(line[1] for line in (result or []))
                yield Document(
                    page_content=text,
                    metadata={"source": str(self.path), "page": i},
                )


# ============================================================
# 测试入口
# ============================================================

if __name__ == "__main__":
    PDF_PATH = Path(__file__).resolve().parents[2] / "data" / "aie-market-analysis.pdf"
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF 不存在: {PDF_PATH}")

    print(f"=== 函数式 ===\n加载: {PDF_PATH}\n")
    docs = ocr_pdf_to_text(PDF_PATH, dpi=300)

    total_chars = sum(len(d.page_content) for d in docs)
    print(f"\n共 {len(docs)} 页，总字符数: {total_chars}\n")

    if docs:
        print("=== 第一页前 300 字预览 ===")
        print(docs[0].page_content[:300])

    print("\n=== 类式（OCRPDFLoader） ===")
    loader = OCRPDFLoader(PDF_PATH, dpi=300)
    pages = loader.load()
    print(f"loader.load() 返回 {len(pages)} 页")
