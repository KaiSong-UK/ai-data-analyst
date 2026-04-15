# AI Data Analyst

**Chat with Your Data — Natural Language → SQL → Insights**

Ask questions in plain English and get answers with charts. No SQL knowledge required.

## Quick Start

```bash
git clone https://github.com/KaiSong-UK/ai-data-analyst.git
cd ai-data-analyst
docker compose up --build
```

Open http://localhost:3000

> Demo runs out-of-the-box with rule-based SQL generation (no API key required).
> Set `OPENAI_API_KEY` in `backend/.env` to enable GPT-4 for smarter queries.

## Example Questions

```
What were our monthly sales?
Show me top 10 products by revenue
How many customers by region?
What's the revenue trend over time?
Compare this month vs last month
```

## Architecture

```
Browser → React (port 3000) → FastAPI (port 8000) → PostgreSQL
                                 ↓
                         Rule Engine / LLM
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, ECharts |
| Backend | FastAPI, SQLAlchemy |
| AI | Rule Engine + OpenAI GPT-4 (optional) |
| Database | PostgreSQL (user data) |

## Local Development

```bash
# Backend
cd backend
cp .env.example .env        # edit DATABASE_URL
pip install -r requirements.txt
python seed_data.py          # load demo e-commerce data
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Features

- 🗣️ **Natural Language to SQL** — Rule-based + LLM fallback
- 📊 **Auto Chart Generation** — line / bar / pie / table
- 🧠 **Schema Awareness** — introspects your DB structure
- 💬 **Conversational** — context-aware follow-up questions
- 🔒 **Read-only** — SQL injection protection, SELECT-only enforced

## License

MIT
