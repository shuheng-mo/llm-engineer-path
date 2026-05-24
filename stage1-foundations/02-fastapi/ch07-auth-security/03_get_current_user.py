"""7.3 路由保护 — get_current_user 依赖"""

# 导入FastAPI核心组件：依赖注入、异常抛出、状态码
from fastapi import Depends, HTTPException, status

# 导入FastAPI的OAuth2密码模式工具：自动提取Bearer Token
from fastapi.security import OAuth2PasswordBearer

# 导入jwt库：解析/验证JWT令牌，捕获令牌相关异常
from jose import JWTError, jwt

# 1. 实例化OAuth2PasswordBearer，指定令牌获取接口地址
# 作用：告诉FastAPI自动从请求头提取Bearer Token，提取失败直接返回401
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # tokenUrl为前端登录获取令牌的接口（如/token）

# 2. 配置项（与上面jwt令牌生成的配置完全一致，必须统一！）
SECRET_KEY = "YOUR_SUPER_SECRET_KEY"  # 服务器专属密钥，生产环境严禁硬编码
ALGORITHM = "HS256"  # 验证算法必须与生成令牌的算法一致
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 与生成令牌的有效期一致（仅作配置，本次代码未直接使用）


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    核心功能：FastAPI依赖注入函数，验证JWT令牌并解析当前用户信息
    :param token: 由Depends(oauth2_scheme)自动注入的JWT令牌字符串
    :return: 解析出的用户信息字典（真实场景返回数据库查询的用户对象）
    :raise: 令牌无效/解析失败时，抛出401未授权异常
    """
    # 定义标准化的401异常：令牌验证失败时统一抛出此异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,  # 401未授权状态码
        detail="无法验证凭据",  # 错误提示信息
        headers={"WWW-Authenticate": "Bearer"},  # 告诉前端需要携带Bearer Token
    )
    try:
        # 核心步骤1：解析JWT令牌，验证其有效性
        # 参数说明：令牌字符串 + 服务器密钥 + 允许的加密算法（与生成时一致）
        # 验证逻辑：自动检查签名是否被篡改、令牌是否过期、算法是否匹配
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 核心步骤2：从令牌的载荷（payload）中提取用户名（key为"sub"，JWT规范字段）
        # "sub"是JWT通用规范字段，代表“主题”，通常存储用户唯一标识（用户名/用户ID）
        username: str = payload.get("sub")

        # 校验：如果载荷中没有用户名，说明令牌无效，抛出401异常
        if username is None:
            raise credentials_exception

    # 捕获所有JWT相关异常：令牌篡改、过期、密钥错误、格式错误等
    except JWTError:
        raise credentials_exception

    # 打印当前用户（调试用），返回用户信息（供路由函数使用）
    print("当前访问用户：", username)
    return {"username": username}  # 真实场景返回查询到的user对象
