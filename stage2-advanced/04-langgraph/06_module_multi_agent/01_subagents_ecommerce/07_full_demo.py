"""Subagents — 完整 demo：端到端可运行的电商运营助手

把 01~06 各步骤串成一个可独立运行的脚本：

  Step 1  底层业务工具          (对应 01_tools.py)
  Step 2  专家子 Agent           (对应 02_subagents.py)
  Step 3  把子 Agent 包装为工具  (对应 03_wrap_as_tools.py)
  Step 4  Supervisor 协调者     (对应 04_supervisor.py)
  Step 5  运行示例              (对应 05_run_demo.py)
  Step 6  Human-in-the-loop      (对应 06_human_in_loop.py)

运行：
    uv run python stage2-advanced/04-langgraph/06_module_multi_agent/01_subagents_ecommerce/07_full_demo.py
"""

import pathlib
import sys
import uuid
from typing import Annotated

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import InjectedToolCallId, tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402


# ============================================================
# Step 1：底层业务工具
# ============================================================
@tool
def create_product(name: str, category: str, price: float, inventory: int) -> str:
    """创建新商品并上架。"""
    return f"商品已上架 - 名称: {name}, 类目: {category}, 价格: ¥{price}, 库存: {inventory}件"


@tool
def update_inventory(sku: str, quantity: int) -> str:
    """更新商品库存数量。"""
    return f"库存已更新 - SKU: {sku}, 新库存: {quantity}件"


@tool
def get_product_analytics(sku: str) -> str:
    """获取商品销售数据分析。"""
    return f"商品 {sku} 数据 - 浏览量: 1234, 销量: 45, 转化率: 3.6%"


@tool
def create_promotion(name: str, promotion_type: str, rules: str) -> str:
    """创建促销活动。"""
    return f"促销已创建 - 名称: {name}, 类型: {promotion_type}, 规则: {rules}"


@tool
def send_marketing_push(title: str, target_audience: str, channel: str) -> str:
    """发送营销推送消息。"""
    return f"推送已发送 - 标题: {title}, 渠道: {channel}, 目标: {target_audience}"


# ============================================================
# Step 2：专家子 Agent
#   product_agent 挂 HumanInTheLoopMiddleware：create_product 前会中断等审批
# ============================================================
model = get_chat_model("qwen-max")

PRODUCT_PROMPT = """你是电商商品管理专家。

职责：
- 创建和上架新商品
- 管理商品库存
- 分析商品销售数据

工作原则：
✓ 确保商品信息完整准确
✓ 在最终消息中包含所有操作结果"""

MARKETING_PROMPT = """你是电商营销推广专家。

职责：
- 创建各类促销活动
- 制定营销推送策略

工作原则：
✓ 活动规则清晰易懂
✓ 在最终消息中包含所有操作结果"""

# 关键：子 agent 必须自己有 checkpointer，HumanInTheLoopMiddleware 内部用
# langgraph.types.interrupt() 暂停执行，而 interrupt() 要求所在的图 (graph)
# 已挂 checkpointer，否则中断会失效（中断函数文档明确要求）。
product_agent = create_agent(
    model,
    tools=[create_product, update_inventory, get_product_analytics],
    system_prompt=PRODUCT_PROMPT,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"create_product": True},
            description_prefix="📦 商品上架待审批",
        ),
    ],
    checkpointer=InMemorySaver(),
)

marketing_agent = create_agent(
    model,
    tools=[create_promotion, send_marketing_push],
    system_prompt=MARKETING_PROMPT,
)


# ============================================================
# Step 3：把子 Agent 包装为工具（Command 跨节点写状态）
# ============================================================
@tool(
    "manage_product",
    description="""商品管理专家。

何时调用：
- 用户需要上架、修改或下架商品
- 涉及库存管理和调整
- 需要商品销售数据分析

输入：自然语言描述的商品管理需求
示例："上架一款夏季新款连衣裙，价格299元" """,
)
def manage_product(
    request: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """调用商品管理专家 Agent。

    HITL 流程的关键细节：
    1. 子 agent 用以 tool_call_id 为后缀的稳定 thread_id 保存自己的状态，
       supervisor 在 resume 时会重跑本 tool，凭这个 thread_id 找回上次中断态。
    2. 子 agent 第一次跑会因为 HumanInTheLoopMiddleware 中断，返回结果里带
       `__interrupt__`。我们在本 tool 内再调一次 `interrupt(...)` 把这份请求
       上报给 supervisor —— 这样 supervisor 的 checkpointer 会保存它、暂停。
    3. supervisor 被 `Command(resume={"decisions": [...]})` 唤醒后，重跑本
       tool；此时 supervisor 上的 `interrupt()` 直接返回 decisions，我们把它
       透传给子 agent 让子 agent 继续。
    4. 重跑时不能再喂 fresh input，否则子线程会因为 tool_calls 没有对应
       tool 响应而 400。用 get_state 判断子线程是否已有状态。
    """
    sub_config: RunnableConfig = {"configurable": {"thread_id": f"sub_product_{tool_call_id}"}}
    state = product_agent.get_state(sub_config)
    if not state.values:
        result = product_agent.invoke(
            {"messages": [{"role": "user", "content": request}]}, config=sub_config
        )
    else:
        # 我们在 resume 路径上；直接取回当前的待审批 interrupt
        pending = (
            list(state.tasks[0].interrupts) if state.tasks and state.tasks[0].interrupts else None
        )
        result = {"__interrupt__": pending} if pending else state.values  # type: ignore[assignment]

    while result.get("__interrupt__"):
        decisions = interrupt(result["__interrupt__"][0].value)
        result = product_agent.invoke(Command(resume=decisions), config=sub_config)

    final_message = result["messages"][-1].content
    return Command(
        update={"messages": [ToolMessage(content=final_message, tool_call_id=tool_call_id)]}
    )


@tool(
    "create_campaign",
    description="""营销推广专家。

何时调用：
- 用户需要创建促销活动
- 需要发送营销推送

输入：自然语言描述的营销需求
示例："创建618大促满减活动" """,
)
def create_campaign(
    request: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """调用营销推广专家 Agent。"""
    result = marketing_agent.invoke({"messages": [{"role": "user", "content": request}]})
    final_message = result["messages"][-1].content
    return Command(
        update={"messages": [ToolMessage(content=final_message, tool_call_id=tool_call_id)]}
    )


# ============================================================
# Step 4：Supervisor 协调者（带 checkpointer 支持 HITL 暂停/恢复）
# ============================================================
SUPERVISOR_PROMPT = """你是智能电商运营助手的协调者（Supervisor）。

核心能力：
1. 理解用户的复杂运营请求
2. 将任务分解为子任务
3. 选择合适的专家处理各个子任务
4. 整合结果形成完整回复

可用专家：
- manage_product: 处理所有商品管理任务
- create_campaign: 处理所有营销推广任务

工作流程：
1. 分析请求，识别需要哪些专家
2. 可以并行调用多个专家（工具）
3. 整合所有专家结果，提供连贯回复

注意：
- 多领域任务需要调用多个专家
- 给用户完整且易懂的结果"""

supervisor = create_agent(
    model,
    tools=[manage_product, create_campaign],
    system_prompt=SUPERVISOR_PROMPT,
    checkpointer=InMemorySaver(),
)


# ============================================================
# Step 5/6：演示
# ============================================================
def _print_final(result: dict) -> None:
    print(result["messages"][-1].content)


def _new_config() -> RunnableConfig:
    """每个 demo 用独立 thread_id，避免 HITL 之间的状态串扰。"""
    return {"configurable": {"thread_id": f"demo_{uuid.uuid4().hex[:8]}"}}


def demo_simple() -> None:
    """单领域请求：只触发 marketing_agent，不会被 HITL 中断。"""
    print("\n=== Demo 1: 简单请求（营销，无 HITL）===")
    result = supervisor.invoke(
        {"messages": [HumanMessage(content="创建一个618大促满199减30的促销活动，推送给所有会员")]},
        config=_new_config(),
    )
    _print_final(result)


def demo_multi_domain_auto_approve() -> None:
    """多领域请求：商品 + 营销并行。会触发 create_product 的 HITL，演示自动 approve。"""
    print("\n=== Demo 2: 多领域请求（HITL 自动 approve）===")
    config = _new_config()
    request = (
        "上架夏季新款防晒衣（类目：服装，价格159元，库存1000件），"
        '同时创建一个"清凉一夏"满199减20的促销活动'
    )
    result = supervisor.invoke({"messages": [HumanMessage(content=request)]}, config=config)
    result = _resume_until_done(
        result, config, interactive=False, default_decision={"type": "approve"}
    )
    _print_final(result)


def demo_hitl_interactive() -> None:
    """**真正在终端等待人工审批**。

    运行后会看到 supervisor 暂停，打印待审批的工具调用与参数，提示你输入：
      a / approve                 → 批准，执行 create_product
      r / reject [reason]         → 拒绝，把理由作为工具结果回灌给 LLM
      e / edit                    → 修改参数后再批准（之后会引导你按 K=V 形式输入）
    """
    print("\n=== Demo 3: HITL 交互式审批（请在终端按提示输入）===")
    config = _new_config()
    print("用户：上架一款蓝牙耳机，类目数码，价格199元，库存500件")
    result = supervisor.invoke(
        {"messages": [HumanMessage(content="上架一款蓝牙耳机，类目数码，价格199元，库存500件")]},
        config=config,
    )
    result = _resume_until_done(result, config, interactive=True)
    _print_final(result)


def _prompt_decision(payload: object) -> dict:
    """根据中断 payload 让用户在终端给一个 decision。"""
    print("\n────── 待审批 ──────")
    print(payload)
    print("────────────────────")
    choice = input("决策 [a=approve / r=reject / e=edit]（默认 a）> ").strip().lower() or "a"
    if choice in ("a", "approve"):
        return {"type": "approve"}
    if choice in ("r", "reject"):
        reason = input("拒绝理由（可空）> ").strip()
        return {"type": "reject", "message": reason or "人工拒绝"}
    if choice in ("e", "edit"):
        # HumanInTheLoopMiddleware 的 edit 决策格式：
        #   {"type": "edit", "args": {"action": "...", "args": {...}}}
        # 这里简化为「按 K=V 形式覆盖部分参数」，action 用原工具名。
        raw = input("以空格分隔的 K=V 覆盖参数（如 price=259 inventory=300）> ").strip()
        overrides: dict = {}
        for token in raw.split():
            if "=" in token:
                k, v = token.split("=", 1)
                if v.replace(".", "", 1).isdigit():
                    overrides[k] = float(v) if "." in v else int(v)
                else:
                    overrides[k] = v
        return {"type": "edit", "args": {"action": "create_product", "args": overrides}}
    print(f"未识别的输入 {choice!r}，按 approve 处理。")
    return {"type": "approve"}


def _resume_until_done(
    result: dict,
    config: RunnableConfig,
    *,
    interactive: bool,
    default_decision: dict | None = None,
) -> dict:
    """循环检测 `__interrupt__` 并恢复，直到 supervisor 跑完。

    HumanInTheLoopMiddleware 的 interrupt payload 形如：
        {"action_requests": [...], "review_configs": [...]}
    其中 action_requests 与 review_configs 一一对应，**每个 interrupt 内部**
    含 N 个待审批 tool_call。resume 端 middleware 读取
        decisions = interrupt(hitl_request)["decisions"]
    所以 `Command(resume=...)` 必须是 dict `{"decisions": [...]}`，list 长度
    等于该 interrupt 的 action_requests 数量。
    """
    while True:
        interrupts = result.get("__interrupt__") if isinstance(result, dict) else None
        if not interrupts:
            return result
        # supervisor 一次最多有一个 active interrupt（HITL 中间件聚合处理）
        itr = interrupts[0]
        action_requests = (
            itr.value.get("action_requests", []) if isinstance(itr.value, dict) else []
        )
        if interactive:
            decisions = [_prompt_decision(req) for req in action_requests]
        else:
            assert default_decision is not None
            for req in action_requests:
                print(f"[HITL] 收到审批请求：{req}")
            print(f"[HITL] 自动恢复，决策：{default_decision}")
            decisions = [default_decision for _ in action_requests]
        result = supervisor.invoke(Command(resume={"decisions": decisions}), config=config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Subagents 电商助手端到端 demo")
    parser.add_argument(
        "--demo",
        choices=["simple", "multi", "hitl", "all"],
        default="all",
        help="选择运行哪个 demo（默认 all 会顺序跑 simple → multi → hitl）",
    )
    args = parser.parse_args()

    if args.demo in ("simple", "all"):
        demo_simple()
    if args.demo in ("multi", "all"):
        demo_multi_domain_auto_approve()
    if args.demo in ("hitl", "all"):
        demo_hitl_interactive()
