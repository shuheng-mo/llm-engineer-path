"""Adaptive-RAG（自适应 RAG） — 按问题复杂度路由 A/B/C 三种策略

对应课程章节：二 / 6.3
"""

import json
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()


class AdaptiveRAG:
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0,
        )
        self._init_prompts()

    def _init_prompts(self):
        self.classify_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """将用户问题分类为以下三类之一：

【A类：无需检索】
- 简单常识（"北京是哪国首都"）
- 数学计算（"123+456"）
- 创作任务（"写一首诗"）
- 格式转换（"翻译成英文"）
- 代码生成（"写一个排序函数"）

【B类：单次RAG】
- 事实查询（"公司年假政策"）
- 定义解释（"什么是RAG"）
- 单一主题的问题

【C类：多步RAG】
- 对比分析（"A和B哪个好"）
- 多主题综合（"总结X和Y的关系"）
- 需要推理的决策（"推荐一个适合我的..."）
- 涉及多个实体/时间段的问题

只返回分类结果，格式：{"type": "A/B/C", "reason": "简短原因"}""",
                ),
                ("human", "{question}"),
            ]
        )

        self.decompose_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """将复杂问题分解为 2-4 个可独立检索的子问题。

要求：
1. 每个子问题应该是具体的、可检索的
2. 子问题合起来能完整回答原问题
3. 返回 JSON 数组格式

示例：
原问题："对比 React 和 Vue，哪个适合电商项目？"
输出：["React 框架的特点和优势", "Vue 框架的特点和优势", "电商前端项目的技术需求"]""",
                ),
                ("human", "{question}"),
            ]
        )

        self.rag_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "根据参考文档回答问题。只使用文档中的信息。\n\n参考文档：\n{context}"),
                ("human", "{question}"),
            ]
        )

        self.synthesize_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """基于以下子问题的回答，综合回答用户的原始问题。

要求：
1. 整合各子问题的信息
2. 给出结构化的分析
3. 如果是决策类问题，给出明确建议

原始问题：{question}

各子问题回答：
{sub_answers}""",
                ),
                ("human", "请给出综合分析和最终答案。"),
            ]
        )

    def _classify(self, question: str) -> dict:
        response = (self.classify_prompt | self.llm).invoke({"question": question})
        try:
            return json.loads(response.content)
        except Exception:
            return {"type": "B", "reason": "默认单次RAG"}

    def _decompose(self, question: str) -> list:
        response = (self.decompose_prompt | self.llm).invoke({"question": question})
        try:
            return json.loads(response.content)
        except Exception:
            return [question]

    def _single_rag(self, question: str) -> str:
        docs = self.retriever.invoke(question)
        context = "\n\n".join(d.page_content for d in docs)
        return (
            (self.rag_prompt | self.llm).invoke({"question": question, "context": context}).content
        )

    def _multi_step_rag(self, question: str) -> str:
        sub_questions = self._decompose(question)
        print(f"   分解为 {len(sub_questions)} 个子问题:")
        for i, sq in enumerate(sub_questions, 1):
            print(f"      {i}. {sq}")

        sub_answers = [f"【{sq}】\n{self._single_rag(sq)}" for sq in sub_questions]
        return (
            (self.synthesize_prompt | self.llm)
            .invoke(
                {
                    "question": question,
                    "sub_answers": "\n\n".join(sub_answers),
                }
            )
            .content
        )

    def query(self, question: str) -> dict:
        classification = self._classify(question)
        query_type = classification.get("type", "B")
        print(f"\n📌 问题分类: {query_type}类 - {classification.get('reason', '')}")

        if query_type == "A":
            print("📌 策略: 直接LLM回答（无需检索）")
            answer = self.llm.invoke(question).content
        elif query_type == "B":
            print("📌 策略: 标准单次RAG")
            answer = self._single_rag(question)
        else:
            print("📌 策略: 多步RAG（问题分解 + 多次检索 + 综合）")
            answer = self._multi_step_rag(question)

        return {"question": question, "classification": classification, "answer": answer}

    def query_with_trace(self, question: str):
        print(f"\n{'=' * 60}")
        print(f"🔍 问题: {question}")
        print("=" * 60)
        result = self.query(question)
        print(f"\n💬 答案:\n{result['answer']}")
        return result


if __name__ == "__main__":
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    vectorstore = Chroma(
        persist_directory=str(DATA_DIR / "chroma_db"), embedding_function=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    adaptive_rag = AdaptiveRAG(retriever)

    test_questions = [
        "123 × 456 等于多少？",
        "帮我写一个 Python 快速排序函数",
        "什么是 RAG？",
        "公司的年假政策是什么？",
        "对比 LangChain 和 LlamaIndex，哪个更适合构建客服系统？",
        "总结 Python 和 JavaScript 的主要区别，并推荐一个适合后端开发的语言",
    ]
    for q in test_questions:
        adaptive_rag.query_with_trace(q)
        print("\n")
