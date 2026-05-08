"""Advanced RAG PDF 阅读助手 — 6 大技术综合：父文档/查询优化/混合检索/重排序/LCR/带引用

对应课程章节：二 / 7. 阶段总结实战
"""
import os
from collections import defaultdict
from typing import Dict, List, Tuple

from dotenv import load_dotenv

# ========== LangChain v1.0 核心导入 ==========
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ========== 集成包（v1.0 兼容）==========
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ========== LangChain Classic / Cross-Encoder 可选 ==========
try:
    from langchain_classic.retrievers import EnsembleRetriever, ParentDocumentRetriever  # noqa: F401
    LANGCHAIN_CLASSIC_AVAILABLE = True
except ImportError:
    LANGCHAIN_CLASSIC_AVAILABLE = False
    print("⚠️ langchain-classic 未安装，将使用自定义实现")

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    print("⚠️ sentence-transformers 未安装，将使用 LLM 重排序")

load_dotenv()


class AdvancedRAGAssistant:
    """Advanced RAG PDF 阅读助手 — LangChain v1.0 兼容版本。

    集成技术:
    1. 父文档检索（小块检索，大块返回）
    2. 查询优化（改写 + Multi-Query）
    3. 混合检索（BM25 + Dense + RRF）
    4. Cross-Encoder / LLM 重排序
    5. Long Context Reorder
    6. 带引用的生成
    """

    def __init__(
        self,
        pdf_path: str = None,
        pdf_directory: str = None,
        use_hybrid_search: bool = True,
        use_reranker: bool = True,
        use_query_optimization: bool = True,
        use_context_reorder: bool = True,
        parent_chunk_size: int = 1000,
        child_chunk_size: int = 200,
    ):
        self.use_hybrid_search = use_hybrid_search
        self.use_reranker = use_reranker
        self.use_query_optimization = use_query_optimization
        self.use_context_reorder = use_context_reorder

        self.llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0.3,
        )
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
        )

        self.documents = self._load_documents(pdf_path, pdf_directory)

        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=100,
            separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=20,
            separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
        )

        self.parent_docs, self.child_docs, self.child_to_parent = self._create_parent_child_chunks()

        self.vectorstore = Chroma.from_documents(
            documents=self.child_docs,
            embedding=self.embeddings,
            persist_directory=str(DATA_DIR / "advanced_rag_v1_db"),
        )
        print(f"💾 向量数据库创建完成（{len(self.child_docs)} 个子文档块）")

        if self.use_hybrid_search:
            self.bm25_retriever = BM25Retriever.from_documents(self.child_docs)
            self.bm25_retriever.k = 10
            print("🔍 BM25 检索器创建完成")

        if self.use_reranker and CROSS_ENCODER_AVAILABLE:
            self.reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
            print("🎯 Cross-Encoder 重排序器加载完成")
        else:
            self.reranker = None

        self._init_prompts()
        self.chat_history: List = []
        self._print_init_summary()

    def _print_init_summary(self):
        print("\n" + "=" * 60)
        print(" Advanced RAG 助手初始化完成！(LangChain v1.0)")
        print("=" * 60)
        print("📌 启用技术:")
        print("   • 父文档检索: ✅")
        print(f"   • 查询优化: {'✅' if self.use_query_optimization else '❌'}")
        print(f"   • 混合检索: {'✅' if self.use_hybrid_search else '❌'}")
        print(f"   • 重排序: {'✅ Cross-Encoder' if self.reranker else '✅ LLM Reranker' if self.use_reranker else '❌'}")
        print(f"   • 上下文重排序: {'✅' if self.use_context_reorder else '❌'}")
        print("   • 带引用生成: ✅")
        print("=" * 60 + "\n")

    def _load_documents(self, pdf_path, pdf_directory):
        documents = []
        if pdf_path:
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
            print(f" 已加载文件: {pdf_path}")
        if pdf_directory:
            loader = DirectoryLoader(
                pdf_directory, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True
            )
            documents.extend(loader.load())
            print(f" 已加载目录: {pdf_directory}")
        if not documents:
            print("⚠️ 未加载任何文档，请检查路径")
        print(f"📄 共加载 {len(documents)} 个文档页面")
        return documents

    def _create_parent_child_chunks(self) -> Tuple[List[Document], List[Document], Dict]:
        parent_docs, child_docs, child_to_parent = [], [], {}
        parent_chunks = self.parent_splitter.split_documents(self.documents)
        for parent_idx, parent_doc in enumerate(parent_chunks):
            parent_doc.metadata["parent_idx"] = parent_idx
            parent_docs.append(parent_doc)
            for child_idx, child_content in enumerate(self.child_splitter.split_text(parent_doc.page_content)):
                child_id = f"parent_{parent_idx}_child_{child_idx}"
                child_doc = Document(
                    page_content=child_content,
                    metadata={**parent_doc.metadata, "child_id": child_id, "parent_idx": parent_idx},
                )
                child_docs.append(child_doc)
                child_to_parent[child_id] = parent_idx
        print(f"📝 创建 {len(parent_docs)} 个父文档，{len(child_docs)} 个子文档")
        return parent_docs, child_docs, child_to_parent

    def _init_prompts(self):
        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """你是搜索查询优化专家。将用户的口语化问题改写为适合知识库检索的查询。

【改写规则】
1. 去除口语词（啥、咋、啊、呢、吗）
2. 展开模糊动词（处理→读取/写入/解析）
3. 补充专业术语和同义词
4. 保持简洁，不超过 30 字

只输出改写后的查询，无需解释。""",
            ),
            ("human", "{question}"),
        ])
        self.multi_query_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """生成 3 个不同角度的搜索查询，帮助更全面地检索相关文档。

【要求】
- 每个查询从不同角度切入（如：定义、原理、应用、对比）
- 用换行分隔，不要编号
- 直接输出查询，无需解释""",
            ),
            ("human", "原问题：{question}"),
        ])
        self.rag_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """你是一个专业的 PDF 文档阅读助手。

【任务】根据参考文档回答用户问题

【规则】
1. 只使用参考文档中的信息，不要使用你自己的知识
2. 在回答中使用 [文档X] 标注引用了哪个文档
3. 如果文档中没有答案，直接说"根据现有资料无法回答"
4. 回答要准确、简洁、有条理

【参考文档】
{context}""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])
        self.rerank_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """评估文档与查询的相关性，给出 0-10 的分数。
只输出一个数字，不要有任何其他内容。

评分标准：
- 0-3：不相关
- 4-6：部分相关
- 7-10：高度相关""",
            ),
            ("human", "查询：{query}\n\n文档：{document}\n\n相关性分数："),
        ])

    # ── 查询优化 ──
    def _rewrite_query(self, question: str) -> str:
        return (self.rewrite_prompt | self.llm).invoke({"question": question}).content.strip()

    def _generate_multi_queries(self, question: str) -> List[str]:
        response = (self.multi_query_prompt | self.llm).invoke({"question": question})
        return [q.strip() for q in response.content.strip().split("\n") if q.strip()]

    def _optimize_query(self, question: str) -> List[str]:
        queries = [question]
        rewritten = self._rewrite_query(question)
        if rewritten and rewritten != question:
            queries.append(rewritten)
        queries.extend(self._generate_multi_queries(question))
        return list(dict.fromkeys(queries))[:5]

    # ── 混合检索 ──
    def _vector_search(self, query: str, k: int = 10) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)

    def _bm25_search(self, query: str) -> List[Document]:
        return self.bm25_retriever.invoke(query)

    def _rrf_fusion(self, results_list: List[List[Document]], k: int = 60, top_n: int = 10) -> List[Document]:
        rrf_scores = defaultdict(float)
        doc_map = {}
        for results in results_list:
            for rank, doc in enumerate(results, start=1):
                doc_id = hash(doc.page_content[:200])
                rrf_scores[doc_id] += 1 / (k + rank)
                doc_map[doc_id] = doc
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_map[doc_id] for doc_id, _ in sorted_docs[:top_n]]

    def _hybrid_search(self, queries: List[str], k: int = 10) -> List[Document]:
        all_results = []
        for query in queries:
            all_results.append(self._vector_search(query, k=k))
            if self.use_hybrid_search:
                all_results.append(self._bm25_search(query))
        return self._rrf_fusion(all_results, top_n=k)

    # ── 父文档 ──
    def _get_parent_documents(self, child_docs: List[Document]) -> List[Document]:
        parent_indices = {doc.metadata.get("parent_idx") for doc in child_docs if doc.metadata.get("parent_idx") is not None}
        return [self.parent_docs[idx] for idx in sorted(parent_indices) if idx < len(self.parent_docs)]

    # ── 重排序 ──
    def _rerank_with_cross_encoder(self, query, docs, top_n=5):
        if not docs:
            return []
        scores = self.reranker.predict([(query, d.page_content) for d in docs])
        return [d for d, _ in sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)[:top_n]]

    def _rerank_with_llm(self, query, docs, top_n=5):
        scored = []
        for doc in docs:
            response = (self.rerank_prompt | self.llm).invoke({"query": query, "document": doc.page_content[:500]})
            try:
                score = float(response.content.strip())
            except Exception:
                score = 5.0
            scored.append((doc, score))
        return [d for d, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:top_n]]

    def _rerank(self, query, docs, top_n=5):
        if self.reranker is not None:
            return self._rerank_with_cross_encoder(query, docs, top_n)
        return self._rerank_with_llm(query, docs, top_n)

    # ── Long Context Reorder ──
    def _long_context_reorder(self, documents):
        if len(documents) <= 2:
            return documents
        odd, even = [], []
        for i, doc in enumerate(documents):
            (odd if i % 2 == 0 else even).append(doc)
        return odd + even[::-1]

    def _format_docs_with_citation(self, docs):
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            page = doc.metadata.get("page", "?")
            page_str = str(page + 1) if isinstance(page, int) else str(page)
            formatted.append(
                f"[文档{i}] 来源: {os.path.basename(source)} | 第 {page_str} 页\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(formatted)

    def retrieve(self, question, top_k=5, verbose=False):
        if verbose:
            print(f"\n🔍 开始检索: {question}")

        queries = self._optimize_query(question) if self.use_query_optimization else [question]
        if verbose:
            print(f"   📝 查询优化: {len(queries)} 个查询变体")
            for q in queries:
                print(f"      - {q}")

        child_results = self._hybrid_search(queries, k=20)
        if verbose:
            print(f"   🔎 混合检索: 找到 {len(child_results)} 个子文档")

        parent_results = self._get_parent_documents(child_results)
        if verbose:
            print(f"   📚 父文档检索: 映射到 {len(parent_results)} 个父文档")

        if self.use_reranker and len(parent_results) > top_k:
            reranked = self._rerank(question, parent_results, top_n=top_k)
            if verbose:
                print(f"   🎯 重排序: 保留 Top-{len(reranked)}")
        else:
            reranked = parent_results[:top_k]

        if self.use_context_reorder:
            final = self._long_context_reorder(reranked)
            if verbose:
                print("   🔄 上下文重排序: 完成")
        else:
            final = reranked

        return final

    def ask(self, question, verbose=False):
        docs = self.retrieve(question, top_k=5, verbose=verbose)
        if not docs:
            return "抱歉，未能找到与您问题相关的信息。"

        context = self._format_docs_with_citation(docs)
        response = (self.rag_prompt | self.llm | StrOutputParser()).invoke({
            "context": context,
            "question": question,
            "chat_history": self.chat_history,
        })

        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=response))
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        return response

    def clear_history(self):
        self.chat_history = []
        print("🔄 对话历史已清除")


def main():
    print("=" * 70)
    print("📚 Advanced RAG PDF 阅读助手 (LangChain v1.0)")
    print("=" * 70)

    assistant = AdvancedRAGAssistant(
        pdf_directory=str(DATA_DIR),
        use_hybrid_search=True,
        use_reranker=True,
        use_query_optimization=True,
        use_context_reorder=True,
    )

    print("\n💡 提示：输入 'quit' 退出，'clear' 清除历史，'verbose' 切换详细模式\n")

    verbose_mode = False
    while True:
        question = input("🙋 你的问题: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            print("👋 再见！")
            break
        if question.lower() == "clear":
            assistant.clear_history()
            continue
        if question.lower() == "verbose":
            verbose_mode = not verbose_mode
            print(f"📢 详细模式: {'开启' if verbose_mode else '关闭'}")
            continue

        try:
            answer = assistant.ask(question, verbose=verbose_mode)
            print(f"\n🤖 回答:\n{answer}\n")
            print("-" * 70)
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

            traceback.print_exc()


if __name__ == "__main__":
    main()
