"""BSE Corporate Actions - Fetches dividend announcements from BSE India API.

Uses direct HTTP requests to BSE official API - no external library dependencies.
Includes caching to minimize API calls and respect rate limits.
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.tools.bse_dividend")


class BSEDividendTool:
    """Tool for fetching Indian stock dividend data from BSE Corporate Actions."""
    
    def __init__(self):
        self.base_url = "https://api.bseindia.com/BseIndiaAPI/api"
        self.session = requests.Session()
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.bseindia.com/',
            'Origin': 'https://www.bseindia.com'
        })
        self._last_request_time = 0
        self._min_request_interval = 2  # Minimum seconds between requests to respect rate limits
        logger.info("[BSEDividendTool] Initialized with BSE API")
    
    def _rate_limit(self):
        """Ensure we don't make requests too frequently."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            logger.debug(f"[BSEDividendTool] Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()
        
    def _parse_amount(self, purpose: str) -> Optional[float]:
        """Extract dividend amount from purpose string."""
        import re
        try:
            # Match patterns like "Rs. 6.50", "Rs 6.50", "Rs.6.50", "Dividend Rs. 6.50"
            match = re.search(r'Rs\.?\s*([\d.]+)', purpose, re.IGNORECASE)
            if match:
                return float(match.group(1))
            return None
        except:
            return None
    
    def _extract_dividend_type(self, purpose: str) -> str:
        """Extract dividend type from purpose string."""
        purpose_lower = purpose.lower()
        if 'interim' in purpose_lower:
            return 'Interim'
        elif 'final' in purpose_lower:
            return 'Final'
        elif 'special' in purpose_lower:
            return 'Special'
        return 'Regular'
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and format date string."""
        if not date_str:
            return ''
        try:
            for fmt in ['%d-%b-%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.strftime('%Y-%m-%d')
                except:
                    continue
            return date_str
        except:
            return date_str
        
    async def get_dividend_announcements(self, ticker: str = None) -> Dict[str, Any]:
        """Get dividend announcements from BSE Corporate Actions.
        
        Args:
            ticker: Stock ticker symbol (e.g., "ITC", "RELIANCE"). If None, returns all recent dividends.
            
        Returns:
            dict with dividend information from BSE
        """
        cache_key = f"bse_dividends_{ticker or 'ALL'}_{datetime.now().strftime('%Y%m%d')}"
        
        # Check cache first (cache for 1 hour)
        try:
            cached = await SQLiteMCPTool.get_cache("bse_dividends", cache_key)
            if cached:
                cached_time = cached.get("cached_at")
                if cached_time:
                    cache_dt = datetime.fromisoformat(cached_time)
                    # Cache valid for 1 hour
                    if (datetime.now() - cache_dt).total_seconds() < 3600:
                        logger.info(f"[BSEDividendTool] Returning cached dividend data for {ticker or 'all stocks'}")
                        return cached
        except Exception as e:
            logger.warning(f"[BSEDividendTool] Cache check failed: {e}")
        
        logger.info(f"[BSEDividendTool] Fetching dividend announcements for {ticker or 'all stocks'}")
        
        # Rate limit check
        self._rate_limit()
        
        try:
            # BSE Corporate Actions API endpoint
            # Get last 30 days of corporate actions
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            to_date = datetime.now().strftime('%Y%m%d')
            
            url = f"{self.base_url}/CorpAction/w"
            
            params = {
                'FromDate': from_date,
                'ToDate': to_date,
                'Flag': 'DI'  # Dividend announcements
            }
            
            logger.info(f"[BSEDividendTool] Calling BSE API: {url}")
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            # Parse response - BSE returns JSON
            data = response.json()
            
            if not data or not isinstance(data, list):
                logger.warning("[BSEDividendTool] No data returned from BSE API")
                return self._get_error_response(ticker, "No data from BSE API")
            
            dividends = []
            for item in data:
                symbol = item.get('scrip_code', item.get('security_code', ''))
                if not symbol:
                    continue
                
                # Filter by ticker if specified
                if ticker:
                    clean_ticker = ticker.upper().replace('.NS', '').replace('.BO', '')
                    if clean_ticker not in symbol.upper():
                        continue
                
                purpose = item.get('purpose', '')
                if not purpose or 'dividend' not in purpose.lower():
                    continue
                    
                dividend = {
                    'ticker': str(symbol).replace('.NS', '').replace('.BO', '').strip(),
                    'company_name': item.get('security_name', item.get('company_name', symbol)),
                    'dividend_amount': self._parse_amount(purpose),
                    'dividend_type': self._extract_dividend_type(purpose),
                    'ex_dividend_date': self._parse_date(item.get('ex_date', item.get('exDate', ''))),
                    'record_date': self._parse_date(item.get('record_date', item.get('recDate', ''))),
                    'announcement_date': self._parse_date(item.get('annc_date', item.get('anncDate', ''))),
                    'source': 'BSE Corporate Actions'
                }
                dividends.append(dividend)
            
            logger.info(f"[BSEDividendTool] Found {len(dividends)} dividend announcements from BSE")
            
            if not dividends:
                return self._get_error_response(ticker, "No dividend announcements found")
            
            # Prepare result
            result = {
                'ticker': ticker or 'ALL',
                'company_name': 'Multiple Companies' if not ticker else dividends[0]['company_name'],
                'announcements': dividends,
                'count': len(dividends),
                'source': 'BSE Corporate Actions',
                'search_date': datetime.now().strftime("%d %B %Y"),
                'error': None,
                'cached_at': datetime.now().isoformat()
            }
            
            # Cache the result
            try:
                await SQLiteMCPTool.set_cache("bse_dividends", cache_key, result, ttl=3600)
                logger.info(f"[BSEDividendTool] Cached dividend data for {ticker or 'all stocks'}")
            except Exception as e:
                logger.warning(f"[BSEDividendTool] Failed to cache data: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"[BSEDividendTool] Error fetching from BSE: {e}", exc_info=True)
            return self._get_error_response(ticker, str(e))
    
    def _get_error_response(self, ticker: str = None, error_msg: str = "") -> Dict[str, Any]:
        """Return error response - NO sample data."""
        if ticker:
            clean_ticker = ticker.upper().replace('.NS', '').replace('.BO', '')
            return {
                'ticker': clean_ticker,
                'company_name': clean_ticker,
                'announcements': [],
                'count': 0,
                'source': 'BSE Corporate Actions - Error',
                'search_date': datetime.now().strftime("%d %B %Y"),
                'error': f'Failed to fetch dividend data: {error_msg}'
            }
        
        return {
            'ticker': 'ALL',
            'company_name': 'Multiple Companies',
            'announcements': [],
            'count': 0,
            'source': 'BSE Corporate Actions - Error',
            'search_date': datetime.now().strftime("%d %B %Y"),
            'error': f'Failed to fetch dividend data: {error_msg}'
        }


# Global instance
bse_dividend_tool = BSEDividendTool()


# Export - keep old name for compatibility
nse_dividend_tool = bse_dividend_tool
__all__ = ['bse_dividend_tool', 'nse_dividend_tool', 'BSEDividendTool']
