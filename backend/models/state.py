"""
LangGraph state definition for the Market Analyst workflow.

This TypedDict flows through every node in the LangGraph graph.
Each agent writes its results into the corresponding field.
"""

from __future__ import annotations

import logging
from typing import TypedDict, Optional

logger = logging.getLogger("market_analyst.models.state")


# ── Per-agent result payloads ──────────────────────────────────────


class FundamentalResult(TypedDict, total=False):
    """Output of the Fundamental Analyst Agent."""

    revenue: str
    pe_ratio: Optional[float]
    earnings_growth: str
    market_cap: str
    debt: str
    profit_margin: str
    score: float  # 0–10
    summary: str


class TechnicalResult(TypedDict, total=False):
    """Output of the Technical Analyst Agent."""

    rsi: Optional[float]
    macd: str
    ma50: Optional[float]
    ma200: Optional[float]
    trend: str  # "bullish" | "bearish" | "neutral"
    score: float  # 0–10
    summary: str


class SentimentResult(TypedDict, total=False):
    """Output of the Sentiment Analyst Agent."""

    positive_signals: list[str]
    negative_signals: list[str]
    score: float  # 0–10
    summary: str


# ── Master graph state ─────────────────────────────────────────────


class MarketState(TypedDict, total=False):
    """
    Shared state that flows through the LangGraph workflow.

    Fields are populated progressively as agents execute:
      1. Intent analyser sets `query` and `stocks`.
      2. Specialist agents set their respective `*_result` fields.
      3. Master agent writes `final_decision`.
    """

    query: str
    stocks: list[str]
    analysis_type: str  # "single" | "compare" | "portfolio"
    fundamental_result: dict  # maps stock → FundamentalResult
    technical_result: dict  # maps stock → TechnicalResult
    sentiment_result: dict  # maps stock → SentimentResult
    final_decision: str


logger.info("State models loaded")
