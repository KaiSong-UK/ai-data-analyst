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


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY in backend/.env",
        )

    model = req.model or settings.default_model

    # Step 1: Build schema description
    schema_desc = build_schema_description(req.schema)

    # Step 2: Generate SQL from natural language
    generated_sql = generate_sql(req.question, schema_desc, model)

    # Step 3: Execute the query
    try:
        data = execute_readonly_query(generated_sql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")

    # Step 4: Infer chart type
    chart_type = parse_chart_type(req.question)

    return ChatResponse(
        question=req.question,
        generated_sql=generated_sql,
        chart_type=chart_type,
        data=data,
    )


@router.get("/schemas")
async def list_schemas():
    return {"schemas": settings.allowed_schemas}
