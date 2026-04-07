"""Indian Stock News Tool - Fetches Indian stock market news using NewsAPI.

Provides:
  - Indian stock news from NewsAPI (Economic Times, Business Standard, etc.)
  - Market updates, IPO news, company announcements
  - Requires NewsAPI key (100 requests/day free)
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any
import requests

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.tools.indian_stock_news")

# Get API key from environment
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_BASE_URL = "https://newsapi.org/v2"

class IndianStockNewsTool:
    """Tool for fetching Indian stock market news using NewsAPI."""
    
    # Indian business news sources on NewsAPI
    INDIAN_SOURCES = [
        "the-times-of-india",
        "the-hindu",
        "business-insider",
        "financial-post"
    ]
    
    @staticmethod
    def _parse_newsapi_date(date_str: str) -> int:
        """Parse ISO 8601 date string to timestamp."""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return int(dt.timestamp())
        except:
            return int(datetime.now().timestamp())
    
    @staticmethod
    def _transform_newsapi_article(article: dict, category: str = "general") -> dict:
        """Transform NewsAPI article to our format."""
        return {
            "headline": article.get("title", "").strip(),
            "source": article.get("source", {}).get("name", "NewsAPI"),
            "url": article.get("url", ""),
            "datetime": IndianStockNewsTool._parse_newsapi_date(article.get("publishedAt", "")),
            "summary": (article.get("description", "") or "")[:200] + "..." if len(article.get("description", "") or "") > 200 else (article.get("description", "") or ""),
            "category": category,
            "image_url": article.get("urlToImage", "")
        }
    
    @staticmethod
    async def get_market_news(max_results: int = 10) -> dict[str, Any]:
        """Fetch general Indian stock market news from NewsAPI."""
        cache_key = "indian_market_news"
        
        if not NEWS_API_KEY:
            logger.error("[IndianStockNews] NEWS_API_KEY not set")
            return {
                "news": [],
                "count": 0,
                "error": "NEWS_API_KEY not configured",
                "source": "newsapi"
            }
        
        # Check cache first (30 min cache for news)
        try:
            cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
            if cached:
                cached_time = cached.get("cached_at")
                if cached_time:
                    cache_dt = datetime.fromisoformat(cached_time)
                    if (datetime.now() - cache_dt).total_seconds() < 1800:  # 30 min
                        logger.info("[IndianStockNews] Returning cached market news")
                        return cached
        except:
            pass
        
        try:
            # Build NewsAPI query for Indian stock market
            url = f"{NEWS_API_BASE_URL}/everything"
            params = {
                "q": '(NSE OR BSE OR "Sensex" OR "Nifty") AND (stock OR market OR shares)',
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_results,
                "apiKey": NEWS_API_KEY
            }
            
            logger.info(f"[IndianStockNews] Calling NewsAPI: {url}")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"[IndianStockNews] NewsAPI error: {error_msg}")
                return {
                    "news": [],
                    "count": 0,
                    "error": error_msg,
                    "source": "newsapi"
                }
            
            articles = data.get("articles", [])
            news_items = [IndianStockNewsTool._transform_newsapi_article(a) for a in articles]
            
            logger.info(f"[IndianStockNews] Fetched {len(news_items)} articles from NewsAPI")
            
            result = {
                "news": news_items,
                "count": len(news_items),
                "source": "newsapi",
                "cached_at": datetime.now().isoformat()
            }
            
            # Cache for 30 minutes
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=1800)
            return result
            
        except Exception as e:
            logger.error(f"[IndianStockNews] Error fetching from NewsAPI: {e}", exc_info=True)
            return {
                "news": [],
                "count": 0,
                "error": str(e),
                "source": "newsapi"
            }

    @staticmethod
    async def get_company_news(symbol: str, max_results: int = 5) -> dict[str, Any]:
        """Fetch news for a specific Indian company from NewsAPI."""
        clean_symbol = symbol.upper().replace(".NS", "").replace(".BO", "")
        cache_key = f"indian_company_news_{clean_symbol}"
        
        if not NEWS_API_KEY:
            return {
                "symbol": clean_symbol,
                "news": [],
                "count": 0,
                "error": "NEWS_API_KEY not configured",
                "source": "newsapi"
            }
        
        # Check cache (2 hour cache)
        try:
            cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
            if cached:
                cached_time = cached.get("cached_at")
                if cached_time:
                    cache_dt = datetime.fromisoformat(cached_time)
                    if (datetime.now() - cache_dt).total_seconds() < 7200:
                        return cached
        except:
            pass
        
        try:
            url = f"{NEWS_API_BASE_URL}/everything"
            params = {
                "q": f"{clean_symbol} (stock OR shares OR company) India",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_results,
                "apiKey": NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                return {
                    "symbol": clean_symbol,
                    "news": [],
                    "count": 0,
                    "error": data.get("message", "NewsAPI error"),
                    "source": "newsapi"
                }
            
            articles = data.get("articles", [])
            news_items = [IndianStockNewsTool._transform_newsapi_article(a, "company") for a in articles]
            
            result = {
                "symbol": clean_symbol,
                "news": news_items,
                "count": len(news_items),
                "source": "newsapi",
                "cached_at": datetime.now().isoformat()
            }
            
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=7200)
            return result
            
        except Exception as e:
            return {
                "symbol": clean_symbol,
                "news": [],
                "count": 0,
                "error": str(e),
                "source": "newsapi"
            }

    @staticmethod
    async def get_category_news(category: str, max_results: int = 10) -> dict[str, Any]:
        """Fetch news by category from NewsAPI."""
        cache_key = f"indian_category_news_{category}"
        
        if not NEWS_API_KEY:
            return {
                "news": [],
                "count": 0,
                "error": "NEWS_API_KEY not configured",
                "category": category,
                "source": "newsapi"
            }
        
        # Check cache (1 hour)
        try:
            cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
            if cached:
                cached_time = cached.get("cached_at")
                if cached_time:
                    cache_dt = datetime.fromisoformat(cached_time)
                    if (datetime.now() - cache_dt).total_seconds() < 3600:
                        return cached
        except:
            pass
        
        # Category queries
        category_queries = {
            "ipo": "India IPO initial public offering listing",
            "merger": "India merger acquisition deal takeover",
            "earnings": "India quarterly earnings results profit",
            "forex": "India rupee dollar forex currency",
            "crypto": "India crypto bitcoin ethereum",
            "general": "Indian stock market NSE BSE Sensex Nifty"
        }
        
        query = category_queries.get(category, category_queries["general"])
        
        try:
            url = f"{NEWS_API_BASE_URL}/everything"
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_results,
                "apiKey": NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                return {
                    "news": [],
                    "count": 0,
                    "error": data.get("message", "NewsAPI error"),
                    "category": category,
                    "source": "newsapi"
                }
            
            articles = data.get("articles", [])
            news_items = [IndianStockNewsTool._transform_newsapi_article(a, category) for a in articles]
            
            result = {
                "news": news_items,
                "count": len(news_items),
                "category": category,
                "source": "newsapi",
                "cached_at": datetime.now().isoformat()
            }
            
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {
                "news": [],
                "count": 0,
                "error": str(e),
                "category": category,
                "source": "newsapi"
            }


# Global instance
indian_stock_news_tool = IndianStockNewsTool()
