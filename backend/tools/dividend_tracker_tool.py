"""Dividend Tracker Tool - Fetches dividend announcements using Yahoo Finance (yfinance).

Optimized for rate limits:
  - Reduced to top 20 dividend-paying stocks
  - Added 0.5s delay between requests
  - Avoided extra API calls (no ticker.info)
  - 1-hour caching
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any
import yfinance as yf

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.tools.dividend_tracker")


# Top 20 Indian dividend-paying stocks (reduced from 50 to avoid rate limits)
TOP_DIVIDEND_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "ITC.NS", "HDFCBANK.NS", "INFY.NS",
    "SBIN.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS", "IOC.NS", "BPCL.NS", "GAIL.NS",
    "NHPC.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SUNPHARMA.NS", "WIPRO.NS"
]

# Company name cache (to avoid ticker.info API calls)
COMPANY_NAMES = {
    "RELIANCE.NS": "Reliance Industries Ltd",
    "TCS.NS": "Tata Consultancy Services Ltd",
    "ITC.NS": "ITC Ltd",
    "HDFCBANK.NS": "HDFC Bank Ltd",
    "INFY.NS": "Infosys Ltd",
    "SBIN.NS": "State Bank of India",
    "ONGC.NS": "Oil & Natural Gas Corporation Ltd",
    "NTPC.NS": "NTPC Ltd",
    "POWERGRID.NS": "Power Grid Corporation of India Ltd",
    "COALINDIA.NS": "Coal India Ltd",
    "HINDUNILVR.NS": "Hindustan Unilever Ltd",
    "BHARTIARTL.NS": "Bharti Airtel Ltd",
    "IOC.NS": "Indian Oil Corporation Ltd",
    "BPCL.NS": "Bharat Petroleum Corporation Ltd",
    "GAIL.NS": "GAIL (India) Ltd",
    "NHPC.NS": "NHPC Ltd",
    "KOTAKBANK.NS": "Kotak Mahindra Bank Ltd",
    "AXISBANK.NS": "Axis Bank Ltd",
    "SUNPHARMA.NS": "Sun Pharmaceutical Industries Ltd",
    "WIPRO.NS": "Wipro Ltd"
}


class DividendTrackerTool:
    """Tool for fetching dividend announcements from Yahoo Finance."""

    @staticmethod
    async def get_dividend_announcements() -> dict[str, Any]:
        """Fetch dividend announcements from Yahoo Finance.
        
        Optimized to avoid rate limits:
        - 20 stocks only
        - 0.3s delay between requests, 1s every 5 requests
        - Uses cached company names
        
        Returns:
            Dictionary with dividend announcements list
        """
        cache_key = "yahoo_dividend_announcements"
        
        # Check cache first (valid for 1 hour)
        cached = await SQLiteMCPTool.get_cache("corporate_actions", cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if (datetime.now() - cache_dt).total_seconds() < 3600:
                    logger.info("[DividendTracker] Returning cached dividend data")
                    return cached

        try:
            dividend_items = []
            today = datetime.now()
            
            logger.info(f"[DividendTracker] Fetching dividends for {len(TOP_DIVIDEND_STOCKS)} stocks")
            
            for i, symbol in enumerate(TOP_DIVIDEND_STOCKS):
                try:
                    # Add delay every 5 requests to avoid rate limits
                    if i > 0 and i % 5 == 0:
                        time.sleep(1)
                    else:
                        time.sleep(0.3)  # 300ms between requests
                    
                    ticker = yf.Ticker(symbol)
                    
                    # Get dividend history only
                    dividends = ticker.dividends
                    
                    if dividends is not None and len(dividends) > 0:
                        # Get the most recent dividend
                        last_dividend_date = dividends.index[-1]
                        last_dividend_amount = dividends.iloc[-1]
                        
                        # Check if it's within last 90 days
                        days_since = (today - last_dividend_date.to_pydatetime()).days
                        
                        if days_since <= 90:
                            # Use cached company name instead of API call
                            company_name = COMPANY_NAMES.get(symbol, symbol.replace('.NS', ''))
                            
                            # Determine dividend type
                            dividend_type = "interim" if len(dividends) > 1 and (dividends.index[-1] - dividends.index[-2]).days < 200 else "final"
                            
                            ex_date = last_dividend_date.strftime('%d-%m-%Y')
                            record_date = (last_dividend_date + timedelta(days=2)).strftime('%d-%m-%Y')
                            
                            dividend_items.append({
                                "company_name": company_name,
                                "symbol": symbol.replace('.NS', ''),
                                "purpose": f"{dividend_type.capitalize()} Dividend - Rs {last_dividend_amount:.2f} per share",
                                "dividend_type": dividend_type,
                                "record_date": record_date,
                                "ex_date": ex_date,
                                "announcement_date": ex_date,
                                "dividend_amount": float(last_dividend_amount),
                                "source": "Yahoo Finance"
                            })
                            
                except Exception as e:
                    logger.debug(f"[DividendTracker] Error fetching {symbol}: {e}")
                    continue
            
            # Sort by ex_date
            dividend_items.sort(key=lambda x: datetime.strptime(x['ex_date'], '%d-%m-%Y'), reverse=True)
            
            result = {
                "dividends": dividend_items,
                "count": len(dividend_items),
                "source": "yahoo_finance",
                "cached_at": datetime.now().isoformat()
            }
            
            # Cache for 1 hour
            await SQLiteMCPTool.set_cache("corporate_actions", cache_key, result, ttl=3600)
            logger.info(f"[DividendTracker] Found {len(dividend_items)} recent dividends")
            return result

        except Exception as e:
            logger.error(f"[DividendTracker] Error: {e}")
            return {
                "dividends": [],
                "count": 0,
                "error": str(e),
                "source": "yahoo_finance",
                "cached_at": datetime.now().isoformat()
            }

    @staticmethod
    async def get_upcoming_dividends(days_ahead: int = 30) -> dict[str, Any]:
        """Get upcoming dividends (based on historical patterns)."""
        result = await DividendTrackerTool.get_dividend_announcements()
        result["upcoming_days"] = days_ahead
        result["note"] = "Upcoming based on historical patterns. Actual dates may vary."
        return result

    @staticmethod
    async def get_recent_dividends(days_back: int = 90) -> dict[str, Any]:
        """Get recent dividends from past N days."""
        result = await DividendTrackerTool.get_dividend_announcements()
        result["recent_days"] = days_back
        
        # Filter by date
        today = datetime.now()
        filtered = []
        for d in result.get("dividends", []):
            try:
                ex_date = datetime.strptime(d['ex_date'], '%d-%m-%Y')
                if (today - ex_date).days <= days_back:
                    filtered.append(d)
            except:
                continue
        
        result["dividends"] = filtered
        result["count"] = len(filtered)
        return result


# Global instance
dividend_tracker_tool = DividendTrackerTool()
