"""Indian Stock News Tool - Fetches Indian stock market news using RSS feeds.

Provides:
  - Indian stock news from Moneycontrol, Economic Times, Mint, NDTV Profit
  - Market updates, IPO news, company announcements
  - No API key required
"""

import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any
import requests

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.tools.indian_stock_news")


class IndianStockNewsTool:
    """Tool for fetching Indian stock market news using RSS feeds with Indian market filtering."""

    RSS_FEEDS = {
        "moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
        "economictimes": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "mint": "https://www.livemint.com/rss/news",
        "ndtvprofit": "https://www.ndtvprofit.com/rss/news",
        "zeebiz": "https://www.zeebiz.com/rss/news.xml"
    }

    # Keywords to filter for Indian stock market relevance
    INDIAN_MARKET_KEYWORDS = [
        # Market indices
        'sensex', 'nifty', 'nifty 50', 'nse', 'bse', 'nse india', 'bse india',
        # Market terms
        'stock market', 'share market', 'equity', 'stocks', 'shares', 'scrip',
        'market update', 'market news', 'trading', 'investor', 'portfolio',
        # Corporate actions
        'dividend', 'bonus', 'split', 'ipo', 'listing', 'earnings', 'results',
        'quarterly', 'annual report', 'agm', 'board meeting',
        # Indian companies
        'reliance', 'tcs', 'infosys', 'hdfc', 'icici', 'sbi', 'axis', 'kotak',
        'itc', 'hul', 'bharti', 'larsen', 'l&t', 'coal india', 'ongc', 'ntpc',
        'bajaj', 'asian paints', 'nestle', 'maruti', 'mahindra', 'tata',
        # Sectors
        'banking', 'it sector', 'pharma', 'auto', 'fmcg', 'oil', 'gas',
        # Regulatory
        'sebi', 'rbi', 'reserve bank', 'finance ministry', 'budget', 'tax',
        # Economic indicators
        'gdp', 'inflation', 'interest rate', 'repo rate', 'rupee', 'forex'
    ]

    @staticmethod
    def _is_indian_market_relevant(title: str, description: str = "") -> bool:
        """Check if news is relevant to Indian stock market."""
        text = (title + " " + description).lower()
        return any(keyword.lower() in text for keyword in IndianStockNewsTool.INDIAN_MARKET_KEYWORDS)
    @staticmethod
    def _parse_rss_feed(feed_url: str, source_name: str, max_items: int = 10) -> list[dict]:
        """Parse an RSS feed and return news items filtered for Indian market relevance."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            
            # Handle both RSS 2.0 and Atom formats
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            news_items = []
            for item in items:
                title = item.findtext('title', '') or item.findtext('.//{http://www.w3.org/2005/Atom}title', '')
                link = item.findtext('link', '') or item.findtext('.//{http://www.w3.org/2005/Atom}link', '')
                description = item.findtext('description', '') or item.findtext('.//{http://www.w3.org/2005/Atom}summary', '')
                pub_date = item.findtext('pubDate', '') or item.findtext('.//{http://www.w3.org/2005/Atom}published', '')
                
                title = (title or "").strip()
                description_clean = description or ""
                
                # Clean up HTML from description
                try:
                    description_clean = ET.fromstring(f'<root>{description_clean}</root>').text or description_clean
                except:
                    pass
                
                # Filter for Indian market relevance
                if not IndianStockNewsTool._is_indian_market_relevant(title, description_clean):
                    continue
                
                news_items.append({
                    "headline": title,
                    "source": source_name,
                    "url": (link or "").strip(),
                    "datetime": IndianStockNewsTool._parse_date(pub_date) if pub_date else int(datetime.now().timestamp()),
                    "summary": (description_clean[:200] + "..." if len(description_clean) > 200 else description_clean) if description_clean else "",
                    "category": "general"
                })
                
                if len(news_items) >= max_items:
                    break
            
            logger.info(f"[IndianStockNews] Fetched {len(news_items)} relevant items from {source_name}")
            return news_items
        except Exception as e:
            logger.warning(f"[IndianStockNews] Failed to fetch from {source_name}: {e}")
            return []

    @staticmethod
    def _parse_date(date_str: str) -> int:
        """Parse various date formats to timestamp."""
        try:
            formats = [
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%SZ"
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue
            return int(datetime.now().timestamp())
        except:
            return int(datetime.now().timestamp())

    @staticmethod
    async def get_market_news(max_results: int = 10) -> dict[str, Any]:
        """Fetch general Indian stock market news from RSS feeds with filtering."""
        cache_key = "indian_market_news"
        logger.info(f"[IndianStockNews] Fetching market news from RSS feeds with Indian market filter")
        
        cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if cache_dt.date() == datetime.now().date():
                    logger.info(f"[IndianStockNews] Returning cached news from today")
                    return cached

        try:
            # Fetch from all RSS feeds
            all_news = []
            for source_name, feed_url in IndianStockNewsTool.RSS_FEEDS.items():
                news = IndianStockNewsTool._parse_rss_feed(feed_url, source_name, max_items=5)
                all_news.extend(news)
            
            # Sort by datetime (newest first)
            all_news.sort(key=lambda x: x["datetime"], reverse=True)
            
            result = {
                "news": all_news[:max_results],
                "count": len(all_news[:max_results]),
                "source": "rss_feeds",
                "cached_at": datetime.now().isoformat()
            }
            logger.info(f"[IndianStockNews] Total filtered news items: {len(all_news)}")

            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"[IndianStockNews] Error fetching news from RSS: {e}", exc_info=True)
            return {
                "news": [],
                "count": 0,
                "error": str(e),
                "source": "rss_feeds"
            }

    @staticmethod
    async def get_company_news(symbol: str, max_results: int = 5) -> dict[str, Any]:
        """Fetch news for a specific Indian company from RSS feeds."""
        clean_symbol = symbol.upper().replace(".NS", "").replace(".BO", "")
        cache_key = f"indian_company_news_{clean_symbol}"
        
        cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if cache_dt.date() == datetime.now().date():
                    return cached

        try:
            # Fetch from all RSS feeds and filter for company mentions
            all_news = []
            for source_name, feed_url in IndianStockNewsTool.RSS_FEEDS.items():
                news = IndianStockNewsTool._parse_rss_feed(feed_url, source_name, max_items=10)
                # Filter news containing the company symbol/name
                for item in news:
                    if clean_symbol.lower() in item["headline"].lower() or clean_symbol.lower() in item["summary"].lower():
                        item["category"] = "company"
                        all_news.append(item)
            
            # Sort by datetime (newest first)
            all_news.sort(key=lambda x: x["datetime"], reverse=True)
            
            result = {
                "symbol": clean_symbol,
                "news": all_news[:max_results],
                "count": len(all_news[:max_results]),
                "source": "rss_feeds",
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
                "source": "rss_feeds"
            }

    @staticmethod
    async def get_category_news(category: str, max_results: int = 10) -> dict[str, Any]:
        """Fetch news by category from RSS feeds."""
        cache_key = f"indian_category_news_{category}"
        cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if cache_dt.date() == datetime.now().date():
                    return cached

        # Category keywords to filter news
        category_keywords = {
            "ipo": ["ipo", "initial public offering", "listing", "public issue"],
            "merger": ["merger", "acquisition", "deal", "takeover"],
            "earnings": ["earnings", "results", "profit", "loss", "revenue", "quarterly"],
            "forex": ["rupee", "dollar", "forex", "currency"],
            "crypto": ["crypto", "bitcoin", "ethereum"],
            "general": []  # No filter for general
        }

        keywords = category_keywords.get(category, [])

        try:
            # Fetch from all RSS feeds and filter by category keywords
            all_news = []
            for source_name, feed_url in IndianStockNewsTool.RSS_FEEDS.items():
                news = IndianStockNewsTool._parse_rss_feed(feed_url, source_name, max_items=5)
                for item in news:
                    text = (item["headline"] + " " + item["summary"]).lower()
                    # If no keywords (general) or matches keywords
                    if not keywords or any(kw in text for kw in keywords):
                        item["category"] = category
                        all_news.append(item)
            
            # Sort by datetime (newest first)
            all_news.sort(key=lambda x: x["datetime"], reverse=True)

            result = {
                "news": all_news[:max_results],
                "count": len(all_news[:max_results]),
                "category": category,
                "source": "rss_feeds",
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
                "source": "rss_feeds"
            }


# Global instance
indian_stock_news_tool = IndianStockNewsTool()
