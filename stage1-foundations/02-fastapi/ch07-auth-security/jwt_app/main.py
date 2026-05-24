"""7.3 完整 demo — 登录获取 token + 受保护路由

运行: cd jwt_app && uv run uvicorn main:app --reload
文档: http://127.0.0.1:8000/docs
"""

# main.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from utils.security import create_access_token, get_current_user

# 创建FastAPI实例
app = FastAPI(title="JWT令牌验证示例", version="1.0")

# ==================== 模拟用户数据库（真实场景替换为数据库查询） ====================
fake_users_db = {
    "zhangsan": {
        "user_id": 1,
        "username": "zhangsan",
        "password": "123456",  # 生产环境务必加密存储（如bcrypt）
    },
    "lisi": {"user_id": 2, "username": "lisi", "password": "654321"},
}


# ==================== 登录接口（生成令牌） ====================
@app.post("/token", summary="用户登录，获取JWT令牌")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    接收用户名密码，验证通过后返回JWT令牌。

    ⚠️ 响应结构必须符合 OAuth2 规范 (RFC 6749 §5.1):
        access_token / token_type 必须在响应**顶层**，不能套娃在 data 里！
    否则:
      - Swagger UI 的 Authorize 按钮看不到 token → 后续请求不会自动带 Bearer
      - 标准 OAuth2 客户端 SDK 解不出 token
    原 docx 代码包了一层 {"code":200, "data":{...}} 是 bug，已修正。
    """
    # 1. 验证用户是否存在
    user = fake_users_db.get(form_data.username)
    if not user:
        # 失败时应抛 HTTPException 401，让 Swagger UI 正确显示登录失败
        raise HTTPException(status_code=401, detail="用户名不存在")

    # 2. 验证密码（真实场景用加密算法验证，如 bcrypt.checkpw）
    if form_data.password != user["password"]:
        raise HTTPException(status_code=401, detail="密码错误")

    # 3. 生成 JWT 令牌（payload 必须包含 "sub" 字段）
    access_token = create_access_token(data={"sub": user["username"], "user_id": user["user_id"]})

    # 4. 返回令牌 — OAuth2 标准扁平结构（access_token / token_type 在顶层）
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # 过期秒数，可选字段
    }


# ==================== 受保护的接口（需要验证令牌） ====================
@app.get("/protected", summary="受保护的接口（需携带有效JWT令牌）")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """
    依赖get_current_user函数，只有令牌有效时才能访问
    current_user会自动接收解析后的用户信息
    """
    return {
        "code": 200,
        "message": "访问受保护接口成功",
        "data": {"current_user": current_user, "content": "这是只有登录用户才能看到的内容"},
    }


# ==================== 主函数（运行服务） ====================
if __name__ == "__main__":
    import uvicorn

    # 启动服务：地址0.0.0.0，端口8000，自动重载
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
