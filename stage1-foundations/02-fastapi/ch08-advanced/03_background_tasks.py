"""8.3 后台任务 — BackgroundTasks

场景：HTTP 请求处理完后，还有些"不影响响应"的工作要做，例如：
  - 注册成功后发欢迎邮件
  - 操作完成后写审计日志
  - 触发缓存预热 / webhook 回调

FastAPI 的 BackgroundTasks 让你**先返回响应给客户端**，再异步执行这些副作用。
工作流程：
    Client → POST /register → 立即返回 {"ok": true}
                              ↓
                          后台执行: 发邮件 + 写日志 (客户端已经拿到响应了)

⚠️ 限制：
  - BackgroundTasks 跟主请求**同进程同事件循环**，挂了不会重试
  - 任务长 / 重要 / 需重试 → 上 Celery / Arq / Dramatiq / RQ 等真正的任务队列

运行: uv run uvicorn 03_background_tasks:app --reload
测试:
    curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" \\
      -d '{"username":"alice","email":"alice@example.com"}'
    # 立即返回，但服务器控制台会延迟 2 秒看到 "已发送欢迎邮件"
"""

import time
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI(title="Background Tasks Demo")

# 审计日志文件 (放在 02-fastapi/data/ 下，已 .gitignore)
_LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "audit.log"
_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# ── 后台任务函数 (普通 def 或 async def 都行) ─────────────────────
def send_welcome_email(email: str):
    """模拟发邮件 — 故意 sleep 2 秒，观察"响应已返回但任务还在跑"的效果"""
    print(f"  [BG] 准备给 {email} 发欢迎邮件...")
    time.sleep(2)  # 模拟 SMTP 调用延迟
    print(f"  [BG] ✅ 已发送欢迎邮件 → {email}")


def write_audit_log(action: str, user: str):
    """写审计日志到文件"""
    line = f"{datetime.now().isoformat()} | {action} | user={user}\n"
    _LOG_FILE.write_text(_LOG_FILE.read_text() + line if _LOG_FILE.exists() else line)
    print(f"  [BG] 📝 审计日志已写入 → {action}")


# ── 请求模型 ──────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    email: str


# ── 单个后台任务 ──────────────────────────────────────────────────
@app.post("/register")
async def register(req: RegisterRequest, bg: BackgroundTasks):
    """注册成功立即返回，邮件在后台发出"""
    print(f"路由函数执行中... 用户={req.username}")
    bg.add_task(send_welcome_email, req.email)  # ← 加入后台任务队列
    print("路由函数返回响应 (此时邮件还没发)")
    return {"ok": True, "username": req.username}


# ── 多个任务链式 ──────────────────────────────────────────────────
@app.post("/action/{name}")
async def do_action(name: str, bg: BackgroundTasks):
    """演示一次添加多个后台任务，它们按 add_task 顺序串行执行"""
    bg.add_task(write_audit_log, action=f"do_action:{name}", user="anonymous")
    bg.add_task(send_welcome_email, email=f"admin@example.com")  # 通知管理员
    bg.add_task(write_audit_log, action=f"notify_admin:{name}", user="system")
    return {"ok": True, "action": name, "queued_tasks": 3}


# ── 什么时候需要换成 Celery? ─────────────────────────────────────
# BackgroundTasks 适用于：
#   ✓ 任务轻量 (< 几秒)
#   ✓ 失败可丢 (邮件没发就重发一次邀请也无妨)
#   ✓ 不需要持久化、跨服务、定时调度
#
# 上 Celery / Arq / Dramatiq 的信号：
#   ✗ 任务长 (> 30s)，会拖累 worker 处理新请求
#   ✗ 必须重试、必须确保送达
#   ✗ 需要定时执行 (cron-like)
#   ✗ 任务由多个服务共同消费 (用 Redis/RabbitMQ 做队列)
