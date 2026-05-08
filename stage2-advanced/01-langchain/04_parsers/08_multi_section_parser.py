"""多段输出解析 — 把 markdown 多章节拆成 Section 列表

对应课程章节：第五章 / 4.2
"""
import re
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Section(BaseModel):
    title: str = Field(description="章节标题")
    content: str = Field(description="章节内容")
    key_points: List[str] = Field(description="关键要点")


class MultiSectionParser:
    def __init__(self):
        self.section_parser = PydanticOutputParser(pydantic_object=Section)

    def parse(self, text: str) -> List[Section]:
        sections = []
        # 按章节分隔符（"---SECTION---" 或 "### " 开头）拆分
        parts = re.split(r"(?:---SECTION---|(?=### ))", text)

        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                import json
                data = json.loads(part)
                sections.append(Section(**data))
            except Exception:
                section = self._extract_section(part)
                if section:
                    sections.append(section)
        return sections

    def _extract_section(self, text: str) -> Section:
        lines = text.split("\n")
        title, content_lines, key_points = "", [], []

        for line in lines:
            line = line.strip()
            if line.startswith("### ") or line.startswith("# "):
                title = line.lstrip("#").strip()
            elif line.startswith("- ") or line.startswith("* "):
                key_points.append(line[2:])
            elif line:
                content_lines.append(line)

        return Section(
            title=title or "未命名章节",
            content=" ".join(content_lines),
            key_points=key_points,
        )


if __name__ == "__main__":
    parser = MultiSectionParser()
    text = """
### 第一章 简介
这是简介的内容。
- 要点 1
- 要点 2

### 第二章 核心概念
这是核心概念的内容。
- 概念 A
- 概念 B
- 概念 C
"""
    for i, s in enumerate(parser.parse(text), 1):
        print(f"\n=== 章节 {i} ===")
        print(f"标题: {s.title}")
        print(f"内容: {s.content[:50]}...")
        print(f"要点: {s.key_points}")
