import re
from typing import Optional
from .config import settings
from .database import get_table_metadata


def build_schema_description(schema: str = "public") -> str:
    """Build a natural-language description of the database schema."""
    try:
        tables = get_table_metadata(schema)
    except Exception:
        return f"Schema '{schema}' has no tables."

    if not tables:
        return f"Schema '{schema}' has no tables."

    table_descs = {}
    for row in tables:
        tbl = row["table_name"]
        col = row["column_name"]
        dtype = row["data_type"]
        nullable = "NULL" if row["is_nullable"] == "YES" else "NOT NULL"
        pk = " (PK)" if row.get("is_primary_key") else ""
        fk = f" -> {row.get('foreign_table','')}.{row.get('foreign_column','')}" if row.get("foreign_table") else ""

        if tbl not in table_descs:
            table_descs[tbl] = []
        table_descs[tbl].append(f"  - {col}: {dtype} {nullable}{pk}{fk}")

    lines = []
    for tbl, cols in table_descs.items():
        lines.append(f"Table: {tbl}")
        lines.extend(cols)
        lines.append("")
    return "\n".join(lines)


def _get_demo_schema() -> dict:
    """Return demo schema info used when no real DB is available."""
    return {
        "customers": ["id", "name", "email", "region", "signup_date", "tier"],
        "products": ["id", "name", "category", "price", "stock"],
        "orders": ["id", "customer_id", "created_at", "status", "total_amount"],
        "order_items": ["id", "order_id", "product_id", "quantity", "unit_price", "subtotal"],
    }


def _rule_based_sql(question: str, schema_desc: str, schema: str = "public") -> Optional[str]:
    """
    Map common question patterns to SQL without needing an LLM.
    Returns SQL string or None if no pattern matches.
    """
    q = question.lower().strip()

    # Revenue / sales
    if any(k in q for k in ["revenue", "销售额", "sales", "收入", "total amount"]):
        if any(k in q for k in ["month", "月", "monthly", "每个月"]):
            return """
SELECT DATE_TRUNC('month', o.created_at) AS month,
       ROUND(SUM(o.total_amount), 2) AS revenue,
       COUNT(DISTINCT o.id) AS order_count
FROM orders o
WHERE o.status = 'completed'
  AND o.created_at >= NOW() - INTERVAL '3 months'
GROUP BY 1
ORDER BY 1;"""
        if any(k in q for k in ["product", "产品", "top"]):
            return """
SELECT p.name AS product,
       ROUND(SUM(oi.subtotal), 2) AS revenue,
       SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
WHERE o.status = 'completed'
  AND o.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;"""
        return """
SELECT ROUND(SUM(total_amount), 2) AS total_revenue,
       COUNT(*) AS total_orders,
       ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '30 days';"""

    # Customer analysis
    if any(k in q for k in ["customer", "客户", "user"]):
        if any(k in q for k in ["region", "区域", "地理"]):
            return """
SELECT c.region,
       COUNT(DISTINCT c.id) AS customer_count,
       ROUND(SUM(o.total_amount), 2) AS revenue
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
GROUP BY c.region
ORDER BY revenue DESC;"""
        if any(k in q for k in ["tier", "级别", "premium", "vip"]):
            return """
SELECT c.tier,
       COUNT(DISTINCT c.id) AS customers,
       ROUND(SUM(o.total_amount), 2) AS revenue
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
GROUP BY c.tier
ORDER BY revenue DESC;"""
        return """
SELECT c.name, c.email, c.region, c.tier,
       COUNT(o.id) AS order_count,
       ROUND(COALESCE(SUM(o.total_amount), 0), 2) AS lifetime_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
ORDER BY lifetime_value DESC
LIMIT 20;"""

    # Product analysis
    if any(k in q for k in ["product", "产品", "item"]):
        if any(k in q for k in ["category", "分类", "类型"]):
            return """
SELECT p.category,
       COUNT(DISTINCT p.id) AS product_count,
       ROUND(SUM(oi.subtotal), 2) AS revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;"""
        if any(k in q for k in ["stock", "库存"]):
            return """
SELECT name, category, stock, price
FROM products
ORDER BY stock ASC
LIMIT 20;"""
        return """
SELECT p.name, p.category, p.price,
       COUNT(DISTINCT oi.order_id) AS times_ordered,
       SUM(oi.quantity) AS total_sold
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id
ORDER BY total_sold DESC NULLS LAST
LIMIT 20;"""

    # Trend / over time
    if any(k in q for k in ["trend", "趋势", "over time", "增长", "growth"]):
        return """
SELECT DATE_TRUNC('week', created_at) AS week,
       COUNT(*) AS orders,
       ROUND(SUM(total_amount), 2) AS revenue
FROM orders
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '3 months'
GROUP BY 1
ORDER BY 1;"""

    # Comparison / vs / 对比
    if any(k in q for k in ["vs", "compare", "对比", "和", "compared", "yoy", "同比"]):
        return """
SELECT DATE_TRUNC('month', created_at) AS month,
       TO_CHAR(created_at, 'YYYY-MM') AS label,
       ROUND(SUM(total_amount), 2) AS revenue
FROM orders
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '6 months'
GROUP BY 1, 2
ORDER BY 1;"""

    # Count / summary
    if any(k in q for k in ["count", "how many", "多少", "总计", "summary"]):
        if "order" in q or "订单" in q:
            return """
SELECT COUNT(*) AS total_orders,
       COUNT(DISTINCT customer_id) AS unique_customers,
       ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
WHERE status = 'completed';"""
        return """
SELECT 'customers' AS table_name, COUNT(*) AS count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;"""

    return None


def generate_sql(question: str, schema_description: str = "", model: str = "gpt-4") -> str:
    """
    Generate SQL from a natural language question.
    Priority:
      1. LLM (if OPENAI_API_KEY is set)
      2. Rule-based fallback
      3. Demo placeholder
    """
    # --- LLM path ---
    if settings.openai_api_key and not settings.openai_api_key.startswith("sk-demo"):
        try:
            from langchain_openai import ChatOpenAI
            prompt = f"""You are a PostgreSQL expert. Given the schema and user question, generate a SQL query.

Schema:
{schema_description}

Rules:
- Only SELECT queries
- Use JOINs for foreign keys
- WHERE conditions for date filters when relevant
- Max {settings.max_rows_returned} rows
- Use table aliases

User Question: {question}

Respond ONLY with the SQL query, no explanation:"""
            llm = ChatOpenAI(model=model, api_key=settings.openai_api_key, temperature=0)
            response = llm.invoke(prompt)
            sql = response.content.strip()
            # Strip markdown code fences if present
            if sql.startswith("```"):
                sql = sql.strip("`").lstrip("sql").strip()
            return sql
        except Exception as e:
            print(f"[AI Analyst] LLM call failed: {e}, falling back to rules")

    # --- Rule-based fallback ---
    schema_desc = schema_description or build_schema_description()
    sql = _rule_based_sql(question, schema_desc)
    if sql:
        return sql.strip()

    # --- No match ---
    return f"-- No rule matched for: {question}\n-- Try: revenue, top products, customers by region, order summary"


def parse_chart_type(question: str) -> str:
    """Infer the best chart type from the question keywords."""
    q = question.lower()
    if any(w in q for w in ["trend", "over time", "month", "year", "growth", "趋势", "增长", "同比"]):
        return "line"
    if any(w in q for w in ["top", "rank", "largest", "most", "占比", "比例", "产品", "product"]):
        return "bar"
    if any(w in q for w in ["distribution", "分布", "region", "区域", "category", "分类"]):
        return "pie"
    if any(w in q for w in ["compare", "vs", "对比", "comparison"]):
        return "line"
    return "table"
