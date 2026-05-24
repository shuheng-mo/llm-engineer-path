"""
私密笔记本 —— FastAPI 用户认证系统
运行方式: uvicorn main:app --reload
测试方式: 访问 http://127.0.0.1:8000/docs 使用 Swagger UI 测试
"""

import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel

# ===================== 配置 =====================
SECRET_KEY = "my-notebook-secret-key-2024"  # 生产环境应从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===================== 应用初始化 =====================
app = FastAPI(title="私密笔记本")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ===================== 模拟数据库 =====================
users_db: dict = {}  # {"alice": {"username": "alice", "hashed_password": "..."}}
notes_db: list = []  # [{"id": 1, "owner": "alice", "title": "...", "content": "..."}]
note_id_counter = 0


# ===================== 数据模型 =====================
class UserRegister(BaseModel):
    username: str
    password: str


class NoteCreate(BaseModel):
    title: str
    content: str


# ===================== 工具函数 =====================


def hash_password(password: str) -> str:
    """将明文密码进行 bcrypt 哈希加密"""
    password_bytes = password.encode("utf-8")  # 字符串转字节（bcrypt 要求）
    salt = bcrypt.gensalt()  # 生成随机盐值
    hashed = bcrypt.hashpw(password_bytes, salt)  # 哈希加密
    return hashed.decode("utf-8")  # 字节转字符串，方便存储


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与数据库中的哈希值匹配"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),  # bcrypt 自动从哈希值中提取盐
        hashed_password.encode("utf-8"),  # 无需手动管理盐值
    )


def create_access_token(data: dict) -> str:
    """生成 JWT 访问令牌"""
    to_encode = data.copy()  # 复制字典，避免修改原数据
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # 添加过期时间（JWT 规范字段）
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ===================== 核心依赖：获取当前用户 =====================


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    路由保护的核心依赖函数:
    1. Depends(oauth2_scheme) 自动从请求头 Authorization: Bearer <token> 中提取令牌
    2. 用密钥解析令牌，验证签名和过期时间
    3. 从载荷中取出用户名，查询数据库返回用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


# ===================== 接口路由 =====================


@app.post("/register")
def register(user: UserRegister):
    """用户注册：密码经 bcrypt 哈希后存储"""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")

    users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password),  # 绝不存储明文密码
    }
    return {"message": "注册成功", "username": user.username}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录：验证密码，返回 JWT 令牌"""
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 令牌载荷只放用户标识，不放密码等敏感信息（Payload 是 Base64 编码，可被解码查看）
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/notes")
def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    """创建笔记（需登录），笔记自动绑定当前用户"""
    global note_id_counter
    note_id_counter += 1
    new_note = {
        "id": note_id_counter,
        "owner": current_user["username"],
        "title": note.title,
        "content": note.content,
    }
    notes_db.append(new_note)
    return {"message": "笔记创建成功", "note": new_note}


@app.get("/notes")
def get_my_notes(current_user: dict = Depends(get_current_user)):
    """查看当前用户的笔记列表（需登录），只能看到自己的笔记"""
    my_notes = [n for n in notes_db if n["owner"] == current_user["username"]]
    return {"username": current_user["username"], "notes": my_notes}
