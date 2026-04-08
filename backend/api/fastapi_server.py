"""
FastAPI Backend – API Gateway for the AI Market Analyst.

Provides REST endpoints for stock analysis, comparison, portfolio review,
and free-form chat. Wires into the LangGraph orchestration layer.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from backend.config import logger as root_logger
from backend.models.schemas import (
    AnalysisResponse,
    AnalysisType,
    AnalyzeStockRequest,
    ChatRequest,
    CompareStocksRequest,
    ErrorResponse,
    ExportRequest,
    FundamentalAnalysis,
    HistoricalAnalysisResponse,
    IntentResponse,
    NewsArticle,
    PortfolioRequest,
    Recommendation,
    SentimentAnalysis,
    StockAnalysis,
    TechnicalAnalysis,
    WatchlistItem,
)
from backend.workflows.market_graph import (
    parse_intent_cached,
    run_analysis,
    run_compare_stocks,
    run_portfolio_analysis,
    run_single_stock_analysis,
)
from backend.tools.yahoo_finance_tool import YahooFinanceTool
from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.api.server")


# ── Lifespan ──────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI server starting up")
    await SQLiteMCPTool.initialize()
    yield
    await SQLiteMCPTool.shutdown()
    logger.info("FastAPI server shutting down")


# ── App Setup ─────────────────────────────────────────────────────


app = FastAPI(
    title="AI Market Analyst",
    description="Multi-agent AI system for stock market analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS – allow Streamlit and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (React Frontend) ───────────────────────────────

# Check if frontend dist exists (production/Docker)
FRONTEND_DIST = "/app/frontend/dist"
if os.path.exists(FRONTEND_DIST):
    logger.info("Serving React frontend from %s", FRONTEND_DIST)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
else:
    logger.info("Frontend dist not found at %s - API only mode", FRONTEND_DIST)


# ── Error Handling ────────────────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
        ).model_dump(),
    )


# ── Helper: Convert graph result → AnalysisResponse ──────────────


async def _build_response(result: dict, analysis_type: AnalysisType) -> AnalysisResponse:
    """Convert raw LangGraph output into a structured AnalysisResponse."""
    logger.info("Building response from graph result")

    stocks_analysis = []
    stock_list = result.get("stocks", [])
    fundamental_all = result.get("fundamental_result", {})
    technical_all = result.get("technical_result", {})
    sentiment_all = result.get("sentiment_result", {})

    for ticker in stock_list:
        f_data = fundamental_all.get(ticker, {})
        t_data = technical_all.get(ticker, {})
        s_data = sentiment_all.get(ticker, {})
        
        # Fetch news for this stock
        news_articles = []
        try:
            import asyncio
            # Run news fetch synchronously within async context
            news_data = await YahooFinanceTool.get_all_stock_data(ticker)
            raw_news = news_data.get("news", [])
            for article in raw_news[:5]:  # Limit to 5 articles
                news_articles.append(NewsArticle(
                    title=article.get("title", ""),
                    publisher=article.get("publisher", ""),
                    link=article.get("link", ""),
                    publish_time=str(article.get("publish_time", "")),
                    summary=article.get("summary", ""),
                ))
        except Exception as e:
            logger.warning("Failed to fetch news for %s: %s", ticker, e)

        stocks_analysis.append(
            StockAnalysis(
                stock=ticker,
                fundamental=FundamentalAnalysis(
                    revenue=str(f_data.get("revenue", "")),
                    pe_ratio=f_data.get("pe_ratio"),
                    earnings_growth=str(f_data.get("earnings_growth", "")),
                    market_cap=str(f_data.get("market_cap", "")),
                    debt=str(f_data.get("debt", "")),
                    profit_margin=str(f_data.get("profit_margin", "")),
                    score=float(f_data.get("score", 0)),
                    summary=str(f_data.get("summary", "")),
                ),
                technical=TechnicalAnalysis(
                    rsi=t_data.get("rsi"),
                    macd=str(t_data.get("macd", "")),
                    ma50=t_data.get("ma50"),
                    ma200=t_data.get("ma200"),
                    trend=str(t_data.get("trend", "")),
                    score=float(t_data.get("score", 0)),
                    summary=str(t_data.get("summary", "")),
                ),
                sentiment=SentimentAnalysis(
                    positive_signals=list(s_data.get("positive_signals", [])),
                    negative_signals=list(s_data.get("negative_signals", [])),
                    score=float(s_data.get("score", 0)),
                    summary=str(s_data.get("summary", "")),
                ),
                news=news_articles,
            )
        )

    rec_str = result.get("recommendation", "HOLD").upper()
    try:
        recommendation = Recommendation(rec_str)
    except ValueError:
        recommendation = Recommendation.HOLD

    response = AnalysisResponse(
        analysis_type=analysis_type,
        stocks=stocks_analysis,
        recommendation=recommendation,
        reasoning=result.get("reasoning", ""),
    )

    logger.info("Response built: type=%s, stocks=%d, rec=%s",
                analysis_type.value, len(stocks_analysis), recommendation.value)
    return response


# ── Endpoints ─────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Serve React frontend if available, otherwise redirect to API docs."""
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "market-analyst-ai"}


@app.post("/analyze_stock", response_model=AnalysisResponse)
async def analyze_stock(request: AnalyzeStockRequest):
    """Analyze a single stock."""
    logger.info("POST /analyze_stock – ticker=%s", request.stock)

    try:
        result = await run_single_stock_analysis(request.stock)
        return await _build_response(result, AnalysisType.SINGLE)
    except Exception as e:
        logger.error("Error analyzing stock %s: %s", request.stock, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare_stocks", response_model=AnalysisResponse)
async def compare_stocks(request: CompareStocksRequest):
    """Compare two stocks head-to-head."""
    logger.info("POST /compare_stocks – %s vs %s", request.stock_a, request.stock_b)

    try:
        result = await run_compare_stocks(request.stock_a, request.stock_b)
        return await _build_response(result, AnalysisType.COMPARE)
    except Exception as e:
        logger.error("Error comparing stocks: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio_analysis", response_model=AnalysisResponse)
async def portfolio_analysis(request: PortfolioRequest):
    """Analyze a portfolio of stocks."""
    logger.info("POST /portfolio_analysis – stocks=%s", request.stocks)

    try:
        result = await run_portfolio_analysis(request.stocks)
        return await _build_response(result, AnalysisType.PORTFOLIO)
    except Exception as e:
        logger.error("Error analyzing portfolio: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse_intent", response_model=IntentResponse)
async def parse_intent(request: ChatRequest):
    """Parse a free-form query to extract stocks and analysis type."""
    logger.info("POST /parse_intent – query=%r", request.query)

    try:
        intent = await parse_intent_cached(request.query)
        return IntentResponse(
            stocks=intent.get("stocks", []),
            analysis_type=intent.get("analysis_type", "single"),
            parsed_query=intent.get("parsed_query", request.query),
        )
    except Exception as e:
        logger.error("Error parsing intent: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=AnalysisResponse)
async def chat(request: ChatRequest):
    """Free-form market question."""
    logger.info("POST /chat – query=%r", request.query)

    try:
        result = await run_analysis(request.query)

        # Determine type from result
        analysis_type_str = result.get("analysis_type", "single")
        try:
            analysis_type = AnalysisType(analysis_type_str)
        except ValueError:
            analysis_type = AnalysisType.SINGLE

        return await _build_response(result, analysis_type)
    except Exception as e:
        logger.error("Error processing chat: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Advanced Feature Endpoints ────────────────────────────────────

# Watchlist endpoints
@app.get("/watchlist", response_model=list[WatchlistItem])
async def get_watchlist():
    """Get all stocks in the watchlist."""
    logger.info("GET /watchlist")
    return await SQLiteMCPTool.get_watchlist()


@app.post("/watchlist/{ticker}")
async def add_to_watchlist(ticker: str, notes: str = ""):
    """Add a stock to the watchlist."""
    logger.info("POST /watchlist/%s", ticker)
    success = await SQLiteMCPTool.add_to_watchlist(ticker, notes)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")
    return {"success": True, "ticker": ticker}


@app.delete("/watchlist/{ticker}")
async def remove_from_watchlist(ticker: str):
    """Remove a stock from the watchlist."""
    logger.info("DELETE /watchlist/%s", ticker)
    success = await SQLiteMCPTool.remove_from_watchlist(ticker)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist")
    return {"success": True, "ticker": ticker}


# NSE Corporate Actions Dividend endpoint - uses BSE India API
@app.get("/nse/dividends")
async def nse_dividends(ticker: str = None):
    """Get dividend announcements from BSE India API."""
    logger.info(f"GET /nse/dividends ticker={ticker}")
    
    try:
        from backend.tools.bse_dividend_api_tool import bse_dividend_api_tool
        
        if ticker:
            # Get dividends for specific ticker
            result = await bse_dividend_api_tool.get_dividends_by_ticker(ticker)
        else:
            # Get all recent dividends from major stocks
            result = await bse_dividend_api_tool.get_dividend_announcements(days_back=90, days_ahead=30)
        
        # Format response to match expected structure
        dividends = result.get("dividends", [])
        announcements = []
        for d in dividends:
            announcements.append({
                "ticker": d.get("symbol", ""),
                "company_name": d.get("company_name", ""),
                "dividend_amount": d.get("dividend_amount"),
                "dividend_type": d.get("dividend_type", ""),
                "ex_dividend_date": d.get("ex_date", ""),
                "record_date": d.get("record_date", ""),
                "announcement_date": d.get("announcement_date", ""),
                "purpose": d.get("purpose", ""),
                "source": "BSE India API"
            })
        
        return {
            "ticker": ticker.upper().replace('.NS', '').replace('.BO', '') if ticker else "ALL",
            "announcements": announcements,
            "count": len(announcements),
            "source": "BSE India API",
            "search_date": datetime.now().strftime("%d %B %Y"),
            "error": None
        }
    except Exception as e:
        logger.error(f"Error fetching dividends: {e}", exc_info=True)
        return {
            "ticker": ticker.upper().replace('.NS', '').replace('.BO', '') if ticker else "ALL",
            "error": str(e),
            "announcements": [],
            "count": 0,
            "source": "Yahoo Finance - Error"
        }


# Historical Analysis endpoint
@app.get("/historical/{ticker}", response_model=HistoricalAnalysisResponse)
async def get_historical_analysis(ticker: str, limit: int = 30):
    """Get historical analysis data for a stock."""
    logger.info("GET /historical/%s limit=%d", ticker, limit)
    
    try:
        history = await SQLiteMCPTool.get_analysis_history(ticker, limit)
        
        # If no history in DB, return sample data for demo
        if not history:
            logger.info("No history in DB for %s, returning sample data", ticker)
            now = datetime.now()
            sample_data = [
                {
                    "analysis": {
                        "ticker": ticker,
                        "fundamental_score": 75,
                        "technical_score": 68,
                        "sentiment_score": 72,
                        "recommendation": "HOLD",
                        "reasoning": "Stock showing mixed signals with moderate fundamentals."
                    },
                    "created_at": (now - timedelta(days=i*7)).timestamp()
                }
                for i in range(min(limit, 5))
            ]
            return HistoricalAnalysisResponse(
                ticker=ticker,
                history=sample_data,
                count=len(sample_data)
            )
        
        return HistoricalAnalysisResponse(
            ticker=ticker,
            history=history,
            count=len(history)
        )
    except Exception as e:
        logger.error("Error getting historical analysis: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# Export endpoint
@app.post("/export")
async def export_report(request: ExportRequest):
    """Export analysis report in PDF, CSV, or JSON format."""
    logger.info("POST /export %s as %s", request.ticker, request.format)
    
    try:
        # Run analysis
        result = await run_single_stock_analysis(request.ticker)
        response = await _build_response(result, AnalysisType.SINGLE)
        
        if request.format == "json":
            return JSONResponse(
                content=response.model_dump(),
                headers={"Content-Disposition": f"attachment; filename={request.ticker}_analysis.json"}
            )
        elif request.format == "csv":
            import csv
            import io
            
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(["Stock", "Recommendation", "Fundamental Score", "Technical Score", "Sentiment Score"])
            
            # Data
            for stock in response.stocks:
                writer.writerow([
                    stock.stock,
                    response.recommendation.value,
                    stock.fundamental.score,
                    stock.technical.score,
                    stock.sentiment.score
                ])
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={request.ticker}_analysis.csv"}
            )
        else:
            # PDF format - return JSON for now (PDF generation requires additional libs)
            return JSONResponse(
                content={
                    "message": "PDF export requires additional setup. Use 'json' or 'csv' format.",
                    "analysis": response.model_dump()
                }
            )
    except Exception as e:
        logger.error("Error exporting report: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/sector_performance")
async def nse_sector_performance():
    """Get Indian sector performance data from NSE sectoral indices."""
    logger.info("GET /nse/sector_performance - Using NSE Indian sectors")
    
    try:
        from backend.tools.nse_market_tool import nse_market_tool
        sectors = nse_market_tool.get_sector_performance()
        return {"sectors": sectors, "count": len(sectors), "source": "NSE Sectoral Indices"}
    except Exception as e:
        logger.error("Error fetching NSE sector performance: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Failed to fetch sector performance: {str(e)}")


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (keys masked)."""
    import os
    
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    return {
        "groq_api_key_set": bool(groq_key),
        "groq_api_key_preview": groq_key[:8] + "..." + groq_key[-4:] if len(groq_key) > 12 else ("***" if groq_key else "NOT SET"),
        "environment": dict(os.environ) if os.getenv("DEBUG_FULL_ENV") else "Set DEBUG_FULL_ENV to see all"
    }

@app.get("/debug/test_yahoo")
async def debug_test_yahoo():
    """Test Yahoo Finance directly to see if it's working."""
    try:
        import yfinance as yf
        
        # Test NIFTY 50
        nifty = yf.Ticker("^NSEI")
        nifty_info = nifty.info
        nifty_hist = nifty.history(period="2d")
        
        return {
            "yfinance_available": True,
            "nifty_info_keys": list(nifty_info.keys())[:10] if nifty_info else [],
            "nifty_history_length": len(nifty_hist),
            "nifty_last_close": float(nifty_hist['Close'].iloc[-1]) if len(nifty_hist) > 0 else None,
            "nifty_prev_close": float(nifty_hist['Close'].iloc[-2]) if len(nifty_hist) > 1 else None,
        }
    except Exception as e:
        return {
            "yfinance_available": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/debug/nsetools")
async def debug_nsetools():
    """Debug endpoint to check nsetools availability and test data fetch."""
    logger.info("GET /debug/nsetools")
    
    result = {
        "nsetools_available": False,
        "nsetools_initialized": False,
        "test_fetch": None,
        "error": None
    }
    
    try:
        from backend.tools.nse_market_tool import NSETOOLS_AVAILABLE, nse_market_tool
        result["nsetools_available"] = NSETOOLS_AVAILABLE
        result["nsetools_initialized"] = nse_market_tool is not None
        
        if nse_market_tool:
            try:
                # Test fetch NIFTY 50
                nifty = nse_market_tool.nse.get_index_quote("NIFTY 50")
                result["test_fetch"] = {
                    "nifty_50_data": nifty,
                    "success": nifty is not None
                }
            except Exception as e:
                result["test_fetch"] = {"error": str(e)}
    except Exception as e:
        result["error"] = str(e)
    
    return result


@app.get("/nse/market_overview")
async def nse_market_overview():
    """Get market overview from nsetools - real-time data."""
    logger.info("GET /nse/market_overview")
    
    try:
        from backend.tools.nse_market_tool import nse_market_tool
        overview = nse_market_tool.get_market_state()
        logger.info("Fresh market overview fetched from nsetools")
        return overview
    except Exception as e:
        logger.error("Error fetching market overview from nsetools: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Failed to fetch market data: {str(e)}")


@app.get("/nse/market_movers")
async def nse_market_movers(type: str = "gainers"):
    """Get Indian market movers (gainers/losers) from NSE."""
    logger.info("GET /nse/market_movers type=%s", type)
    
    try:
        from backend.tools.nse_market_tool import nse_market_tool
        movers = nse_market_tool.get_market_movers(type)
        return {"movers": movers, "type": type, "count": len(movers), "source": "NSE"}
    except Exception as e:
        logger.error("Error fetching NSE market movers: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Failed to fetch market movers: {str(e)}")


@app.get("/indian_news/market")
async def indian_market_news(max_results: int = 10):
    """Get Indian stock market news from Moneycontrol, Economic Times, etc."""
    logger.info(f"GET /indian_news/market - max_results={max_results}")
    
    try:
        from backend.tools.indian_stock_news_tool import indian_stock_news_tool
        news = await indian_stock_news_tool.get_market_news(max_results=max_results)
        logger.info(f"Indian market news result: count={news.get('count', 0)}, source={news.get('source')}")
        if news.get('error'):
            logger.error(f"Indian news error: {news.get('error')}")
        return news
    except Exception as e:
        logger.error(f"Error fetching Indian market news: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Failed to fetch news: {str(e)}")


@app.get("/indian_news/company/{symbol}")
async def indian_company_news(symbol: str, max_results: int = 5):
    """Get Indian company-specific news."""
    logger.info(f"GET /indian_news/company/{symbol}")
    
    try:
        from backend.tools.indian_stock_news_tool import indian_stock_news_tool
        news = await indian_stock_news_tool.get_company_news(symbol, max_results=max_results)
        return news
    except Exception as e:
        logger.error(f"Error fetching Indian company news for {symbol}: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Failed to fetch news: {str(e)}")


@app.get("/indian_news/category/{category}")
async def indian_category_news(category: str, max_results: int = 10):
    """Get Indian stock news by category: ipo, merger, earnings, forex, crypto, general."""
    logger.info(f"GET /indian_news/category/{category}")
    
    try:
        from backend.tools.indian_stock_news_tool import indian_stock_news_tool
        news = await indian_stock_news_tool.get_category_news(category, max_results=max_results)
        return news
    except Exception as e:
        logger.error(f"Error fetching Indian category news for {category}: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Failed to fetch news: {str(e)}")


@app.get("/dividends/announcements")
async def dividend_announcements(days_back: int = 30, days_ahead: int = 30):
    """Get recent and upcoming dividends from dual live BSE sources."""
    logger.info("GET /dividends/announcements - days_back=%d, days_ahead=%d", days_back, days_ahead)

    from backend.tools.bse_dividend_api_tool import bse_dividend_api_tool
    from backend.tools.bse_corporate_actions_tool import bse_corporate_actions_tool

    primary_items: list[dict] = []
    secondary_items: list[dict] = []
    primary_error = None
    secondary_error = None
    source_status = {
        "primary_bse_package": {"status": "error", "count": 0},
        "secondary_bse_http": {"status": "error", "count": 0},
    }

    try:
        primary = await bse_dividend_api_tool.get_dividend_announcements(
            days_back=days_back,
            days_ahead=days_ahead,
        )
        primary_items = primary.get("dividends", [])
        source_status["primary_bse_package"] = {
            "status": "ok" if primary_items else "empty",
            "count": len(primary_items),
            "error": primary.get("error"),
        }
    except Exception as e:
        primary_error = str(e)
        source_status["primary_bse_package"] = {
            "status": "error",
            "count": 0,
            "error": primary_error,
        }
        logger.error("Primary BSE source failed: %s", e, exc_info=True)

    try:
        # Secondary source already supports date-window filtering.
        secondary = await bse_corporate_actions_tool.get_dividend_announcements(
            from_date=(datetime.now() - timedelta(days=days_back)).strftime("%d-%m-%Y"),
            to_date=(datetime.now() + timedelta(days=days_ahead)).strftime("%d-%m-%Y"),
        )
        secondary_items = secondary.get("dividends", [])
        secondary_diag = secondary.get("diagnostics", {})
        source_status["secondary_bse_http"] = {
            "status": secondary_diag.get("status", "ok" if secondary_items else "empty"),
            "count": len(secondary_items),
            "error": secondary.get("error"),
            "diagnostics": secondary_diag,
        }
        # Tag secondary rows clearly for observability.
        for item in secondary_items:
            if not item.get("source"):
                item["source"] = "BSE Corporate Actions API"
    except Exception as e:
        secondary_error = str(e)
        source_status["secondary_bse_http"] = {
            "status": "error",
            "count": 0,
            "error": secondary_error,
        }
        logger.error("Secondary BSE source failed: %s", e, exc_info=True)

    merged_map: dict[tuple[str, str, str], dict] = {}
    for item in primary_items + secondary_items:
        symbol = str(item.get("symbol", "")).strip().upper()
        ex_date = str(item.get("ex_date", "")).strip()
        purpose = str(item.get("purpose", "")).strip().upper()
        if not ex_date:
            continue
        key = (symbol, ex_date, purpose)
        if key not in merged_map:
            merged_map[key] = item

    merged_items = list(merged_map.values())
    if not merged_items:
        raise HTTPException(
            status_code=503,
            detail=(
                "No live dividend data available from both BSE sources. "
                f"primary_error={primary_error}, secondary_error={secondary_error}, "
                f"source_status={source_status}"
            ),
        )

    # Sort newest first where date parse succeeds.
    def _safe_ex_date(value: str) -> datetime:
        try:
            return datetime.strptime(value, "%d-%m-%Y")
        except (TypeError, ValueError):
            return datetime.min

    merged_items.sort(
        key=lambda x: _safe_ex_date(x.get("ex_date", "")),
        reverse=True,
    )

    now = datetime.now()
    recent_items = []
    upcoming_items = []

    for item in merged_items:
        ex_date_str = item.get("ex_date", "")
        try:
            ex_date = datetime.strptime(ex_date_str, "%d-%m-%Y")
        except ValueError:
            continue

        if ex_date >= now:
            upcoming_items.append(item)
        else:
            recent_items.append(item)

    return {
        "recent": {
            "dividends": recent_items,
            "count": len(recent_items),
            "source": "bse_dual_live",
            "recent_days": days_back,
        },
        "upcoming": {
            "dividends": upcoming_items,
            "count": len(upcoming_items),
            "source": "bse_dual_live",
            "upcoming_days": days_ahead,
        },
        "cached_at": datetime.now().isoformat(),
        "sources_used": {
            "primary_count": len(primary_items),
            "secondary_count": len(secondary_items),
        },
        "source_status": source_status,
    }
