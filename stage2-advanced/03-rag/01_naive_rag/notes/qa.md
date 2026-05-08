1. langchain_community.document_loaders 的lazy_load()方法底层原理是什么？如何进行重载？
2. 对于一些复杂PDF，比如有图层pypdf无法识别文档内容的情况下最佳实践是什么？OCR吗？如果不是我们怎么做？
3. 既然Embedding Model在RAG流程中很重要，那么我们在选择Embedding Model时应该考虑哪些因素？怎么评判Embedding模型向量化的质量？
4. chunk size和chunk overlap的取值如何影响Embedding和下游的检索效果？有没有实际的例子说明它们之间的直接关系？
5. 为什么调试RAG runnale pipeline比较麻烦？为什么要使用astream_events来调试？有没有其他更好的调试方法？
