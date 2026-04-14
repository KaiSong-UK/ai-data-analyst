from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, schema
from core.config import settings

app = FastAPI(
    title="AI Data Analyst",
    version="1.0.0",
    description="Chat with your database using natural language",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(schema.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
