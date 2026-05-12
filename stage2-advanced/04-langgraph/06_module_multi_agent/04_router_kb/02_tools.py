"""Router — Step 2：各垂直领域的工具

对应课程章节：模块六 / 五 / Step 2
"""

from langchain.tools import tool


@tool
def search_code(query: str) -> str:
    """在GitHub仓库中搜索代码"""
    return f"在代码库找到匹配 '{query}' 的结果：src/auth.py 中的认证中间件"


@tool
def search_issues(query: str) -> str:
    """搜索GitHub问题和PR"""
    return f"找到3个匹配 '{query}' 的issue：#142, #89, #203"


@tool
def search_notion(query: str) -> str:
    """在Notion工作空间搜索文档"""
    return "找到文档：'API认证指南' - 涵盖OAuth2流程和JWT令牌"


@tool
def get_page(page_id: str) -> str:
    """获取特定Notion页面"""
    return "页面内容：认证设置的分步说明"


@tool
def search_slack(query: str) -> str:
    """搜索Slack消息和线程"""
    return "在 #engineering 发现讨论：'使用Bearer令牌进行API认证'"


@tool
def get_thread(thread_id: str) -> str:
    """获取特定Slack线程"""
    return "线程讨论了API密钥轮换的最佳实践"
