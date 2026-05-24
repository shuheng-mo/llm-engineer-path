"""7.1 密码安全 — bcrypt 哈希 & 校验"""

import bcrypt  # 导入 bcrypt 加密库


def get_password_hash(password: str) -> str:
    """
    功能：将明文密码加密成哈希值（密文）
    :param password: 传入的明文密码（如用户注册时输入的 123456）
    :return: 加密后的哈希字符串（可直接存入数据库）
    """
    # 1. 将字符串密码转换为字节类型（bcrypt 库只支持字节流处理）
    password_bytes = password.encode("utf-8")

    # 2. 生成随机盐值（默认加密难度）
    salt = bcrypt.gensalt()

    # 3. 核心加密：将密码和盐值拼接后哈希，生成密文（字节类型）
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)

    # 4. 将字节类型的密文转换为字符串，方便存入数据库
    return hashed_password_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    功能：验证用户输入的明文密码，与数据库中的密文是否匹配
    :param plain_password: 用户登录时输入的明文密码
    :param hashed_password: 从数据库中取出的密文（哈希值）
    :return: 匹配返回 True，不匹配返回 False
    """
    # 1. 将明文密码和密文都转换为字节类型
    plain_pwd_bytes = plain_password.encode("utf-8")
    hashed_pwd_bytes = hashed_password.encode("utf-8")

    # 2. 核心验证：bcrypt 会自动从密文中提取盐值，与明文密码重新哈希对比
    # 无需手动处理盐值，直接返回对比结果（True/False）
    return bcrypt.checkpw(plain_pwd_bytes, hashed_pwd_bytes)


# ------------------- 测试代码 -------------------
if __name__ == "__main__":
    # 1. 模拟用户注册：加密密码
    original_password = "my_secure_password"  # 用户设置的明文密码
    hashed_pwd = get_password_hash(original_password)
    print(
        f"加密后的密文：{hashed_pwd}"
    )  # 输出类似：$2b$12$EixZaYb4xU58Gpq1R0yWbeb00LU5qUaK6x6h9s6Q0hW8XQd6cR5u

    # 2. 模拟用户登录：验证密码
    # 正确密码验证
    is_correct = verify_password(original_password, hashed_pwd)
    print(f"密码验证结果（正确密码）：{is_correct}")  # 输出：True

    # 错误密码验证
    wrong_password = "wrong_password"
    is_wrong = verify_password(wrong_password, hashed_pwd)
    print(f"密码验证结果（错误密码）：{is_wrong}")  # 输出：False
