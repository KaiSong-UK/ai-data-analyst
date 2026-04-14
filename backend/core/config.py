from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/your_database"

    # AI
    openai_api_key: str = ""
    default_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # Security
    secret_key: str = "change-me"
    allowed_schemas: list[str] = ["public"]
    query_timeout_seconds: int = 30
    max_rows_returned: int = 1000

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
