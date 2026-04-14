from fastapi import APIRouter
from core.database import get_table_metadata
from core.config import settings

router = APIRouter(prefix="/api/schema", tags=["schema"])


@router.get("/tables")
async def list_tables(schema: str = "public"):
    if schema not in settings.allowed_schemas:
        return {"error": f"Schema '{schema}' is not allowed"}
    try:
        tables = get_table_metadata(schema)
        return {"schema": schema, "tables": tables}
    except Exception as e:
        return {"error": str(e)}
