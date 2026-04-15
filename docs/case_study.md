# AI Market Analyst – Case Study

**Author:** Ashish Kumar Sankhua | Product Manager  
**Date:** April 2026 | **Status:** Production Ready

---

## 1. Executive Summary

AI Market Analyst is an **AI-powered multi-agent system** for Indian stock market analysis. It uses specialized agents (Fundamental, Technical, Sentiment) orchestrated via LangGraph, with a FastAPI backend and React frontend.

**Key Metrics:**
- Development Time: 2 weeks
- Lines of Code: ~6,000 Python + ~3,500 TypeScript
- LLM Provider: Groq (Llama 3.3 70B)
- Data Sources: Yahoo Finance, NSE India, Google News RSS
- Cache Strategy: SQLite MCP with 24-hour TTL

**Core Features Delivered:**
- Natural language stock analysis (single, compare, portfolio)
- Market movers (top gainers/losers) in INR
- Multi-agent parallel processing
- Two-level caching for performance
- Render deployment with auto-deploy on git push

---

## 2. Problem Statement

Users needed a way to:
1. Get instant stock analysis without switching between multiple apps
2. Understand fundamental, technical, and sentiment perspectives in one view
3. Query stocks using natural language (no mode selection required)
4. View real-time Indian market data (NSE indices, movers, sectors)
5. Compare multiple stocks side-by-side
6. Stay updated with latest Indian stock market news

---

## 3. Solution Architecture

Following SKILL.md Phase-Based Modular Architecture:

```
market_analyst_main/
├── backend/
│   ├── api/              # Phase 4: Delivery layer
│   ├── agents/           # Phase 3: AI processing
│   ├── tools/            # Phase 1-2: Data acquisition
│   ├── workflows/        # Phase 3: Orchestration
│   ├── models/           # Shared data contracts
│   └── config.py         # Configuration
├── frontend/
│   └── react-directory/  # Phase 5: UI layer
├── tests/                # Integration tests
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── .env                  # Environment variables
├── requirements.txt
└── README.md
```

---

## 4. Implementation Phases

### Phase 1: Data Acquisition
- Yahoo Finance tool for stock data, financials, ratios, and news
- NSE India tool (nsetools) for market data
- Google News RSS for market news

### Phase 2: Processing & Caching
- SQLite MCP cache layer
- Rate limiting (1s between requests)
- 24-hour TTL for intent cache

### Phase 3: AI Layer
- Intent Analyzer (extracts ticker + analysis type)
- Fundamental Agent (financial analysis)
- Technical Agent (price indicators)
- Sentiment Agent (news sentiment)
- Master Agent (aggregator)

### Phase 4: Backend API
- Created FastAPI endpoints
- Implemented `/chat`, `/analyze_stock`, `/compare_stocks`, `/portfolio_analysis`
- Added NSE endpoints for market data
- Added Indian news endpoint
- Set up health checks and error handling

### Phase 5: Frontend
- Built React + TypeScript + Vite frontend
- Created StockCard with StockChart components
- Implemented MarketMovers with INR currency formatting
- Added MarketOverview, SectorAnalysis, NewsInsights views

---

## 5. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Groq LLM only** | Fast inference (~0.3s), free tier available |
| **SQLite caching** | No external database needed, persistent cache |
| **Phase-based structure** | Each phase independent and testable |
| **Agent pattern** | Specialized agents for different perspectives |
| **Unified query interface** | No mode switching required |
| **INR Currency** | Indian market focus (₹ instead of $) |

---

## 6. Challenges & Solutions

### Challenge 1: Yahoo Finance Rate Limiting
**Issue:** 429 Client Error: Too Many Requests
**Solution:** Implemented aggressive caching with 1-hour TTL + sample data fallback
```python
# Check cache first
cached = await SQLiteMCPTool.get_cache("yahoo_finance", cache_key, max_age_seconds=3600)
if cached:
    return cached

# If Yahoo fails, use sample data
return get_sample_data(ticker)
```

### Challenge 2: News Data Source Migration
**Issue:** DuckDuckGo library had compatibility issues with proxies parameter
**Solution:** Migrated to Yahoo Finance `get_news()` API for stock-specific news
- Added sample news data for 7 major Indian stocks as fallback

### Challenge 3: Dividend Data Unavailable
**Issue:** No reliable free API for Indian dividend data (BSE India API issues)
**Solution:** Temporarily disabled dividend feature - endpoints return 410 Gone
- Can be re-enabled when reliable data source is found

### Challenge 4: Frontend Currency
**Issue:** Market Movers showing $ instead of ₹
**Solution:** Updated all price displays in MarketMovers.tsx
```tsx
// Before: ${mover.price?.toFixed(2)}
// After: ₹{mover.price?.toFixed(2)}
```

### Challenge 5: LLM Analysis Failures
**Issue:** "LLM analysis failed" messages appearing in analysis results
**Solution:** Added detailed error logging with tracebacks in:
- `backend/llm_provider.py` - logs GROQ_API_KEY status
- All agent files - logs specific failure points
- Fallback: All agents return score 5.0 with raw data when LLM fails

---

## 7. Testing Strategy

- **All external API calls are mocked** (Groq, Yahoo Finance, NSE) — per `docs/rules.md`
- **Backend:** 12 pytest test files covering every layer
- **React:** 3 Vitest test files (integration, API mocking, error handling)
- **FastAPI:** TestClient-based endpoint tests
- **LangGraph:** Full pipeline integration tests with mocked agents

---

## 8. API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Full analysis pipeline (natural language) |
| POST | `/analyze_stock` | Single stock analysis |
| POST | `/compare_stocks` | Compare multiple stocks |
| POST | `/portfolio_analysis` | Portfolio analysis |
| POST | `/parse_intent` | Extract stocks + intent from query |
| GET | `/health` | Health check |

### Market Data Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/nse/market_movers` | Top gainers/losers |
| GET | `/nse/market_overview` | Market indices (NIFTY, SENSEX) |
| GET | `/nse/sector_performance` | Sector performance |
| GET | `/indian_news/market` | Market news |

---

## 9. Configuration

```bash
# LLM Configuration
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq

# API URLs
API_BASE_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=dump.log
```

---

## 10. Deployment

### Local Development
```bash
# Backend
python3 -m uvicorn backend.api.fastapi_server:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend/react-directory && npm run dev
```

### Production (per SKILL.md patterns)
- **Backend:** Render / Railway
- **Frontend:** Vercel / Netlify
- **Database:** SQLite (file-based, no external DB needed)

---

## 11. Lessons Learned

1. **LLM Provider Selection** → Groq provides fastest inference for this use case
2. **Caching is Critical** → Yahoo Finance rate limits require aggressive caching
3. **Phase-Based Structure** → Makes debugging and testing much easier
4. **Unified Interface** → Users prefer single query box over mode selection
5. **Fallback Data** → Always have sample data for when APIs fail

---

## 12. Recent Implementation Changes

### April 2026 Updates

#### 12.1 Dividend Tracker Changes
- **Status:** Dividend functionality temporarily disabled
- **Removed:** `/nse/dividends` and `/dividends/announcements` endpoints (return 410 Gone)
- **Reason:** No reliable free API for Indian dividend data (BSE India API integration issues)
- **Previous:** Was using Finnhub + sample data fallback

#### 12.2 Dashboard UI Updates
- **Removed:** "Latest News" section from Dashboard (per user request)
- **Added:** StockChart component to StockCard for price visualization
- **Components:** NewsSection still available but not displayed in Dashboard

#### 12.3 LLM Analysis Debugging
- **Issue:** "LLM analysis failed" messages in Fundamental, Technical, Sentiment
- **Debug Added:** Detailed error logging with tracebacks in:
  - `backend/llm_provider.py` - logs GROQ_API_KEY status
  - `backend/agents/fundamental_agent.py` - logs LLM failures
  - `backend/agents/technical_agent.py` - logs technical analysis failures
  - `backend/agents/sentiment_agent.py` - logs sentiment analysis failures
- **Fallback:** All agents return score 5.0 with raw data when LLM fails

#### 12.4 News Data Source Migration
- **Changed:** From DuckDuckGo to Yahoo Finance `get_news()` API
- **File:** `backend/tools/yahoo_finance_tool.py` - news fetching with rate limiting
- **Fallback:** Sample news data for major Indian stocks when API fails

#### 12.5 Market Data Tools (Current)
- **NSE Market Tool:** `backend/tools/nse_market_tool.py` - Indian market data from nsetools
- **Indian News Tool:** `backend/tools/indian_stock_news_tool.py` - Google News RSS feed
- **Yahoo Finance Tool:** `backend/tools/yahoo_finance_tool.py` - Primary stock data
- **SQLite Cache:** `backend/tools/sqlite_mcp_tool.py` - Caching layer (used by all tools)

#### 12.6 Frontend Components (Current)
- **Active:** Header, Footer, Sidebar, ChatPanel, MarketOverview, MarketMovers, NewsInsights, SectorAnalysis, SettingsPage, StockCard, StockChart, DebugPanel, NewsSection
- **Removed:** DividendTracker, FeaturesPanel, Watchlist (not used in current UI)

#### 12.7 Render Deployment
- **Blueprint:** `render.yaml` for auto-configuration
- **Start Script:** `render_start.sh` for server startup
- **Config:** Environment variables for `GROQ_API_KEY`, `API_BASE_URL`

---

## 13. Deployment Guide

### Render (Recommended)

**Prerequisites:**
- Render account (free tier available)
- GitHub repository connected to Render

**Setup Steps:**
1. Connect GitHub repo to Render
2. Set environment variables in Render dashboard:
   - `GROQ_API_KEY` - Your Groq API key
   - `API_BASE_URL` - Your Render service URL
   - `REACT_APP_API_URL` - Same as API_BASE_URL
3. Push to main branch triggers auto-deploy

See [RENDER_DEPLOY.md](../RENDER_DEPLOY.md) for detailed instructions.

### Environment Variables Required

| Variable | Source | Required | Description |
|----------|--------|----------|-------------|
| `GROQ_API_KEY` | Groq Console | Yes | LLM API access (Llama 3.3 70B) |
| `GROQ_MODEL` | - | No | Defaults to llama-3.3-70b-versatile |
| `LOG_LEVEL` | - | No | INFO/DEBUG/ERROR |
| `LOG_FILE` | - | No | Defaults to dump.log |

---

## 14. Future Enhancements

- [ ] Vector database for news memory (ChromaDB)
- [ ] LLM reasoning chains
- [ ] Event-driven updates (real-time market triggers)
- [ ] Portfolio risk modeling
- [ ] Backtesting engine
- [ ] Playwright-based MoneyControl scraper for true real-time data

---

## 14. References

- **SKILL.md** → Project patterns and best practices
- **docs/architecture.md** → Full system design
- **README.md** → Quick start and setup
