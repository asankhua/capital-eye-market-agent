"""Indian Stock News Tool - Fetches Indian stock market news using Google News RSS.

Provides:
  - Indian stock news from Google News RSS feed
  - Market updates, IPO news, company announcements
  - No API key required
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
import requests
import xml.etree.ElementTree as ET

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.tools.indian_stock_news")


class IndianStockNewsTool:
    """Tool for fetching Indian stock market news using Google News RSS."""

    # Google News RSS feed for Indian stock market
    GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q=india+stock+market&hl=en-IN&gl=IN&ceid=IN:en"

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
        """Parse an RSS feed and return news items."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            
            # Handle both RSS 2.0 and Atom formats
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            logger.info(f"[IndianStockNews] Found {len(items)} items in RSS feed from {source_name}")
            
            news_items = []
            import re
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    pub_date_elem = item.find('pubDate')
                    source_elem = item.find('source')
                    
                    # Extract text content
                    title = title_elem.text if title_elem is not None and title_elem.text else ''
                    link = link_elem.text if link_elem is not None and link_elem.text else ''
                    description = desc_elem.text if desc_elem is not None and desc_elem.text else ''
                    pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else ''
                    
                    # Get source from source element or use default
                    source = source_name
                    if source_elem is not None and source_elem.text:
                        source = source_elem.text
                    
                    title = title.strip()
                    link = link.strip()
                    
                    # Clean up HTML tags from description
                    if description:
                        description_clean = re.sub(r'<[^>]+>', '', description)
                        description_clean = re.sub(r'\s+', ' ', description_clean).strip()
                    else:
                        description_clean = title
                    
                    # Skip if no title or link
                    if not title or not link:
                        continue
                    
                    news_items.append({
                        "headline": title,
                        "source": source,
                        "url": link,
                        "datetime": IndianStockNewsTool._parse_date(pub_date) if pub_date else int(datetime.now().timestamp()),
                        "summary": (description_clean[:200] + "..." if len(description_clean) > 200 else description_clean),
                        "category": "general"
                    })
                    
                    if len(news_items) >= max_items:
                        break
                except Exception as item_error:
                    logger.warning(f"[IndianStockNews] Error parsing item: {item_error}")
                    continue
            
            logger.info(f"[IndianStockNews] Successfully parsed {len(news_items)} items from {source_name}")
            return news_items
        except Exception as e:
            logger.error(f"[IndianStockNews] Failed to fetch from {source_name}: {e}")
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
    async def get_market_news(max_results: int = 10, bypass_cache: bool = False) -> dict[str, Any]:
        """Fetch Indian stock market news from Google News RSS."""
        cache_key = "indian_market_news"
        
        # Check cache unless bypass is requested
        if not bypass_cache:
            cached = await SQLiteMCPTool.get_cache("indian_news", cache_key)
            if cached:
                cached_time = cached.get("cached_at")
                if cached_time:
                    cache_dt = datetime.fromisoformat(cached_time)
                    if cache_dt.date() == datetime.now().date():
                        if cached.get("news"):
                            return cached

        try:
            # Fetch from Google News RSS
            news = IndianStockNewsTool._parse_rss_feed(IndianStockNewsTool.GOOGLE_NEWS_RSS_URL, "Google News", max_items=max_results)
            
            result = {
                "news": news,
                "count": len(news),
                "source": "google_news_rss",
                "cached_at": datetime.now().isoformat()
            }
            
            await SQLiteMCPTool.set_cache("indian_news", cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"[IndianStockNews] Error fetching news from Google RSS: {e}")
            # Return empty array on error - no sample data
            return {
                "news": [],
                "count": 0,
                "source": "google_news_rss",
                "error": str(e),
                "cached_at": datetime.now().isoformat()
            }

    @staticmethod
    def _get_sample_news(max_results: int = 10) -> list[dict]:
        """Return sample Indian market news when RSS feeds fail."""
        return [
            {
                "headline": "Sensex closes at record high amid strong buying in banking stocks",
                "source": "Sample Data",
                "url": "https://www.moneycontrol.com",
                "datetime": int(datetime.now().timestamp()),
                "summary": "The BSE Sensex ended at a new record high, driven by strong buying in banking and financial stocks. Nifty also closed higher.",
                "category": "general"
            },
            {
                "headline": "RBI keeps repo rate unchanged at 6.5%, maintains neutral stance",
                "source": "Sample Data",
                "url": "https://www.moneycontrol.com",
                "datetime": int(datetime.now().timestamp()) - 3600,
                "summary": "The Reserve Bank of India decided to keep the repo rate unchanged at 6.5% while maintaining a neutral monetary policy stance.",
                "category": "general"
            },
            {
                "headline": "FIIs net buyers in Indian equities for third consecutive month",
                "source": "Sample Data",
                "url": "https://www.moneycontrol.com",
                "datetime": int(datetime.now().timestamp()) - 7200,
                "summary": "Foreign Institutional Investors continued their buying streak in Indian equities for the third month in a row.",
                "category": "general"
            },
            {
                "headline": "IT sector leads gains as rupee weakens against dollar",
                "source": "Sample Data",
                "url": "https://www.moneycontrol.com",
                "datetime": int(datetime.now().timestamp()) - 10800,
                "summary": "IT stocks surged on BSE and NSE as the weakening rupee boosted export earnings for IT companies.",
                "category": "general"
            },
            {
                "headline": "IPO market sees robust activity with 15 new listings in Q1",
                "source": "Sample Data",
                "url": "https://www.moneycontrol.com",
                "datetime": int(datetime.now().timestamp()) - 14400,
                "summary": "The Indian IPO market witnessed strong activity in Q1 with 15 new listings, raising over Rs 50,000 crore.",
                "category": "general"
            }
        ][:max_results]

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
