"""Long Context Reorder（手动实现） — 理解 odd/even 重排原理

对应课程章节：二 / 5.2 方式二
"""


def long_context_reorder(documents: list) -> list:
    """Long Context Reorder 手动实现。

    原理：
    - 相关性排名为奇数（1, 3, 5...）的文档放前半部分
    - 偶数（2, 4, 6...）放后半部分，且倒序
    最相关 (#1) 在开头，第二相关 (#2) 在结尾。
    """
    if len(documents) <= 2:
        return documents

    odd_rank, even_rank = [], []
    for i, doc in enumerate(documents):
        if i % 2 == 0:
            odd_rank.append(doc)
        else:
            even_rank.append(doc)

    return odd_rank + even_rank[::-1]


if __name__ == "__main__":
    docs = [f"Doc{i}(相关性#{i})" for i in range(1, 8)]
    print("原始顺序:", docs)
    print("重排序后:", long_context_reorder(docs))
