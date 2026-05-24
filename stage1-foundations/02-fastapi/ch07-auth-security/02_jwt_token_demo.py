"""7.2 JWT 令牌生成示例"""

# 导入时间相关模块：处理令牌过期时间
from datetime import datetime, timedelta, timezone

# 导入jwt核心库：生成JWT令牌
from jose import jwt

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


# ------------------- 测试代码 -------------------
if __name__ == "__main__":
    # 模拟用户登录成功，获取的用户信息（仅存非敏感信息！）
    user_info = {"user_id": 1, "username": "zhangsan"}
    # 生成JWT令牌
    token = create_access_token(user_info)
    print("生成的JWT令牌：")
    print(token)
