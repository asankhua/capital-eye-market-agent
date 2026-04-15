# Capital Eye Market Agent

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6B6B?style=for-the-badge&logo=groq&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3A3A?style=for-the-badge&logo=langchain&logoColor=white)

**AI-powered multi-agent system** for Indian stock market analysis. Uses specialized agents (Fundamental, Technical, Sentiment) orchestrated via LangGraph, with a FastAPI backend and React frontend.

## Who Is This For?

| User | Benefit |
|------|---------|
| **Retail Investors** | Get instant AI-powered analysis without switching between apps |
| **Traders** | Compare stocks, view market movers, track sectors in one place |
| **Finance Students** | Learn fundamental, technical, and sentiment analysis concepts |
| **Financial Advisors** | Quick stock analysis for client recommendations |
| **Business Professionals** | Stay updated on Indian market news without manual research |

## How It Helps

- **Saves Time** - Single query gives fundamental, technical, and sentiment analysis
- **No Expert Required** - AI explains everything in plain language
- **Indian Market Focus** - Built specifically for NSE stocks with INR currency
- **Always Available** - 24/7 AI assistant for stock queries
- **Free to Use** - No subscription required, uses Groq's free tier

## Key Features

### Core Capabilities
- **Natural Language Queries** - Ask "How is Reliance doing?" and get full analysis
- **Multi-Agent Analysis** - Fundamental, Technical, Sentiment agents work in parallel
- **Stock Comparison** - Compare multiple stocks side-by-side
- **Portfolio Analysis** - Analyze your entire stock portfolio

### Market Data
- **Market Movers** - Top gainers/losers in Indian markets (NSE)
- **Market Overview** - Real-time Indian market indices (NIFTY, SENSEX)
- **Sector Analysis** - Performance by sector
- **News Insights** - Latest Indian stock market news

### Technical Features
- **Two-Level Caching** - Intent cache (24h) + Graph cache for performance
- **Fallback Data** - Sample data when APIs fail
- **Error Handling** - Detailed logging with fallback to default scores

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

## Technology Stack

### Backend
- **FastAPI >=0.104.0** - REST API framework
- **Groq (Llama 3.3 70B)** - LLM provider for AI analysis
- **LangGraph** - Multi-agent orchestration
- **SQLite MCP** - Persistent caching layer

### Data Sources
- **Yahoo Finance (yfinance)** - Stock prices, financials, ratios, news
- **NSE India (nsetools)** - Indian market indices & movers
- **Google News RSS** - Market news

### Frontend
- **React 19 + TypeScript** - User interface
- **Vite** - Build tool
- **Framer Motion** - UI animations
- **Lucide React** - Icon library

### External Libraries
- **yfinance** - Yahoo Finance data
- **nsetools** - NSE India data
- **langgraph** - Agent workflow
- **pydantic** - Data validation

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

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │
│  │  ChatPanel  │  │ StockCard   │  │ MarketMovers│  │  MarketOverview│ │
│  │             │  │ +StockChart │  │             │  │                │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph Workflow                           │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐  │   │
│  │  │ Intent    │  │Fundamental│  │ Technical │  │  Sentiment │  │   │
│  │  │ Analyzer  │─▶│  Agent    │  │   Agent   │  │   Agent    │  │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └────────────┘  │   │
│  │       │               │              │              │          │   │
│  │       └───────────────┴──────────────┴──────────────┘          │   │
│  │                              ▼                                  │   │
│  │                    ┌──────────────┐                            │   │
│  │                    │ Master Agent │                            │   │
│  │                    │ (Aggregator) │                            │   │
│  │                    └──────────────┘                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Yahoo Finance│  │ NSE India    │  │Google News  │  │  SQLite   │  │
│  │              │  │ (nsetools)   │  │    RSS      │  │   Cache   │  │
│  │• Price Data  │  │• Market Index│  │• Market News│  │           │  │
│  │• Financials  │  │• Movers      │  │             │  │ 24h TTL   │  │
│  │• News        │  │• Sectors     │  │             │  │           │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **User Query** → Natural language input via React UI
2. **Intent Parsing** → Extract stocks + analysis type
3. **Parallel Agents** → Fundamental, Technical, Sentiment run simultaneously
4. **Aggregation** → Master agent combines results
5. **Response** → Unified analysis with recommendation

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

### Render (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Setup:**
1. Connect your GitHub repo to Render
2. Set environment variables in Render dashboard:
   - `GROQ_API_KEY` - Your Groq API key
   - `API_BASE_URL` - Your Render service URL
   - `REACT_APP_API_URL` - Same as API_BASE_URL
3. Deploy automatically on every push to `main`

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for detailed instructions.

### Docker (Local)
```bash
docker build -t capital-eye .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key capital-eye
```

### Manual Deployment

**Backend:**
```bash
python -m uvicorn backend.api.fastapi_server:app --host 0.0.0.0 --port $PORT
```

**Frontend:**
```bash
cd frontend/react-directory
npm run build
# Deploy dist/ to Vercel/Netlify
```

## Security & Privacy

- **API Keys** - Stored in environment variables, never in code
- **Caching** - Local SQLite database, no external data sharing
- **LLM Processing** - Only stock data sent to Groq, no personal data
- **No Tracking** - No analytics or user data collection

## Browser Compatibility

- **Chrome/Chromium**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Documentation

- [docs/architecture.md](docs/architecture.md) - System architecture and design
- [docs/case_study.md](docs/case_study.md) - Implementation details and lessons learned
- [SKILL.md](SKILL.md) - Project patterns and best practices

---

*Capital Eye Market Agent - AI-powered stock analysis for Indian markets*
