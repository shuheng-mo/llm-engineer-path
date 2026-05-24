"""7.3 完整 security 模块 — JWT 生成 + get_current_user"""

# 导入时间相关模块：处理令牌过期时间
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# 导入jwt核心库：生成JWT令牌
from jose import jwt, JWTError
from starlette import status

# 1. 配置项（项目中建议单独放在配置文件里）
SECRET_KEY = "YOUR_SUPER_SECRET_KEY"  # 服务器专属密钥，生产环境绝对不能硬编码！
ALGORITHM = "HS256"  # 生成JWT的加密算法，本次用对称加密HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 令牌有效期，30分钟后自动失效


def create_access_token(data: dict):
    """
    核心功能：生成JWT访问令牌
    :param data: 要存入令牌的用户信息（字典类型，如{"user_id": 1, "username": "zhangsan"}）
    :return: 生成的JWT令牌字符串
    """
    # 1. 复制传入的用户信息，避免修改原字典（开发规范，防止副作用）
    to_encode = data.copy()

    # 2. 计算令牌的过期时间：当前UTC时间 + 有效期（30分钟）
    # 用timezone.utc避免本地时间时区问题，保证跨服务器/跨地区时间一致
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 3. 给要加密的字典，添加过期时间（key固定为"exp"，JWT规范要求）
    to_encode.update({"exp": expire})

    # 4. 生成JWT令牌核心步骤
    # 参数说明：要加密的字典 + 服务器密钥 + 加密算法
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # 5. 返回生成的令牌字符串，给前端使用
    return encoded_jwt


# 1. 实例化OAuth2PasswordBearer，指定令牌获取接口地址
# 作用：告诉FastAPI自动从请求头提取Bearer Token，提取失败直接返回401
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # tokenUrl为前端登录获取令牌的接口（如/token）


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


# ------------------- 测试代码 -------------------
if __name__ == "__main__":
    # 模拟用户登录成功，获取的用户信息（仅存非敏感信息！）
    user_info = {"user_id": 1, "username": "zhangsan"}

    # 生成JWT令牌
    token = create_access_token(user_info)
    print("生成的JWT令牌：")
    print(token)
