"""Skills — Step 2：定义业务技能（销售分析 + 库存管理 schema）

对应课程章节：模块六 / 四 / Step 2
"""
# from .01_skill_struct import Skill

SKILLS: list["Skill"] = [        # noqa: F821
    {
        "name": "sales_analytics",
        "description": "销售数据分析的数据库schema和业务逻辑，包括客户、订单和收入。",
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
        "description": "库存追踪的数据库schema和业务逻辑，包括产品、仓库和库存水平。",
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
