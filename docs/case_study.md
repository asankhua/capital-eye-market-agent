# AI Market Analyst – Case Study

**Author:** Ashish Kumar Sankhua  
**Date:** April 2026  
**Derived From:** SKILL.md patterns

---

## 1. Executive Summary

AI Market Analyst is an **AI-powered multi-agent system** for Indian stock market analysis. It uses specialized agents (Fundamental, Technical, Sentiment) orchestrated via LangGraph, with a FastAPI backend and React frontend.

**Key Metrics:**
- Development Time: 2 weeks
- Lines of Code: ~6,000 Python + ~3,500 TypeScript
- LLM Provider: Groq (Llama 3.3 70B)
- Data Sources: Yahoo Finance, DuckDuckGo News, Finnhub
- Cache Strategy: SQLite MCP with 24-hour TTL

**Core Features Delivered:**
- ✅ Natural language stock analysis (single, compare, portfolio)
- ✅ Real-time dividend tracking with announcements
- ✅ Market movers (top gainers/losers) in INR
- ✅ Multi-agent parallel processing
- ✅ Two-level caching for performance

---

## 2. Problem Statement

Users needed a way to:
1. Get instant stock analysis without switching between multiple apps
2. Understand fundamental, technical, and sentiment perspectives in one view
3. Query stocks using natural language (no mode selection required)
4. Track dividend announcements for Indian stocks
5. Compare multiple stocks side-by-side

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
- Yahoo Finance tool for stock data
- DuckDuckGo tool for news search
- Finnhub tool for market movers

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

### Phase 4: Backend API (Days 8-10)
- Created FastAPI endpoints
- Implemented `/chat`, `/analyze_stock`, `/compare_stocks`
- Added dividend endpoints `/moneycontrol/dividends` and `/moneycontrol/dividends/all`
- Set up health checks and error handling

### Phase 5: Frontend (Days 11-14)
- Built React + TypeScript + Vite frontend
- Created StockCard components
- Implemented DividendTracker with auto-load feature
- Added MarketMovers with INR currency formatting

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

### Challenge 1: DuckDuckGo Library Compatibility
**Issue:** `__init__() got an unexpected keyword argument 'proxies'`
**Solution:** Modified DDGS instantiation to not pass explicit proxies parameter
```python
# Before: with DDGS(proxies=None) as ddgs:
# After:
ddgs = DDGS()
raw_results = list(ddgs.news(query, max_results=max_results))
```

### Challenge 2: Yahoo Finance Rate Limiting
**Issue:** 429 Client Error: Too Many Requests
**Solution:** Implemented aggressive caching with 24-hour TTL + sample data fallback
```python
# Check cache first
cached = await SQLiteMCPTool.get_cache("dividends", cache_key, max_age_seconds=86400)
if cached:
    return cached

# If Yahoo fails, use sample data
return get_sample_dividend_data(ticker)
```

### Challenge 3: Dividend Data Source
**Issue:** MoneyControl loads data via JavaScript, blocking scrapers
**Solution:** Used Yahoo Finance for real data + sample data fallback for common Indian stocks

### Challenge 4: Frontend Currency
**Issue:** Market Movers showing $ instead of ₹
**Solution:** Updated all price displays in MarketMovers.tsx
```tsx
// Before: ${mover.price?.toFixed(2)}
// After: ₹{mover.price?.toFixed(2)}
```

---

## 7. Testing Strategy

- **All external API calls are mocked** (Groq, Yahoo Finance, DuckDuckGo) — per `docs/rules.md`
- **Backend:** 12 pytest test files covering every layer
- **React:** 3 Vitest test files (integration, API mocking, error handling)
- **FastAPI:** TestClient-based endpoint tests
- **LangGraph:** Full pipeline integration tests with mocked agents

---

## 8. API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze/{ticker}` | Full stock analysis |
| POST | `/compare` | Compare multiple stocks |
| POST | `/portfolio` | Portfolio analysis |
| GET | `/health` | Health check |

### Data Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dividends/{ticker}` | Dividend information |
| GET | `/earnings/{ticker}` | Earnings data |
| GET | `/watchlist` | User watchlist |
| GET | `/finnhub/market_movers` | Top gainers/losers |

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
- **Backend:** Render / Railway / HuggingFace Spaces
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
1. **Dividend Tracker Enhancement** — Added `/moneycontrol/dividends/all` endpoint
2. **Market Movers Fix** — Changed $ to ₹ for Indian market context
3. **LLM Provider Migration** — Removed Gemini, using Groq exclusively
4. **DuckDuckGo Tool Fix** — Fixed DDGS library compatibility
5. **Finnhub Integration** — Replaced MarketStack with Finnhub for dividend data (60 calls/min vs 1,000/month)
6. **News Display Fix** — Fixed Yahoo Finance `get_news()` API change, added sample news fallback
7. **Documentation** — Updated to match SKILL.md patterns
8. **Hugging Face Deployment** — Created GitHub Action, Dockerfile, and HF requirements

---

## 13. Deployment Guide

### Hugging Face Spaces

**Prerequisites:**
- Hugging Face account with Spaces access
- GitHub repository synced to HF

**Setup Steps:**
1. Create HF_TOKEN secret in GitHub repository settings
2. Push to main branch triggers auto-sync to Hugging Face
3. Configure environment variables in HF Spaces settings

**Live Instance:** https://huggingface.co/spaces/ashishsankhua/capital_eye_market_agent

### Environment Variables Required

| Variable | Source | Required | Description |
|----------|--------|----------|-------------|
| `GROQ_API_KEY` | Groq Console | Yes | LLM API access |
| `GROQ_MODEL` | - | No | Defaults to llama-3.3-70b-versatile |
| `FINNHUB_API_KEY` | Finnhub | No | For real market data (has fallbacks) |
| `TWELVE_DATA_API_KEY` | Twelve Data | No | Alternative market data |
| `LOG_LEVEL` | - | No | INFO/DEBUG/ERROR |

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
