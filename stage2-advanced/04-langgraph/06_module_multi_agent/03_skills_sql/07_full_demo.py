"""Skills — 完整 demo：端到端可运行的 SQL 助手（渐进式技能加载）

把 01~06 各步骤串成一个可独立运行的脚本：

  Step 1  Skill TypedDict                       (对应 01_skill_struct.py)
  Step 2  SKILLS 列表（销售 / 库存 两套 schema）  (对应 02_skills_definitions.py)
  Step 3  load_skill 工具                        (对应 03_load_skill_tool.py)
  Step 4  SkillMiddleware：把技能目录注入系统提示  (对应 04_skill_middleware.py)
  Step 5  组装 agent                            (对应 05_create_agent.py)
  Step 6  跑示例 query 验证 load_skill 真的被调用 (对应 06_run_demo.py)

核心 idea —— "渐进式披露 (progressive disclosure)"：
  把所有 schema 全塞进 system prompt 会让 token 暴涨且分散注意力；
  把它们做成"技能目录"，只在 prompt 里列出名字+一句话描述，
  让 LLM 自己判断该不该 load_skill(name) 把完整内容拉进来。

运行：
    uv run python stage2-advanced/04-langgraph/06_module_multi_agent/03_skills_sql/07_full_demo.py
    uv run python .../07_full_demo.py --demo sales       # 销售 schema 单查询
    uv run python .../07_full_demo.py --demo inventory   # 库存 schema 单查询
    uv run python .../07_full_demo.py --demo all         # 顺序跑两个
"""

import pathlib
import sys
import uuid
from typing import Callable, TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402


# ============================================================
# Step 1：Skill 结构
# ============================================================
class Skill(TypedDict):
    """渐进式披露的技能项。

    - description: 进系统提示（让 LLM 知道存在），保持简短
    - content:     真正的大段内容，按需通过 load_skill 工具加载
    """

    name: str
    description: str
    content: str


# ============================================================
# Step 2：业务技能（销售分析 + 库存管理）
# ============================================================
SKILLS: list[Skill] = [
    {
        "name": "sales_analytics",
        "description": "销售数据分析的数据库 schema 和业务逻辑，包括客户、订单和收入。",
        "content": """# 销售分析 Schema

## 表结构

### customers (客户表)
- customer_id (主键)
- name (客户名称)
- email
- signup_date (注册日期)
- status (active/inactive)
- customer_tier (客户等级: bronze/silver/gold/platinum)

### orders (订单表)
- order_id (主键)
- customer_id (外键 -> customers)
- order_date (订单日期)
- status (订单状态: pending/completed/cancelled/refunded)
- total_amount (订单总金额)
- sales_region (销售区域: north/south/east/west)

### order_items (订单明细表)
- item_id (主键)
- order_id (外键 -> orders)
- product_id (产品ID)
- quantity (数量)
- unit_price (单价)
- discount_percent (折扣百分比)

## 业务规则

**活跃客户定义**：
status = 'active' AND signup_date <= CURRENT_DATE - INTERVAL '90 days'

**收入计算规则**：
只计算 status = 'completed' 的订单。使用 orders 表的 total_amount 字段（已包含折扣）。

**客户生命周期价值 (CLV)**：
客户所有已完成订单的 total_amount 总和。

**高价值订单定义**：
total_amount > 1000 的订单。

## 示例查询
```sql
-- 查询最近一季度收入前10的客户
SELECT
    c.customer_id,
    c.name,
    c.customer_tier,
    SUM(o.total_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND o.order_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY c.customer_id, c.name, c.customer_tier
ORDER BY total_revenue DESC
LIMIT 10;
```

**重要注意事项**：
- 始终在 WHERE 子句中包含 status = 'completed'
- 使用 INTERVAL 而不是固定日期
- 金额字段已包含税费和折扣
""",
    },
    {
        "name": "inventory_management",
        "description": "库存追踪的数据库 schema 和业务逻辑，包括产品、仓库和库存水平。",
        "content": """# 库存管理 Schema

## 表结构

### products (产品表)
- product_id (主键)
- product_name (产品名称)
- sku (库存单位)
- category (类别)
- unit_cost (单位成本)
- reorder_point (补货点：最低库存警戒线)
- discontinued (是否停产: boolean)

### warehouses (仓库表)
- warehouse_id (主键)
- warehouse_name (仓库名称)
- location (位置)
- capacity (容量)

### inventory (库存表)
- inventory_id (主键)
- product_id (外键 -> products)
- warehouse_id (外键 -> warehouses)
- quantity_on_hand (现有库存数量)
- last_updated (最后更新时间)

### stock_movements (库存流动表)
- movement_id (主键)
- product_id (外键 -> products)
- warehouse_id (外键 -> warehouses)
- movement_type (流动类型: inbound/outbound/transfer/adjustment)
- quantity (数量：入库为正，出库为负)
- movement_date (流动日期)
- reference_number (参考号)

## 业务规则

**可用库存定义**：
inventory 表中 quantity_on_hand > 0 的库存。

**需要补货的产品**：
所有仓库的 quantity_on_hand 总和 <= 产品的 reorder_point。

**活跃产品规则**：
排除 discontinued = true 的产品（除非专门分析停产商品）。

**库存估值计算**：
quantity_on_hand * unit_cost

## 示例查询
```sql
-- 查找需要补货的产品
SELECT
    p.product_id,
    p.product_name,
    p.reorder_point,
    SUM(i.quantity_on_hand) as total_stock,
    p.unit_cost,
    (p.reorder_point - SUM(i.quantity_on_hand)) as units_to_reorder
FROM products p
JOIN inventory i ON p.product_id = i.product_id
WHERE p.discontinued = false
GROUP BY p.product_id, p.product_name, p.reorder_point, p.unit_cost
HAVING SUM(i.quantity_on_hand) <= p.reorder_point
ORDER BY units_to_reorder DESC;
```

**重要注意事项**：
- 始终使用 SUM(quantity_on_hand) 跨所有仓库汇总
- 默认排除停产产品
- 负数 quantity 表示出库
""",
    },
]


# ============================================================
# Step 3：load_skill 工具
# ============================================================
@tool
def load_skill(skill_name: str) -> str:
    """加载技能的完整内容到 Agent 上下文中。

    当你需要某个领域的详细 schema/业务规则时调用此工具。

    Args:
        skill_name: 要加载的技能名称（如 "sales_analytics"、"inventory_management"）
    """
    for skill in SKILLS:
        if skill["name"] == skill_name:
            return f"✅ 已加载技能：{skill_name}\n\n{skill['content']}"
    available = ", ".join(s["name"] for s in SKILLS)
    return f"❌ 技能 '{skill_name}' 未找到。可用技能：{available}"


# ============================================================
# Step 4：SkillMiddleware — 把技能目录注入 system prompt
# ============================================================
class SkillMiddleware(AgentMiddleware):
    """每次模型调用前，往 system message 末尾追加可用技能列表。

    关键点：
    - `tools = [load_skill]` 让 middleware 自带工具注册到 agent，
      不需要外层 create_agent 再列一次
    - 用 content_blocks 拼接保留原系统提示，不破坏 agent 自带的人格
    """

    tools = [load_skill]

    def __init__(self) -> None:
        super().__init__()
        self.skills_prompt = "\n".join(f"- **{s['name']}**: {s['description']}" for s in SKILLS)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        skills_addendum = (
            f"\n\n## 可用技能\n\n{self.skills_prompt}\n\n"
            "当你需要处理特定类型请求的详细信息时，使用 load_skill 工具。"
        )

        # 把现有 system prompt 的纯文本拼上技能目录。直接用 .text 取扁平字符串，
        # 比 content_blocks 拼 dict 更省事，类型也更干净。
        original_text = request.system_message.text if request.system_message else ""
        new_system_message = SystemMessage(content=(original_text + skills_addendum).strip())
        return handler(request.override(system_message=new_system_message))


# ============================================================
# Step 5：组装 agent
# ============================================================
agent = create_agent(
    get_chat_model("qwen-max"),
    system_prompt="你是一个 SQL 查询助手，帮助用户编写业务数据库查询。",
    middleware=[SkillMiddleware()],
    checkpointer=InMemorySaver(),
)


# ============================================================
# Step 6：演示
# ============================================================
def _new_config() -> RunnableConfig:
    return {"configurable": {"thread_id": f"sql_{uuid.uuid4().hex[:8]}"}}


def _run_query(query: str, label: str) -> None:
    print(f"\n########## {label} ##########")
    print(f"用户 > {query}\n")
    result = agent.invoke({"messages": [{"role": "user", "content": query}]}, _new_config())

    # 把整段对话依次打印出来：能直接看到 LLM 是否调了 load_skill、调了哪个
    for msg in result["messages"]:
        role = type(msg).__name__
        text = getattr(msg, "content", "")
        # 工具调用单独高亮
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                print(f"[{role}] 🔧 调用工具: {tc['name']}({tc.get('args', {})})")
            if text:
                print(f"[{role}] {text}")
        else:
            preview = text if isinstance(text, str) else str(text)
            if len(preview) > 600:
                preview = preview[:600] + "...(截断)"
            print(f"[{role}] {preview}")


def demo_sales() -> None:
    _run_query(
        "写一个 SQL 查询，找出上个月订单金额超过 1000 美元的所有客户。",
        "Demo: 销售分析（期望 load_skill('sales_analytics')）",
    )


def demo_inventory() -> None:
    _run_query(
        "帮我写一条 SQL，列出所有库存低于补货点、且没有停产的产品。",
        "Demo: 库存管理（期望 load_skill('inventory_management')）",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Skills SQL 助手端到端 demo")
    parser.add_argument(
        "--demo",
        choices=["sales", "inventory", "all"],
        default="all",
        help="选择跑哪个 demo（默认 all）",
    )
    args = parser.parse_args()
    if args.demo in ("sales", "all"):
        demo_sales()
    if args.demo in ("inventory", "all"):
        demo_inventory()
