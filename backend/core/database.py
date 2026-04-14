from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from .config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    execution_options={"statement_timeout": settings.query_timeout_seconds * 1000},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_table_metadata(schema: str) -> list[dict]:
    """Fetch table and column metadata for a given schema."""
    with get_db_session() as session:
        result = session.execute(
            text("""
                SELECT
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    CASE WHEN pk.column_name IS NOT NULL THEN TRUE ELSE FALSE END AS is_primary_key,
                    fk.foreign_table,
                    fk.foreign_column
                FROM information_schema.tables t
                JOIN information_schema.columns c
                    ON t.table_name = c.table_name AND t.table_schema = c.table_schema
                LEFT JOIN (
                    SELECT ku.table_name, ku.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage ku
                        ON tc.constraint_name = ku.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                ) pk ON t.table_name = pk.table_name AND c.column_name = pk.column_name
                LEFT JOIN (
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table,
                        ccu.column_name AS foreign_column
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                ) fk ON t.table_name = fk.table_name AND c.column_name = fk.column_name
                WHERE t.table_schema = :schema AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position
            """),
            {"schema": schema},
        )
        return [dict(row._mapping) for row in result]


def execute_readonly_query(query: str, params: dict | None = None) -> dict:
    """Execute a read-only query and return results."""
    # Security: validate query is SELECT only
    normalized = query.strip().upper()
    if not normalized.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")

    disallowed = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"]
    if any(kw in normalized for kw in disallowed):
        raise ValueError("Query contains disallowed keywords")

    with get_db_session() as session:
        result = session.execute(text(query), params or {})
        rows = result.fetchmany(settings.max_rows_returned)
        columns = list(result.keys())
        return {
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows],
            "row_count": len(rows),
        }
