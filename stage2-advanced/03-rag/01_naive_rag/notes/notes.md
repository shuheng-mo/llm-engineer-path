# Naive RAG

1. 4代RAG范式演进: naive rag -> advanced rag -> graph rag -> agentic rag
2. RAG的基本流程：

```
文档 → Chunk → Embedding → Vector Store → Retrieve → Prompt → Model → Answer
```

需要注意的是Embedding Model在这个过程中很重要，文本片段向量化以及用户提问转查询向量化都依赖于Embedding Model的质量。

## 文件加载注意事项

1. 编码：确保文件编码正确，常见的编码格式有UTF-8、GBK等。错误的编码可能导致文本内容无法正确读取。
2. 大文件处理：大文件一次性加载内存可能溢出，懒加载、分批处理以及流式处理是常见的解决方案。
3. PDF中出现复杂结构：PDF文件可能包含表格、图像等复杂结构，使用专门的PDF解析库（如PyPDF2、pdfplumber、langchain的unstructured loader）可以更好地提取文本内容。
4. 网页动态内容：如果需要从网页加载数据，可能会遇到动态内容加载的问题，使用Selenium、Playwright等工具可以模拟浏览器行为，获取完整的网页内容跳过js渲染的内容无法获取的问题。

## 文本分割

三个问题：

1. 语义稀释，长文档直接embedding会导致语义稀释，无法捕捉到文档的细节信息。
2. 检索噪声，过大的文本块可能包含不相关的信息，增加检索的噪声。
3. 上下文限制，模型的输入长度有限，过长的文本块可能超出模型的输入限制，导致无法处理。

在使用splitter的过程中，chunk size和chunk overlap是两个重要的参数：

- chunk size：每个文本块的最大长度，通常根据模型的输入限制和文本内容的特点来设置。具体要看下游的Embedding Model或者其他模型的输入限制来设置，通常建议设置在模型输入限制的70%-80%左右，以留出足够的空间给其他输入内容。
- chunk overlap：文本块之间的重叠部分，通常设置为chunk size的10%-20%左右。重叠部分可以帮助模型更好地理解文本块之间的关系，减少信息丢失。

合适的separator可以帮助splitter更好地分割文本，常见的separator有换行符、句号、空格等。选择合适的separator可以根据文本内容的结构来决定，例如对于段落较长的文本，可以使用换行符作为separator，而对于句子较短的文本，可以使用句号作为separator。

## Embedding Model嵌入模型与嵌入的方式
