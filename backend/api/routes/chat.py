from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from core.database import execute_readonly_query
from core.sql_generator import generate_sql, build_schema_description, parse_chart_type
from core.config import settings

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    schema: str = "public"
    model: Optional[str] = None


class ChatResponse(BaseModel):
    question: str
    generated_sql: str
    chart_type: str
    data: dict
    explanation: Optional[str] = None


def _build_explanation(question: str, sql: str, chart_type: str, row_count: int) -> str:
    """Generate a natural-language explanation of the query result."""
    q = question.lower()

    if any(k in q for k in ["revenue", "销售额", "sales", "收入"]):
        return f"查询返回 {row_count} 条结果。根据 SQL，生成了按时间/产品维度的收入统计。"
    if any(k in q for k in ["customer", "客户"]):
        return f"共 {row_count} 条客户记录，展示了客户活跃度和消费情况。"
    if any(k in q for k in ["product", "产品"]):
        return f"查询了 {row_count} 条产品数据，按销量或收入排序。"
    if any(k in q for k in ["count", "多少", "总计"]):
        return f"统计结果：{row_count} 条匹配记录。"
    if any(k in q for k in ["trend", "趋势", "增长"]):
        return f"时间趋势分析，共 {row_count} 个数据点。"
    if any(k in q for k in ["vs", "对比", "compare", "同比"]):
        return f"对比分析，{row_count} 个时间段的数据。"
    if "explain" in q or "schema" in q or "结构" in q:
        return f"数据库结构查询，返回 {row_count} 条表结构信息。"
    return f"查询返回 {row_count} 条结果。图表类型：{chart_type}。"


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Step 1: Build schema description
    try:
        schema_desc = build_schema_description(req.schema)
    except Exception:
        schema_desc = ""

    # Step 2: Generate SQL (LLM or rule-based fallback)
    generated_sql = generate_sql(req.question, schema_desc, req.model or settings.default_model)

    # Step 3: Execute the query
    try:
        data = execute_readonly_query(generated_sql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")

    # Step 4: Infer chart type
    chart_type = parse_chart_type(req.question)

    # Step 5: Generate explanation
    explanation = _build_explanation(req.question, generated_sql, chart_type, data.get("row_count", 0))

    return ChatResponse(
        question=req.question,
        generated_sql=generated_sql,
        chart_type=chart_type,
        data=data,
        explanation=explanation,
    )


@router.get("/schemas")
async def list_schemas():
    return {"schemas": settings.allowed_schemas}
