"""Indian Stock News Tool - Fetches Indian stock market news using DuckDuckGo search.

Provides:
  - Indian stock news from Moneycontrol, Economic Times, NSE, BSE
  - Market updates, IPO news, company announcements
  - No API key required
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any
from duckduckgo_search import DDGS

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

class IndianStockNewsTool:
    """Tool for fetching Indian stock market news using DuckDuckGo search."""

    INDIAN_NEWS_SOURCES = [
        "site:moneycontrol.com",
        "site:economictimes.indiatimes.com",
        "site:livemint.com",
        "site:ndtvprofit.com",
        "site:zeebiz.com",
        "site:bsesensex.com",
        "site:nseindia.com",
    ]

    @staticmethod
    async def get_market_news(max_results: int = 10) -> dict[str, Any]:
        """Fetch general Indian stock market news."""
        cache_key = "indian_market_news"
        cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
        if cached:
            # Check if cache is from today
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if cache_dt.date() == datetime.now().date():
                    return cached

        queries = [
            "Indian stock market news today",
            "NSE BSE market updates today",
            "Sensex Nifty news today",
        ]

        news_items = []
        try:
            with DDGS() as ddgs:
                for query in queries[:2]:  # Limit to avoid rate limits
                    results = ddgs.news(
                        query,
                        region="in",
                        safesearch="off",
                        timelimit="d",  # Last 24 hours
                        max_results=max_results // 2
                    )
                    for r in results:
                        news_items.append({
                            "headline": r.get("title", ""),
                            "source": IndianStockNewsTool._extract_source(r.get("source", "")),
                            "url": r.get("url", ""),
                            "datetime": int(datetime.now().timestamp()),
                            "summary": r.get("body", "")[:200] + "..." if len(r.get("body", "")) > 200 else r.get("body", ""),
                            "category": "general"
                        })

                        if len(news_items) >= max_results:
                            break

                    if len(news_items) >= max_results:
                        break

            result = {
                "news": news_items[:max_results],
                "count": len(news_items[:max_results]),
                "source": "indian_stock_news",
                "cached_at": datetime.now().isoformat()
            }

            # Cache for 1 hour
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=3600)
            return result

        except Exception as e:
            return {
                "news": [],
                "count": 0,
                "error": str(e),
                "source": "indian_stock_news"
            }

    @staticmethod
    async def get_company_news(symbol: str, max_results: int = 5) -> dict[str, Any]:
        """Fetch news for a specific Indian company."""
        # Clean symbol
        clean_symbol = symbol.upper().replace(".NS", "").replace(".BO", "")

        cache_key = f"indian_company_news_{clean_symbol}"
        cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
        if cached:
            # Check if cache is from today
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if cache_dt.date() == datetime.now().date():
                    return cached

        queries = [
            f"{clean_symbol} share price news",
            f"{clean_symbol} stock news India",
            f"{clean_symbol} company news NSE",
        ]

        news_items = []
        try:
            with DDGS() as ddgs:
                for query in queries[:2]:
                    results = ddgs.news(
                        query,
                        region="in",
                        safesearch="off",
                        timelimit="w",  # Last week
                        max_results=max_results
                    )
                    for r in results:
                        news_items.append({
                            "headline": r.get("title", ""),
                            "source": IndianStockNewsTool._extract_source(r.get("source", "")),
                            "url": r.get("url", ""),
                            "datetime": int(datetime.now().timestamp()),
                            "summary": r.get("body", "")[:200] + "..." if len(r.get("body", "")) > 200 else r.get("body", ""),
                            "category": "company"
                        })

                        if len(news_items) >= max_results:
                            break

                    if len(news_items) >= max_results:
                        break

            result = {
                "symbol": clean_symbol,
                "news": news_items[:max_results],
                "count": len(news_items[:max_results]),
                "source": "indian_stock_news",
                "cached_at": datetime.now().isoformat()
            }

            # Cache for 2 hours
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=7200)
            return result

        except Exception as e:
            return {
                "symbol": clean_symbol,
                "news": [],
                "count": 0,
                "error": str(e),
                "source": "indian_stock_news"
            }

    @staticmethod
    async def get_category_news(category: str, max_results: int = 10) -> dict[str, Any]:
        """Fetch news by category: ipo, earnings, mergers, general."""
        cache_key = f"indian_category_news_{category}"
        cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
        if cached:
            # Check if cache is from today
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if cache_dt.date() == datetime.now().date():
                    return cached

        category_queries = {
            "ipo": "India IPO news today upcoming IPO NSE BSE",
            "merger": "India mergers acquisitions deals today",
            "earnings": "India company earnings results quarterly",
            "forex": "India rupee dollar forex currency market today",
            "crypto": "India crypto bitcoin news today",
            "general": "Indian stock market sensex nifty news today",
        }

        query = category_queries.get(category, category_queries["general"])

        news_items = []
        try:
            with DDGS() as ddgs:
                results = ddgs.news(
                    query,
                    region="in",
                    safesearch="off",
                    timelimit="d",
                    max_results=max_results
                )
                for r in results:
                    news_items.append({
                        "headline": r.get("title", ""),
                        "source": IndianStockNewsTool._extract_source(r.get("source", "")),
                        "url": r.get("url", ""),
                        "datetime": int(datetime.now().timestamp()),
                        "summary": r.get("body", "")[:200] + "..." if len(r.get("body", "")) > 200 else r.get("body", ""),
                        "category": category
                    })

            result = {
                "news": news_items[:max_results],
                "count": len(news_items[:max_results]),
                "category": category,
                "source": "indian_stock_news",
                "cached_at": datetime.now().isoformat()
            }

            # Cache for 1 hour
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=3600)
            return result

        except Exception as e:
            return {
                "news": [],
                "count": 0,
                "error": str(e),
                "category": category,
                "source": "indian_stock_news"
            }

    @staticmethod
    def _extract_source(source_str: str) -> str:
        """Extract clean source name from URL or string."""
        if not source_str:
            return "Unknown"

        # Remove common prefixes and clean up
        source = source_str.lower()
        source_mapping = {
            "moneycontrol": "Moneycontrol",
            "economictimes": "Economic Times",
            "indiatimes": "Economic Times",
            "livemint": "Mint",
            "ndtv": "NDTV Profit",
            "zeebiz": "Zee Business",
            "bsesensex": "BSE India",
            "nseindia": "NSE India",
            "business-standard": "Business Standard",
            "financialexpress": "Financial Express",
            "cnbc": "CNBC TV18",
        }

        for key, value in source_mapping.items():
            if key in source:
                return value

        # Return original with first letter capitalized
        return source_str.split('.')[0].capitalize()


# Global instance
indian_stock_news_tool = IndianStockNewsTool()
