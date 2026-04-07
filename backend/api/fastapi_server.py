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
    BetaMetrics,
    ChatRequest,
    CompareStocksRequest,
    CorrelationRequest,
    CorrelationResponse,
    DividendInfo,
    EarningsCalendarResponse,
    EarningsInfo,
    ErrorResponse,
    ExportRequest,
    FundamentalAnalysis,
    HistoricalAnalysisResponse,
    IntentResponse,
    NewsArticle,
    PortfolioRequest,
    Recommendation,
    RiskMetricsRequest,
    RiskMetricsResponse,
    SentimentAnalysis,
    SharpeRatio,
    ScreenerRequest,
    ScreenerResponse,
    ScreenerResult,
    StockAnalysis,
    TechnicalAnalysis,
    VaRMetrics,
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


# Stock Screener endpoint
@app.post("/screener", response_model=ScreenerResponse)
async def stock_screener(request: ScreenerRequest):
    """Screen stocks based on fundamental criteria."""
    logger.info("POST /screener with criteria: %s", request.model_dump())
    
    from backend.tools.advanced_tools import StockScreenerTool
    
    try:
        results = await StockScreenerTool.screen_stocks(
            min_pe=request.min_pe,
            max_pe=request.max_pe,
            min_market_cap=request.min_market_cap,
            min_profit_margin=request.min_profit_margin,
            max_debt_to_equity=request.max_debt_to_equity,
            min_roe=request.min_roe,
            sector=request.sector,
            limit=request.limit
        )
        
        return ScreenerResponse(
            results=[ScreenerResult(**r) for r in results],
            count=len(results),
            criteria=request.model_dump(exclude={"limit"})
        )
    except Exception as e:
        logger.error("Error in stock screener: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# Risk Metrics endpoint
@app.post("/risk_metrics", response_model=RiskMetricsResponse)
async def risk_metrics(request: RiskMetricsRequest):
    """Calculate risk metrics (Sharpe, Beta, VaR) for stocks."""
    logger.info("POST /risk_metrics for tickers: %s", request.tickers)
    
    from backend.tools.advanced_tools import RiskMetricsTool
    
    try:
        sharpe_results = []
        beta_results = []
        var_results = []
        
        for ticker in request.tickers:
            sharpe = await RiskMetricsTool.calculate_sharpe_ratio(ticker, request.period)
            beta = await RiskMetricsTool.calculate_beta(ticker, period=request.period)
            var = await RiskMetricsTool.calculate_var(ticker, period=request.period)
            
            sharpe_results.append(SharpeRatio(**sharpe))
            beta_results.append(BetaMetrics(**beta))
            var_results.append(VaRMetrics(**var))
        
        return RiskMetricsResponse(
            sharpe_ratios=sharpe_results,
            betas=beta_results,
            var_metrics=var_results
        )
    except Exception as e:
        logger.error("Error calculating risk metrics: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# Correlation Matrix endpoint
@app.post("/correlation", response_model=CorrelationResponse)
async def correlation_matrix(request: CorrelationRequest):
    """Get correlation matrix for a list of stocks."""
    logger.info("POST /correlation for tickers: %s", request.tickers)
    
    from backend.tools.advanced_tools import CorrelationMatrixTool
    
    try:
        result = await CorrelationMatrixTool.get_correlation_matrix(
            request.tickers, 
            request.period
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return CorrelationResponse(**result)
    except Exception as e:
        logger.error("Error calculating correlation: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# Earnings Calendar endpoint
@app.get("/earnings/{ticker}", response_model=EarningsInfo)
async def get_earnings(ticker: str):
    """Get earnings information for a stock."""
    logger.info("GET /earnings/%s", ticker)
    
    from backend.tools.advanced_tools import EarningsDividendTool
    
    try:
        result = await EarningsDividendTool.get_earnings_info(ticker)
        return EarningsInfo(**result)
    except Exception as e:
        logger.error("Error getting earnings: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/earnings_calendar", response_model=EarningsCalendarResponse)
async def earnings_calendar(days: int = 30):
    """Get upcoming earnings calendar."""
    logger.info("GET /earnings_calendar days=%d", days)
    
    earnings = await SQLiteMCPTool.get_upcoming_earnings(days)
    return EarningsCalendarResponse(
        earnings=[EarningsInfo(**e) for e in earnings],
        days_ahead=days
    )


# Dividend endpoint
@app.get("/dividends/{ticker}", response_model=DividendInfo)
async def get_dividends(ticker: str):
    """Get dividend information for a stock."""
    logger.info("GET /dividends/%s", ticker)
    
    from backend.tools.advanced_tools import EarningsDividendTool
    
    try:
        # Get live data from yfinance
        result = await EarningsDividendTool.get_dividend_info(ticker)
        
        # Get historical data from database
        history = await SQLiteMCPTool.get_dividend_history(ticker)
        result["history"] = history
        
        return DividendInfo(**result)
    except Exception as e:
        logger.error("Error getting dividends: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# MoneyControl Dividend endpoint - returns real-time or sample data from MoneyControl
@app.get("/moneycontrol/dividends")
async def get_moneycontrol_dividends(ticker: str = None):
    """Get dividend information from MoneyControl or sample data."""
    logger.info("GET /moneycontrol/dividends ticker=%s", ticker)
    
    # Use the MoneyControl dividend tool (now uses Finnhub)
    from backend.tools.moneycontrol_dividend_tool import get_moneycontrol_dividends as mc_get_dividends, get_all_dividends_from_finnhub
    
    try:
        if ticker:
            result = await mc_get_dividends(ticker)
        else:
            # Return all recent dividends
            result = await get_all_dividends_from_finnhub()
        return result
    except Exception as e:
        logger.error("Error fetching MoneyControl dividends: %s", e)
        return {
            "ticker": ticker.upper().replace('.NS', '') if ticker else "ALL",
            "error": str(e),
            "history": []
        }


# Get all recent dividend announcements
@app.get("/moneycontrol/dividends/all")
async def get_all_dividends():
    """Get all recent dividend announcements."""
    logger.info("GET /moneycontrol/dividends/all")
    
    from backend.tools.moneycontrol_dividend_tool import get_all_dividends_from_moneycontrol
    
    try:
        result = await get_all_dividends_from_moneycontrol()
        return result
    except Exception as e:
        logger.error("Error fetching all dividends: %s", e)
        return {
            "ticker": "ALL",
            "error": str(e),
            "announcements": []
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


# ── Finnhub API Endpoints ─────────────────────────────────────────

@app.get("/finnhub/earnings_calendar")
async def finnhub_earnings_calendar(from_date: str = None, to_date: str = None, symbol: str = None):
    """Get earnings calendar from Finnhub."""
    logger.info("GET /finnhub/earnings_calendar")
    
    from backend.tools.finnhub_tool import finnhub_tool
    
    try:
        earnings = finnhub_tool.get_earnings_calendar(symbol, from_date, to_date)
        return {"earnings": earnings, "count": len(earnings)}
    except Exception as e:
        logger.error("Error fetching Finnhub earnings: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/finnhub/market_movers")
async def finnhub_market_movers(type: str = "gainers"):
    """Get market movers (gainers/losers/most active) from Finnhub."""
    logger.info("GET /finnhub/market_movers type=%s", type)
    
    try:
        from backend.tools.finnhub_tool import finnhub_tool
        movers = finnhub_tool.get_market_movers(type)
        return {"movers": movers, "type": type, "count": len(movers)}
    except Exception as e:
        logger.error("Error fetching Finnhub market movers: %s", e, exc_info=True)
        # Return dummy data on error
        dummy_movers = [
            {"symbol": "RELIANCE", "name": "Reliance Industries", "price": 2875.50, "change": 42.80, "change_percent": 5.07, "volume": 4850000},
            {"symbol": "TCS", "name": "Tata Consultancy", "price": 4165.20, "change": 182.30, "change_percent": 4.57, "volume": 5230000},
        ]
        return {"movers": dummy_movers, "type": type, "count": len(dummy_movers), "error": str(e)}


@app.get("/finnhub/news")
async def finnhub_news(category: str = "general", symbol: str = None):
    """Get market news from Finnhub."""
    logger.info("GET /finnhub_news category=%s", category)
    
    try:
        from backend.tools.finnhub_tool import finnhub_tool
        if symbol:
            news = finnhub_tool.get_company_news(symbol)
        else:
            news = finnhub_tool.get_market_news(category)
        return {"news": news, "count": len(news)}
    except Exception as e:
        logger.error("Error fetching Finnhub news: %s", e, exc_info=True)
        dummy_news = [
            {"category": "general", "datetime": 0, "headline": "Market data temporarily unavailable", "source": "System", "summary": str(e)[:100], "url": ""}
        ]
        return {"news": dummy_news, "count": 1, "error": str(e)}


@app.get("/finnhub/sector_performance")
async def finnhub_sector_performance():
    """Get sector performance data from Finnhub."""
    logger.info("GET /finnhub/sector_performance")
    
    try:
        from backend.tools.finnhub_tool import finnhub_tool
        sectors = finnhub_tool.get_sector_performance()
        return {"sectors": sectors, "count": len(sectors)}
    except Exception as e:
        logger.error("Error fetching Finnhub sector performance: %s", e, exc_info=True)
        dummy_sectors = [
            {"name": "Technology", "change_percent": 2.45},
            {"name": "Financials", "change_percent": 1.82},
            {"name": "Healthcare", "change_percent": 1.15},
        ]
        return {"sectors": dummy_sectors, "count": len(dummy_sectors), "error": str(e)}


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (keys masked)."""
    import os
    
    finnhub_key = os.getenv("FINNHUB_API_KEY", "")
    twelve_key = os.getenv("TWELVE_DATA_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    return {
        "finnhub_api_key_set": bool(finnhub_key),
        "finnhub_api_key_preview": finnhub_key[:8] + "..." + finnhub_key[-4:] if len(finnhub_key) > 12 else ("***" if finnhub_key else "NOT SET"),
        "twelve_data_api_key_set": bool(twelve_key),
        "twelve_data_api_key_preview": twelve_key[:8] + "..." + twelve_key[-4:] if len(twelve_key) > 12 else ("***" if twelve_key else "NOT SET"),
        "groq_api_key_set": bool(groq_key),
        "environment": dict(os.environ) if os.getenv("DEBUG_FULL_ENV") else "Set DEBUG_FULL_ENV to see all"
    }

@app.get("/twelve_data/market_overview")
async def twelve_data_market_overview():
    """Get market overview from Twelve Data (indices, gainers, losers)."""
    logger.info("GET /twelve_data/market_overview")
    
    try:
        from backend.tools.twelve_data_tool import twelve_data_tool
        overview = twelve_data_tool.get_market_state()
        return overview
    except Exception as e:
        logger.error("Error fetching Twelve Data market overview: %s", e, exc_info=True)
        # Return dummy data on error so UI doesn't break
        return {
            "indices": [
                {"symbol": "NIFTY50", "name": "NIFTY 50", "price": 24150.45, "change": 125.80, "change_percent": 0.52},
                {"symbol": "SENSEX", "name": "BSE SENSEX", "price": 79234.56, "change": 312.45, "change_percent": 0.40},
            ],
            "top_gainers": [],
            "top_losers": [],
            "timestamp": "error_fallback",
            "error": str(e)
        }


@app.get("/twelve_data/indices")
async def twelve_data_indices():
    """Get major market indices from Twelve Data."""
    logger.info("GET /twelve_data/indices")
    
    try:
        from backend.tools.twelve_data_tool import twelve_data_tool
        indices = twelve_data_tool.get_indices()
        return {"indices": indices, "count": len(indices)}
    except Exception as e:
        logger.error("Error fetching Twelve Data indices: %s", e, exc_info=True)
        return {"indices": [], "count": 0, "error": str(e)}
