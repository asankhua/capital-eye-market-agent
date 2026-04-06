---
title: Capital Eye Market Agent
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_file: backend/api/fastapi_server.py
pinned: false
---

# AI Market Analyst

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6B6B?style=for-the-badge&logo=groq&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3A3A?style=for-the-badge&logo=langchain&logoColor=white)

**AI-powered multi-agent system** for Indian stock market analysis. Uses specialized agents (Fundamental, Technical, Sentiment) orchestrated via LangGraph, with a FastAPI backend and React frontend.

**Category:** AI/Backend Python Project (Category B per [SKILL.md](SKILL.md))  
**LLM Provider:** Groq (Llama 3.3 70B)  
**Architecture:** Phase-Based Modular (per SKILL.md)

## Quick Start

```bash
# 1. Clone & enter the project
git clone <repo-url>
cd market_analyst-main

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Start backend
python3 -m uvicorn backend.api.fastapi_server:app --host 0.0.0.0 --port 8000

# 6. Start frontend (new terminal)
cd frontend/react-directory
npm install
npm run dev
```

## Features

- **Natural Language Queries** — Ask questions like "How is Reliance doing?"
- **Multi-Agent Analysis** — Fundamental, Technical, Sentiment agents work in parallel
- **Stock Comparison** — Compare multiple stocks side-by-side
- **Dividend Tracker** — Real-time dividend announcements and history
- **Market Movers** — Top gainers/losers in Indian markets
- **Portfolio Analysis** — Analyze your stock portfolio

## Technology Stack

### Backend (Category B: FastAPI + LLM)
- **FastAPI** ≥0.104.0 — REST API framework
- **Groq** (Llama 3.3 70B) — LLM provider
- **yfinance** — Yahoo Finance data
- **LangGraph** — Agent orchestration
- **SQLite MCP** — Persistent caching

### Frontend (React 19 + TypeScript + Vite)
- **React 19** + **TypeScript**
- **Vite** — Build tool
- **Framer Motion** — Animations
- **Lucide React** — Icons

## Project Structure

Following [SKILL.md](SKILL.md) Phase-Based Modular Architecture:

```
market_analyst-main/
├── backend/
│   ├── api/              # Phase 4: FastAPI endpoints
│   ├── agents/           # Phase 3: LLM agents (Groq)
│   ├── tools/            # Phase 1-2: Data acquisition
│   ├── workflows/        # Phase 3: LangGraph
│   ├── models/           # Pydantic schemas
│   └── config.py         # Configuration
├── frontend/
│   └── react-directory/  # Phase 5: React + Vite UI
├── tests/                # pytest tests
├── docs/
│   ├── architecture.md   # System design
│   └── case_study.md     # Implementation details
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Full analysis pipeline |
| POST | `/analyze_stock/{ticker}` | Single stock analysis |
| POST | `/compare_stocks` | Compare multiple stocks |
| GET | `/moneycontrol/dividends` | Dividend information |
| GET | `/moneycontrol/dividends/all` | All recent dividends |
| GET | `/finnhub/market_movers` | Top gainers/losers |
| GET | `/health` | Health check |

## Configuration

Create `.env` file:
```bash
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq
API_BASE_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000
LOG_LEVEL=INFO
```

## Deployment

### Hugging Face Spaces (Recommended)

The project is configured for automatic deployment to Hugging Face Spaces via GitHub Actions.

**Live Instance:** https://huggingface.co/spaces/ashishsankhua/capital_eye_market_agent

**Setup:**
1. Add `HF_TOKEN` secret in your GitHub repository settings (get from https://huggingface.co/settings/tokens)
2. Push to `main` branch - GitHub Action auto-syncs to Hugging Face
3. Configure environment variables in Hugging Face Spaces settings

**Local Docker Test:**
```bash
docker build -t capital-eye .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key capital-eye
```

### Manual Deployment

**Backend (Render/Railway/Heroku):**
- Set environment variables
- Start command: `python -m uvicorn backend.api.fastapi_server:app --host 0.0.0.0 --port $PORT`

**Frontend (Vercel/Netlify):**
- Build command: `cd frontend/react-directory && npm run build`
- Output directory: `frontend/react-directory/dist`
- Set `REACT_APP_API_URL` to your backend URL

## Documentation

- [docs/architecture.md](docs/architecture.md) — System architecture and design
- [docs/case_study.md](docs/case_study.md) — Implementation details and lessons learned
- [SKILL.md](SKILL.md) — Project patterns and best practices

## License

MIT
