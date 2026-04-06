"""
Pydantic request / response schemas for the FastAPI endpoints.

Validation, serialisation, and OpenAPI docs are all driven by these models.
"""

from __future__ import annotations

import logging
from enum import Enum

from typing import Optional

from pydantic import BaseModel, Field


logger = logging.getLogger("market_analyst.models.schemas")


# ── Enums ──────────────────────────────────────────────────────────


class Recommendation(str, Enum):
    """Possible final recommendations."""

    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class AnalysisType(str, Enum):
    """Types of analysis the system supports."""

    SINGLE = "single"
    COMPARE = "compare"
    PORTFOLIO = "portfolio"


# ── Requests ───────────────────────────────────────────────────────


class AnalyzeStockRequest(BaseModel):
    """POST /analyze_stock"""

    stock: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock ticker symbol, e.g. 'RELIANCE.NS'",
        examples=["RELIANCE.NS", "TCS.NS"],
    )


class CompareStocksRequest(BaseModel):
    """POST /compare_stocks"""

    stock_a: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="First stock ticker",
        examples=["TATAMOTORS.NS"],
    )
    stock_b: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Second stock ticker",
        examples=["M&M.NS"],
    )


class PortfolioRequest(BaseModel):
    """POST /portfolio_analysis"""

    stocks: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of stock tickers in the portfolio",
        examples=[["RELIANCE.NS", "TCS.NS", "INFY.NS"]],
    )


class ChatRequest(BaseModel):
    """POST /chat – free-form query."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Natural-language market question",
        examples=["Compare Tata Motors and Mahindra"],
    )


# ── Sub-responses ──────────────────────────────────────────────────


class FundamentalAnalysis(BaseModel):
    """Fundamental analysis section of the response."""

    revenue: str = ""
    pe_ratio: Optional[float] = None
    earnings_growth: str = ""
    market_cap: str = ""
    debt: str = ""
    profit_margin: str = ""
    score: float = Field(0.0, ge=0, le=10)
    summary: str = ""


class TechnicalAnalysis(BaseModel):
    """Technical analysis section of the response."""

    rsi: Optional[float] = None
    macd: str = ""
    ma50: Optional[float] = None
    ma200: Optional[float] = None
    trend: str = ""
    score: float = Field(0.0, ge=0, le=10)
    summary: str = ""


class SentimentAnalysis(BaseModel):
    """Sentiment analysis section of the response."""

    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    score: float = Field(0.0, ge=0, le=10)
    summary: str = ""


class NewsArticle(BaseModel):
    """News article from Yahoo Finance."""
    
    title: str = ""
    publisher: str = ""
    link: str = ""
    publish_time: str = ""
    summary: str = ""


class StockAnalysis(BaseModel):
    """Combined analysis for one stock."""

    stock: str
    fundamental: FundamentalAnalysis = Field(default_factory=FundamentalAnalysis)
    technical: TechnicalAnalysis = Field(default_factory=TechnicalAnalysis)
    sentiment: SentimentAnalysis = Field(default_factory=SentimentAnalysis)
    news: list[NewsArticle] = Field(default_factory=list)


# ── Top-level response ────────────────────────────────────────────


class AnalysisResponse(BaseModel):
    """Unified response returned by all analysis endpoints."""

    analysis_type: AnalysisType
    stocks: list[StockAnalysis] = Field(default_factory=list)
    recommendation: Recommendation = Recommendation.HOLD
    reasoning: str = ""


class IntentResponse(BaseModel):
    """Response from /parse_intent – detected stocks and analysis type."""

    stocks: list[str] = Field(default_factory=list)
    analysis_type: str = Field(
        default="single",
        description="Detected analysis type: single, compare, or portfolio",
    )
    parsed_query: str = Field(
        default="",
        description="Cleaned version of the user query",
    )


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    detail: str = ""


# ── Advanced Feature Schemas ───────────────────────────────────────

class WatchlistItem(BaseModel):
    """Watchlist entry."""
    ticker: str
    added_at: float
    notes: str = ""


class ScreenerRequest(BaseModel):
    """POST /screener - Filter stocks."""
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_market_cap: Optional[float] = None  # in crores
    min_profit_margin: Optional[float] = None  # 0-1
    max_debt_to_equity: Optional[float] = None
    min_roe: Optional[float] = None  # 0-1
    sector: Optional[str] = None
    limit: int = Field(20, ge=1, le=50)


class ScreenerResult(BaseModel):
    """Single screener result."""
    ticker: str
    company_name: str
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    profit_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    current_price: Optional[float] = None
    sector: str = "Unknown"


class ScreenerResponse(BaseModel):
    """Screener results."""
    results: list[ScreenerResult] = Field(default_factory=list)
    count: int = 0
    criteria: dict = Field(default_factory=dict)


class RiskMetricsRequest(BaseModel):
    """POST /risk_metrics - Calculate risk for stocks."""
    tickers: list[str] = Field(..., min_length=1, max_length=10)
    period: str = "1y"


class SharpeRatio(BaseModel):
    """Sharpe ratio metrics."""
    ticker: str
    sharpe_ratio: Optional[float] = None
    annual_return: Optional[float] = None
    annual_volatility: Optional[float] = None
    error: Optional[str] = None


class BetaMetrics(BaseModel):
    """Beta metrics."""
    ticker: str
    beta: Optional[float] = None
    correlation: Optional[float] = None
    market_index: str = "^NSEI"
    interpretation: str = ""
    error: Optional[str] = None


class VaRMetrics(BaseModel):
    """Value at Risk metrics."""
    ticker: str
    var_daily_percent: Optional[float] = None
    var_amount: Optional[float] = None
    confidence: float = 0.95
    current_price: Optional[float] = None
    interpretation: str = ""
    error: Optional[str] = None


class RiskMetricsResponse(BaseModel):
    """Combined risk metrics response."""
    sharpe_ratios: list[SharpeRatio] = Field(default_factory=list)
    betas: list[BetaMetrics] = Field(default_factory=list)
    var_metrics: list[VaRMetrics] = Field(default_factory=list)


class CorrelationRequest(BaseModel):
    """POST /correlation - Get correlation matrix."""
    tickers: list[str] = Field(..., min_length=2, max_length=10)
    period: str = "1y"


class CorrelationResponse(BaseModel):
    """Correlation matrix response."""
    tickers: list[str] = Field(default_factory=list)
    matrix: dict = Field(default_factory=dict)
    period: str = "1y"
    data_points: int = 0


class EarningsInfo(BaseModel):
    """Earnings information."""
    ticker: str
    earnings_date: Optional[str] = None
    eps_estimate: Optional[float] = None
    revenue_estimate: Optional[float] = None
    eps_actual: Optional[float] = None
    forward_eps: Optional[float] = None
    next_earnings: Optional[str] = None
    error: Optional[str] = None


class EarningsCalendarResponse(BaseModel):
    """Upcoming earnings response."""
    earnings: list[EarningsInfo] = Field(default_factory=list)
    days_ahead: int = 30


class DividendInfo(BaseModel):
    """Dividend information."""
    ticker: str
    dividend_rate: Optional[float] = None
    dividend_yield: Optional[float] = None
    ex_dividend_date: Optional[str] = None
    payout_ratio: Optional[float] = None
    five_year_avg_yield: Optional[float] = None
    history: list[dict] = Field(default_factory=list)
    error: Optional[str] = None


class HistoricalAnalysisRequest(BaseModel):
    """GET /historical/{ticker} - Get historical analysis."""
    ticker: str
    limit: int = 30


class HistoricalAnalysisResponse(BaseModel):
    """Historical analysis data."""
    ticker: str
    history: list[dict] = Field(default_factory=list)
    count: int = 0


class ExportRequest(BaseModel):
    """POST /export - Export analysis report."""
    ticker: str
    format: str = Field("pdf", pattern="^(pdf|csv|json)$")


logger.info("Pydantic schemas loaded")
