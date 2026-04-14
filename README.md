<div align="center">

# 🤖 AI Data Analyst

### Chat with Your Data — Natural Language → SQL → Insights

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/KaiSong-UK/ai-data-analyst?style=social)](https://github.com/KaiSong-UK/ai-data-analyst)

**Ask questions in plain English → Get answers with charts**

</div>

---

## ✨ Features

- 🗣️ **Natural Language to SQL** — Ask "What were our top 10 products last month?" and get results
- 📊 **Auto Chart Generation** — Automatically picks the best visualization for your query
- 🧠 **Schema Awareness** — Understands your database structure and relationships
- 💬 **Conversational** — Follow-up questions, drill-down, and context-aware responses
- 🔒 **Secure** — Read-only database access, query validation, no data leakage
- 📱 **Modern UI** — Clean chat interface with embedded charts

## 🚀 Quick Start

```bash
git clone https://github.com/KaiSong-UK/ai-data-analyst.git
cd ai-data-analyst

# Configure
cp .env.example .env
# Edit .env with your database URL and OpenAI API key

# Start
docker compose up -d

# Open
open http://localhost:3000
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, ECharts |
| Backend | FastAPI, LangChain, SQLAlchemy |
| AI | OpenAI GPT-4 / Claude, Embedding-based schema search |
| Database | PostgreSQL (metadata), Your DB (data) |

## 💬 Example Conversations

```
👤 You: 上个月销售额是多少？
🤖 AI: 2026年3月总销售额为 ¥2,847,630，环比增长 12.3%
      [📊 柱状图: 月度销售额趋势]

👤 You: 哪些产品贡献最大？
🤖 AI: Top 5 产品：
      1. 产品A — ¥523,400 (18.4%)
      2. 产品B — ¥412,800 (14.5%)
      3. 产品C — ¥389,200 (13.7%)
      [🥧 饼图: 产品销售占比]

👤 You: 和去年同期比呢？
🤖 AI: 同比增长 23.1%，主要增长来自产品A（+45.2%）和产品B（+31.8%）
      [📈 折线图: 同比对比]
```

## 📄 License

MIT
