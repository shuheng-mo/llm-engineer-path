"""Self-RAG（自反思 RAG） — 四个反思点：是否检索/检索是否相关/答案是否有依据/答案是否有用

对应课程章节：二 / 6.2
"""
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()


class SelfRAG:
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
        self.need_retrieval_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """判断问题是否需要检索外部知识库。

不需要检索：简单计算、基础常识、创作任务、格式转换
需要检索：专业知识、公司/产品信息、最新数据、具体事实

只回答"需要"或"不需要"。""",
            ),
            ("human", "{question}"),
        ])

        self.is_relevant_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                '判断检索结果是否与问题相关，即是否包含回答问题所需的信息。\n只回答"相关"或"不相关"。',
            ),
            ("human", "问题：{question}\n\n检索结果：\n{context}"),
        ])

        self.is_supported_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                '判断答案中的信息是否都能在参考文档中找到依据。\n如果答案包含参考文档中没有的信息，则"无依据"。\n只回答"有依据"或"无依据"。',
            ),
            ("human", "参考文档：\n{context}\n\n答案：\n{answer}"),
        ])

        self.is_useful_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                '判断答案是否有效回答了问题。\n有用的答案应该直接、具体、可操作。\n只回答"有用"或"无用"。',
            ),
            ("human", "问题：{question}\n\n答案：{answer}"),
        ])

        self.generate_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """根据参考文档回答问题。
只使用文档中的信息，不要编造。
如果文档信息不足，说明哪些部分无法回答。

参考文档：
{context}""",
            ),
            ("human", "{question}"),
        ])

        self.direct_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有帮助的助手。"),
            ("human", "{question}"),
        ])

    def _reflect(self, prompt, **kwargs) -> str:
        return (prompt | self.llm).invoke(kwargs).content.strip()

    def query(self, question: str) -> dict:
        result = {"question": question, "steps": [], "answer": None}

        # 1. 是否需要检索
        need_retrieval = self._reflect(self.need_retrieval_prompt, question=question)
        result["steps"].append({"step": "是否需要检索", "result": need_retrieval})
        if "不需要" in need_retrieval:
            answer = (self.direct_prompt | self.llm).invoke({"question": question})
            result["answer"] = answer.content
            result["steps"].append({"step": "直接回答", "result": "完成"})
            return result

        # 2. 检索
        docs = self.retriever.invoke(question)
        context = "\n\n".join(f"[{i + 1}] {d.page_content}" for i, d in enumerate(docs))
        result["steps"].append({"step": "执行检索", "result": f"检索到 {len(docs)} 个文档"})

        # 3. 检索是否相关
        is_relevant = self._reflect(self.is_relevant_prompt, question=question, context=context)
        result["steps"].append({"step": "检索结果是否相关", "result": is_relevant})
        if "不相关" in is_relevant:
            result["answer"] = "抱歉，未能找到与您问题相关的信息。请尝试换一种方式提问，或确认问题是否在知识库覆盖范围内。"
            return result

        # 4. 生成
        answer = (self.generate_prompt | self.llm).invoke(
            {"question": question, "context": context}
        ).content
        result["steps"].append({"step": "生成答案", "result": "完成"})

        # 5. 答案是否有依据
        is_supported = self._reflect(self.is_supported_prompt, context=context, answer=answer)
        result["steps"].append({"step": "答案是否有依据", "result": is_supported})
        if "无依据" in is_supported:
            answer = (self.generate_prompt | self.llm).invoke({
                "question": question + "\n\n【重要】只使用文档中明确提到的信息，不要推断或补充。",
                "context": context,
            }).content
            result["steps"].append({"step": "重新生成（加强约束）", "result": "完成"})

        # 6. 答案是否有用
        is_useful = self._reflect(self.is_useful_prompt, question=question, answer=answer)
        result["steps"].append({"step": "答案是否有用", "result": is_useful})

        result["answer"] = answer
        return result

    def query_with_trace(self, question: str):
        print(f"\n{'=' * 60}")
        print(f" 问题: {question}")
        print("=" * 60)

        result = self.query(question)
        print("\n Self-RAG 执行过程:")
        for step in result["steps"]:
            print(f"   • {step['step']}: {step['result']}")

        print(f"\n 最终答案:\n{result['answer']}")
        return result


if __name__ == "__main__":
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    vectorstore = Chroma(persist_directory=str(DATA_DIR / "chroma_db"), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    self_rag = SelfRAG(retriever)

    for q in ["1+1等于多少？", "公司的年假政策是什么？", "Python 的 GIL 是什么？"]:
        self_rag.query_with_trace(q)
