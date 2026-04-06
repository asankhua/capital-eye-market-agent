"""
Intent Analyzer – Parses user queries to extract stocks and analysis type.

This is the entry node in the LangGraph workflow. It determines:
  - Which stocks should be analyzed
  - What type of analysis to perform (single/compare/portfolio)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.llm_provider import get_llm_provider

logger = logging.getLogger("market_analyst.agents.intent_analyzer")

# ── Prompt Template ────────────────────────────────────────────────

INTENT_PROMPT = """You are a query parser for a stock market analysis system. Extract the user's intent from their query.

**User query:** "{query}"

Determine:
1. Which stock ticker(s) are being asked about (use NSE format with .NS suffix, e.g. RELIANCE.NS, TATAMOTORS.NS, INFY.NS)
2. The type of analysis requested

Common Indian stock mappings:
- Reliance / RIL → RELIANCE.NS
- Tata Motors → TATAMOTORS.NS
- Mahindra / M&M → M&M.NS
- Infosys → INFY.NS
- TCS → TCS.NS
- HDFC Bank → HDFCBANK.NS
- ICICI Bank → ICICIBANK.NS
- Wipro → WIPRO.NS
- Bharti Airtel / Airtel → BHARTIARTL.NS
- SBI / State Bank → SBIN.NS
- ITC → ITC.NS
- Bajaj Finance → BAJFINANCE.NS
- HUL / Hindustan Unilever → HINDUNILVR.NS
- Asian Paints → ASIANPAINT.NS
- Maruti / Maruti Suzuki → MARUTI.NS
- REC / REC Ltd / REC Limited → RECLTD.NS
- PFC / Power Finance → PFC.NS

Respond in the following JSON format ONLY (no markdown, no extra text):
{{
    "stocks": ["<TICKER1.NS>", "<TICKER2.NS>"],
    "analysis_type": "<single|compare|portfolio>",
    "parsed_query": "<cleaned version of what the user is asking>"
}}

Rules:
- "single" = one stock analysis
- "compare" = exactly two stocks compared head-to-head
- "portfolio" = three or more stocks analyzed together
- If you cannot identify any stocks, return an empty list
"""


def _parse_llm_response(text: str) -> dict[str, Any]:
    """Parse LLM JSON response, handling potential markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    return json.loads(cleaned)


# ── Local Stock Mappings (Fallback when LLM unavailable) ─────────

# Common Indian stock name/ticker mappings
STOCK_MAPPINGS: dict[str, str] = {
    # Direct ticker mappings
    "tcs": "TCS.NS",
    "reliance": "RELIANCE.NS",
    "ril": "RELIANCE.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "tatamotors": "TATAMOTORS.NS",
    "tata motors": "TATAMOTORS.NS",
    "hdfcbank": "HDFCBANK.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icicibank": "ICICIBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "icici": "ICICIBANK.NS",
    "wipro": "WIPRO.NS",
    "sbibank": "SBIN.NS",
    "sbi": "SBIN.NS",
    "state bank": "SBIN.NS",
    "itc": "ITC.NS",
    "hul": "HINDUNILVR.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "hindunilvr": "HINDUNILVR.NS",
    "asianpaint": "ASIANPAINT.NS",
    "asian paints": "ASIANPAINT.NS",
    "maruti": "MARUTI.NS",
    "maruti suzuki": "MARUTI.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",
    "bhartiartl": "BHARTIARTL.NS",
    "bajajfinance": "BAJFINANCE.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "recltd": "RECLTD.NS",
    "rec": "RECLTD.NS",
    "rec ltd": "RECLTD.NS",
    "pfc": "PFC.NS",
    "power finance": "PFC.NS",
    "m&m": "M&M.NS",
    "mahindra": "M&M.NS",
    "axisbank": "AXISBANK.NS",
    "axis bank": "AXISBANK.NS",
    "kotakbank": "KOTAKBANK.NS",
    "kotak bank": "KOTAKBANK.NS",
    "kotak": "KOTAKBANK.NS",
    "lt": "LT.NS",
    "larsen": "LT.NS",
    "l&t": "LT.NS",
    "sunpharma": "SUNPHARMA.NS",
    "sun pharma": "SUNPHARMA.NS",
    "ongc": "ONGC.NS",
    "ntpc": "NTPC.NS",
    "coalindia": "COALINDIA.NS",
    "coal india": "COALINDIA.NS",
    "powergrid": "POWERGRID.NS",
    "power grid": "POWERGRID.NS",
    "bpcl": "BPCL.NS",
    "ioc": "IOC.NS",
    "hindpetro": "HINDPETRO.NS",
    "gail": "GAIL.NS",
    "nifty": "NIFTY50",
    "sensex": "SENSEX",
}


def _extract_stocks_locally(query: str) -> list[str]:
    """Extract stock tickers from query using local mappings (no LLM needed)."""
    import re
    
    query_lower = query.lower()
    stocks_found: set[str] = set()
    
    # Check for direct ticker mentions (uppercase words that look like tickers)
    words = re.findall(r'\b[A-Z]{2,10}\b', query)
    for word in words:
        word_lower = word.lower()
        if word_lower in STOCK_MAPPINGS:
            stocks_found.add(STOCK_MAPPINGS[word_lower])
        # Check if it's already a .NS ticker
        elif word.endswith('.NS') or word.endswith('.ns'):
            stocks_found.add(word.upper())
    
    # Check for multi-word names in the query
    for name, ticker in STOCK_MAPPINGS.items():
        if len(name.split()) > 1 and name in query_lower:
            stocks_found.add(ticker)
        elif ' ' not in name and name in query_lower.split():
            stocks_found.add(ticker)
    
    return list(stocks_found)


def analyze_intent(query: str) -> dict[str, Any]:
    """
    Parse a user query to extract stocks and analysis type.

    Args:
        query: Natural-language market question

    Returns:
        dict with stocks (list), analysis_type (str), parsed_query (str)
    """
    logger.info("Analyzing intent for query: %r", query)

    try:
        llm = get_llm_provider()
        prompt = INTENT_PROMPT.format(query=query)

        logger.info("Calling LLM for intent analysis")
        raw_text = llm.generate(prompt)
        logger.info("Intent analysis response received (%d chars)", len(raw_text))

        result = _parse_llm_response(raw_text)

        # Validate and normalize
        stocks = list(result.get("stocks", []))
        analysis_type = result.get("analysis_type", "single")

        # Auto-correct analysis type based on stock count
        if len(stocks) == 0:
            analysis_type = "single"
        elif len(stocks) == 1:
            analysis_type = "single"
        elif len(stocks) == 2:
            analysis_type = "compare"
        elif len(stocks) >= 3:
            analysis_type = "portfolio"

        parsed = {
            "stocks": stocks,
            "analysis_type": analysis_type,
            "parsed_query": result.get("parsed_query", query),
        }

        logger.info(
            "Intent parsed: stocks=%s, type=%s",
            parsed["stocks"], parsed["analysis_type"],
        )
        return parsed

    except Exception as e:
        logger.error("Intent analysis failed: %s", e)
        # Fallback: extract stocks locally without LLM
        fallback_stocks = _extract_stocks_locally(query)
        analysis_type = "single"
        if len(fallback_stocks) == 2:
            analysis_type = "compare"
        elif len(fallback_stocks) >= 3:
            analysis_type = "portfolio"
        
        logger.info("Fallback extraction found stocks: %s", fallback_stocks)
        return {
            "stocks": fallback_stocks,
            "analysis_type": analysis_type,
            "parsed_query": query,
        }


def analyze_intent_from_request(
    stocks: list[str],
    analysis_type: str,
    query: str = "",
) -> dict[str, Any]:
    """
    Build intent from explicit API request parameters (no LLM call needed).

    Used by typed endpoints like POST /analyze_stock, POST /compare_stocks.
    """
    logger.info(
        "Intent from request: stocks=%s, type=%s, query=%r",
        stocks, analysis_type, query,
    )
    return {
        "stocks": stocks,
        "analysis_type": analysis_type,
        "parsed_query": query or f"Analyze {', '.join(stocks)}",
    }
