import json
import re
from typing import Optional
from .config import settings
from .database import get_table_metadata


def build_schema_description(schema: str = "public") -> str:
    """Build a natural-language description of the database schema."""
    tables = get_table_metadata(schema)
    if not tables:
        return f"Schema '{schema}' has no tables."

    current_table = None
    lines = []
    table_descs = {}

    for row in tables:
        tbl = row["table_name"]
        col = row["column_name"]
        dtype = row["data_type"]
        nullable = "NULL" if row["is_nullable"] == "YES" else "NOT NULL"
        pk = " (PK)" if row["is_primary_key"] else ""
        fk = f" → {row['foreign_table']}.{row['foreign_column']}" if row["foreign_table"] else ""

        if tbl != current_table:
            current_table = tbl
            table_descs[tbl] = []
        table_descs[tbl].append(f"  - {col}: {dtype} {nullable}{pk}{fk}")

    for tbl, cols in table_descs.items():
        lines.append(f"Table: {tbl}")
        lines.extend(cols)
        lines.append("")

    return "\n".join(lines)


def generate_sql(user_question: str, schema_description: str, model: str = "gpt-4") -> str:
    """
    Generate a SQL query from a natural language question.
    In production, this calls OpenAI's API. Here we return a template.
    """
    prompt = f"""You are a PostgreSQL expert. Given the schema and user question, generate a SQL query.

Schema:
{schema_description}

Rules:
- Only generate SELECT queries
- Use proper JOINs for foreign key relationships
- Add WHERE conditions for date filters when relevant
- Limit results to {settings.max_rows_returned} rows max
- Use table aliases for clarity

User Question: {user_question}

Respond ONLY with the SQL query, no explanation:"""

    # --- Production: call OpenAI here ---
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model=model, api_key=settings.openai_api_key)
    # response = llm.invoke(prompt)
    # return response.content.strip()

    # Demo fallback: return a placeholder SQL
    return f"-- Generated SQL for: {user_question}\n-- In production, this calls OpenAI's {model} API\nSELECT 'Set OPENAI_API_KEY in .env to enable AI query generation' AS note;"


def parse_chart_type(question: str) -> str:
    """Infer the best chart type from the question keywords."""
    q = question.lower()
    if any(w in q for w in ["trend", "over time", "month", "year", "growth"]):
        return "line"
    if any(w in q for w in ["top", "rank", "largest", "most", "占比", "比例"]):
        return "bar"
    if any(w in q for w in ["distribution", "分布", "range", "区间"]):
        return "histogram"
    return "table"  # default
