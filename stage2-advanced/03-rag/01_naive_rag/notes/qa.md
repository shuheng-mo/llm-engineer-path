# Naive RAG Q&A

1. langchain_community.document_loaders 的lazy_load()方法底层原理是什么(哪些场景下使用更有收益)？如何进行重载？
2. 对于一些复杂PDF，比如有图层pypdf无法识别文档内容的情况下最佳实践是什么？OCR吗？如果不是我们怎么做？
3. 既然Embedding Model在RAG流程中很重要，那么我们在选择Embedding Model时应该考虑哪些因素？怎么评判Embedding模型向量化的质量？
4. chunk size和chunk overlap的取值如何影响Embedding和下游的检索效果？有没有实际的例子说明它们之间的直接关系？
5. 为什么调试RAG runnale pipeline比较麻烦？为什么要使用astream_events来调试？有没有其他更好的调试方法？
6. LLM Eval的框架比如现在的Terminal-bench和常见的LLM as Judge方法和Ragas在设计和底层原理上有没有根本的不同？Ragas说到底也是LLM as Judge的一种吧？如何规避模型当裁判的时候裁判本身存在幻觉或者不确定性的问题？还有就是LLM界的通病：Ragas 离线分数高≠用户满意。线上真实用户满意度跟离线评分的相关性到底有多强？怎么验证？
7. 向量化是离线昂贵、检索是在线轻量的。当 PDF 库的文档增 / 删 /
  改时，向量库怎么增量更新？什么时候必须全量重建？
8. 如果是多用户SaaS 场景：用户 A 上传的私密文档怎么保证不被用户 B
  查到？租户隔离应该做在向量库层还是检索层？这个有没有什么最佳实践？
9. 怎么让系统知道"这个问题在我的知识库里没有"？光靠 prompt 让 LLM说"不知道"够吗？有没有更可靠的机制？
10. 考虑成本的话，embedding API 调用 = 索引时的 chunk 数 + 每次查询？怎么算清楚一个 RAG 项目的 token预算？哪一块最容易花超？
