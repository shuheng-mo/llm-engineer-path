"""MCP 拦截器 — 洋葱模式组合多个拦截器

对应课程章节：模块三 / 4.5.1 拦截器组合
"""
async def outer_interceptor(request, handler):
    print("外层: 执行前")
    result = await handler(request)
    print("外层: 执行后")
    return result


async def inner_interceptor(request, handler):
    print("内层: 执行前")
    result = await handler(request)
    print("内层: 执行后")
    return result


# 执行顺序：外层(前) → 内层(前) → 工具 → 内层(后) → 外层(后)
# client = MultiServerMCPClient({...}, tool_interceptors=[outer_interceptor, inner_interceptor])
