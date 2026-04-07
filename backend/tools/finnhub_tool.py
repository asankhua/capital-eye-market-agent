"""Finnhub API integration for market data."""
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Import the logger from config
from backend.config import logger

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

class FinnhubTool:
    """Tool for fetching market data from Finnhub API."""
    
    def __init__(self):
        # Read API key at runtime, not import time (for HF Secrets compatibility)
        self.api_key = os.getenv("FINNHUB_API_KEY", "").strip()
        self.api_key_source = "HF Secrets" if self.api_key else "NOT SET"
        
        if self.api_key:
            masked_key = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
            logger.info(f"[Finnhub] Initialized with API key from {self.api_key_source}: {masked_key}")
        else:
            logger.error("[Finnhub] NO API KEY FOUND - Check HF Secrets for FINNHUB_API_KEY")
            raise ValueError("FINNHUB_API_KEY not set in environment")
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated request to Finnhub API."""
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY not set")
        
        url = f"{FINNHUB_BASE_URL}/{endpoint}"
        params = params or {}
        params["token"] = self.api_key
        
        try:
            logger.info(f"[Finnhub] Requesting: {endpoint}")
            response = requests.get(url, params=params, timeout=15)
            logger.info(f"[Finnhub] Response status: {response.status_code}")
            
            response.raise_for_status()
            
            if not response.text:
                logger.error("[Finnhub] Empty response")
                raise RuntimeError("Empty response from Finnhub API")
            
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"[Finnhub] JSON parse error: {e}, text: {response.text[:500]}")
                raise RuntimeError(f"Invalid JSON response: {e}")
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"[Finnhub] API request failed: {e}")
            raise RuntimeError(f"Finnhub API request failed: {e}")
    
    def get_earnings_calendar(self, symbol: Optional[str] = None, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get earnings calendar from Finnhub API."""
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        params = {"from": from_date, "to": to_date}
        if symbol:
            params["symbol"] = symbol
        
        data = self._make_request("calendar/earnings", params)
        
        if not data or "earningsCalendar" not in data:
            logger.error(f"[Finnhub] Invalid earnings response: {data}")
            raise RuntimeError("Invalid response from Finnhub API for earnings calendar")
        
        earnings = []
        for item in data.get("earningsCalendar", []):
            earnings.append({
                "symbol": item.get("symbol", ""),
                "date": item.get("date", ""),
                "epsEstimate": item.get("epsEstimate"),
                "revenueEstimate": item.get("revenueEstimate"),
                "fiscalPeriod": item.get("period", "")
            })
        
        return earnings
    
    def get_market_news(self, category: str = "general", symbol: Optional[str] = None) -> List[Dict]:
        """Get market news from Finnhub API."""
        if symbol:
            # Company-specific news
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            data = self._make_request("company-news", {
                "symbol": symbol,
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d")
            })
            
            if not data or not isinstance(data, list):
                logger.error(f"[Finnhub] Invalid company news response for {symbol}: {data}")
                raise RuntimeError(f"Invalid response from Finnhub API for company news: {symbol}")
            
            news = []
            for item in data[:10]:
                news.append({
                    "datetime": item.get("datetime", 0),
                    "headline": item.get("headline", ""),
                    "source": item.get("source", ""),
                    "summary": item.get("summary", ""),
                    "url": item.get("url", "")
                })
            return news
        else:
            # General market news
            data = self._make_request("news", {"category": category})
            
            if not data or not isinstance(data, list):
                logger.error(f"[Finnhub] Invalid market news response: {data}")
                raise RuntimeError("Invalid response from Finnhub API for market news")
            
            news = []
            for item in data[:10]:
                news.append({
                    "datetime": item.get("datetime", 0),
                    "headline": item.get("headline", ""),
                    "source": item.get("source", ""),
                    "summary": item.get("summary", ""),
                    "url": item.get("url", "")
                })
            return news
    
    def get_market_movers(self, mover_type: str = "gainers") -> List[Dict]:
        """Get market movers (gainers/losers/most active) from Finnhub."""
        # Map our types to Finnhub types
        type_mapping = {
            "gainers": "percent_change_gainers",
            "losers": "percent_change_losers", 
            "active": "most_actives"
        }
        
        data = self._make_request("stock/market movers", {
            "exchange": "US",
            "type": type_mapping.get(mover_type, "percent_change_gainers")
        })
        
        if not data or "data" not in data:
            logger.error(f"[Finnhub] Invalid response for market movers: {data}")
            raise RuntimeError("Invalid response from Finnhub API for market movers")
        
        # Transform Finnhub format to our format
        movers = []
        for item in data.get("data", []):
            movers.append({
                "symbol": item.get("symbol", ""),
                "name": item.get("name", item.get("symbol", "")),
                "price": item.get("price", 0),
                "change": item.get("change", 0),
                "change_percent": item.get("percent_change", 0),
                "volume": item.get("volume", 0)
            })
        
        return movers
    
    def get_sector_performance(self) -> List[Dict]:
        """Get sector performance data from Finnhub API."""
        data = self._make_request("stock/sector")
        
        if not data:
            logger.error("[Finnhub] Invalid sector performance response")
            raise RuntimeError("Invalid response from Finnhub API for sector performance")
        
        # Transform to our format
        sectors = []
        for sector_name, performance in data.items():
            if isinstance(performance, dict):
                change_pct = performance.get("change_percentage", 0)
                sectors.append({
                    "name": sector_name.replace("_", " ").title(),
                    "change_percent": round(change_pct, 2)
                })
        
        return sectors
    
    def get_company_news(self, symbol: str) -> List[Dict]:
        """Get news for specific company."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = self._make_request("company-news", {
            "symbol": symbol,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d")
        })
        
        if not data or not isinstance(data, list):
            logger.error(f"[Finnhub] Invalid company news response for {symbol}")
            raise RuntimeError(f"Invalid response from Finnhub API for company news: {symbol}")
        
        news = []
        for item in data[:5]:
            news.append({
                "datetime": item.get("datetime", 0),
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
                "summary": item.get("summary", ""),
                "url": item.get("url", "")
            })
        
        return news
    
    def get_earnings_calendar(self, symbol: str = None, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get earnings calendar."""
        if not self.api_key:
            return DUMMY_EARNINGS
        
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        params = {"from": from_date, "to": to_date}
        if symbol:
            params["symbol"] = symbol
        
        data = self._make_request("calendar/earnings", params)
        
        if not data or "earningsCalendar" not in data:
            logger.error(f"[Finnhub] Invalid earnings response: {data}")
            raise RuntimeError("Invalid response from Finnhub API for earnings calendar")
        
        earnings = []
        for item in data.get("earningsCalendar", []):
            earnings.append({
                "symbol": item.get("symbol", ""),
                "date": item.get("date", ""),
                "epsEstimate": item.get("epsEstimate"),
                "revenueEstimate": item.get("revenueEstimate"),
                "fiscalPeriod": item.get("period", "")
            })
        
        return earnings
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get stock quote from Finnhub API."""
        data = self._make_request("quote", {"symbol": symbol})
        
        if not data:
            logger.error(f"[Finnhub] Invalid quote response for {symbol}")
            raise RuntimeError(f"Invalid response from Finnhub API for quote: {symbol}")
        
        return data
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get company profile from Finnhub API."""
        data = self._make_request("stock/profile2", {"symbol": symbol})
        
        if not data:
            logger.error(f"[Finnhub] Invalid profile response for {symbol}")
            raise RuntimeError(f"Invalid response from Finnhub API for profile: {symbol}")
        
        return data

# Global instance
finnhub_tool = FinnhubTool()
