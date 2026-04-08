"""
BSE Dividend Data Tool using official BSE India API package.
Fetches real dividend announcements from BSE India without scraping.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, List, Dict
import asyncio
from bse import BSE

logger = logging.getLogger(__name__)

# Popular Indian stocks with their BSE scrip codes
# These are commonly traded stocks on BSE that frequently have dividend announcements
POPULAR_BSE_STOCKS = {
    "RELIANCE": "500325",     # Reliance Industries
    "TCS": "532540",          # Tata Consultancy Services
    "HDFCBANK": "500180",     # HDFC Bank
    "INFY": "500209",         # Infosys
    "ICICIBANK": "532174",    # ICICI Bank
    "KOTAKBANK": "500247",    # Kotak Mahindra Bank
    "HINDUNILVR": "500696",   # Hindustan Unilever
    "ITC": "500875",          # ITC Limited
    "SBIN": "500112",         # State Bank of India
    "BHARTIARTL": "532454",   # Bharti Airtel
    "BAJFINANCE": "500034",    # Bajaj Finance
    "LICI": "543526",         # LIC India
    "ADANIENT": "512599",     # Adani Enterprises
    "ASIANPAINT": "500820",   # Asian Paints
    "MARUTI": "532500",       # Maruti Suzuki
    "TATAMOTORS": "500570",   # Tata Motors
    "AXISBANK": "532215",     # Axis Bank
    "SUNPHARMA": "524715",    # Sun Pharmaceutical
    "ULTRACEMCO": "532538",   # UltraTech Cement
    "ONGC": "500312",         # Oil & Natural Gas Corp
    "WIPRO": "507685",        # Wipro
    "NTPC": "532555",         # NTPC Limited
    "POWERGRID": "532898",    # Power Grid Corp
    "COALINDIA": "533278",    # Coal India
    "TITAN": "500114",        # Titan Company
    "BAJAJFINSV": "500166",   # Bajaj Finserv
    "NESTLEIND": "500790",    # Nestle India
    "ADANIPORTS": "532921",   # Adani Ports
    "GRASIM": "500300",       # Grasim Industries
    "JSWSTEEL": "500228",     # JSW Steel
    "M&M": "500790",          # Mahindra & Mahindra
    "HCLTECH": "532281",      # HCL Technologies
    "ADANIGREEN": "541450",   # Adani Green Energy
    "SBILIFE": "540719",      # SBI Life Insurance
    "TATASTEEL": "500470",    # Tata Steel
}


class BSEDividendAPITool:
    """Tool to fetch dividend announcements from BSE India using official API."""
    
    def __init__(self):
        self.bse = BSE()
        self._rate_limit_delay = 1.0  # 1 second between requests to respect BSE rate limits
    
    async def _rate_limit(self):
        """Simple rate limiting between API calls."""
        await asyncio.sleep(self._rate_limit_delay)
    
    async def get_dividend_announcements(self, days_back: int = 90, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Fetch recent and upcoming dividend announcements from BSE.
        
        Args:
            days_back: Number of days to look back for past dividends
            days_ahead: Number of days to look forward for upcoming dividends
            
        Returns:
            Dictionary with dividends list and metadata
        """
        try:
            logger.info(f"[BSEDividendAPI] Fetching dividend data from BSE (days_back={days_back}, days_ahead={days_ahead})")
            
            dividend_items = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            future_date = datetime.now() + timedelta(days=days_ahead)
            
            # Query corporate actions for each stock
            for symbol, scrip_code in POPULAR_BSE_STOCKS.items():
                try:
                    await self._rate_limit()
                    
                    # Get corporate actions using BSE API
                    actions = self.bse.actions(scrip_code)
                    
                    if actions and 'corporate_actions' in actions:
                        for action in actions['corporate_actions']:
                            # Filter for dividend-related actions
                            purpose = action.get('purpose', '').upper()
                            if any(keyword in purpose for keyword in ['DIVIDEND', 'INTERIM', 'FINAL']):
                                
                                # Parse dates
                                ex_date_str = action.get('ex_date', '')
                                if ex_date_str:
                                    try:
                                        ex_date = datetime.strptime(ex_date_str, '%d-%m-%Y')
                                        
                                        # Include if within our date range
                                        if cutoff_date <= ex_date <= future_date:
                                            # Extract dividend amount from purpose
                                            dividend_amount = self._extract_dividend_amount(purpose)
                                            
                                            dividend_items.append({
                                                "company_name": action.get('company_name', symbol),
                                                "symbol": symbol,
                                                "purpose": action.get('purpose', ''),
                                                "dividend_type": self._get_dividend_type(purpose),
                                                "record_date": action.get('record_date', ''),
                                                "ex_date": ex_date_str,
                                                "announcement_date": action.get('announcement_date', ex_date_str),
                                                "dividend_amount": dividend_amount,
                                                "source": "BSE India API"
                                            })
                                    except ValueError:
                                        logger.debug(f"[BSEDividendAPI] Could not parse date: {ex_date_str}")
                                        continue
                    
                    logger.debug(f"[BSEDividendAPI] Processed {symbol} - found {len([d for d in dividend_items if d['symbol'] == symbol])} dividends")
                    
                except Exception as e:
                    logger.debug(f"[BSEDividendAPI] Error fetching {symbol}: {e}")
                    continue
            
            # Sort by ex_date (most recent first)
            if dividend_items:
                dividend_items.sort(
                    key=lambda x: datetime.strptime(x['ex_date'], '%d-%m-%Y') if x['ex_date'] else datetime.min,
                    reverse=True
                )
            
            result = {
                "dividends": dividend_items,
                "count": len(dividend_items),
                "source": "bse_india_api",
                "queried_stocks": len(POPULAR_BSE_STOCKS),
                "cached_at": datetime.now().isoformat()
            }
            
            logger.info(f"[BSEDividendAPI] Found {len(dividend_items)} dividend announcements from {len(POPULAR_BSE_STOCKS)} stocks")
            return result
            
        except Exception as e:
            logger.error(f"[BSEDividendAPI] Error fetching dividend data: {e}")
            return {
                "dividends": [],
                "count": 0,
                "source": "bse_india_api",
                "error": str(e),
                "cached_at": datetime.now().isoformat()
            }
    
    def _extract_dividend_amount(self, purpose: str) -> float:
        """Extract dividend amount from purpose text."""
        import re
        # Match patterns like "Rs 7.50", "Rs. 10.00", "Rs7.50", etc.
        match = re.search(r'Rs\.?\s*(\d+\.?\d*)', purpose, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 0.0
    
    def _get_dividend_type(self, purpose: str) -> str:
        """Determine dividend type from purpose text."""
        purpose_upper = purpose.upper()
        if 'INTERIM' in purpose_upper:
            return 'interim'
        elif 'FINAL' in purpose_upper:
            return 'final'
        elif 'SPECIAL' in purpose_upper:
            return 'special'
        return 'regular'
    
    async def get_dividends_by_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Get dividend announcements for a specific ticker.
        
        Args:
            ticker: Stock ticker (e.g., "RELIANCE", "TCS", "ITC.NS")
            
        Returns:
            Dictionary with dividends for the specific ticker
        """
        try:
            # Clean ticker (remove .NS, .BO suffixes)
            clean_ticker = ticker.upper().replace('.NS', '').replace('.BO', '').replace('.BSE', '')
            
            # Check if ticker is in our list
            if clean_ticker not in POPULAR_BSE_STOCKS:
                logger.warning(f"[BSEDividendAPI] Ticker {clean_ticker} not in known BSE stocks list")
                return {
                    "dividends": [],
                    "count": 0,
                    "ticker": clean_ticker,
                    "source": "bse_india_api",
                    "note": "Stock not in BSE popular stocks list"
                }
            
            scrip_code = POPULAR_BSE_STOCKS[clean_ticker]
            
            # Get corporate actions for this specific stock
            actions = self.bse.actions(scrip_code)
            dividend_items = []
            
            if actions and 'corporate_actions' in actions:
                for action in actions['corporate_actions']:
                    purpose = action.get('purpose', '').upper()
                    if any(keyword in purpose for keyword in ['DIVIDEND', 'INTERIM', 'FINAL']):
                        dividend_amount = self._extract_dividend_amount(action.get('purpose', ''))
                        
                        dividend_items.append({
                            "company_name": action.get('company_name', clean_ticker),
                            "symbol": clean_ticker,
                            "purpose": action.get('purpose', ''),
                            "dividend_type": self._get_dividend_type(purpose),
                            "record_date": action.get('record_date', ''),
                            "ex_date": action.get('ex_date', ''),
                            "announcement_date": action.get('announcement_date', ''),
                            "dividend_amount": dividend_amount,
                            "source": "BSE India API"
                        })
            
            # Sort by ex_date
            if dividend_items:
                dividend_items.sort(
                    key=lambda x: datetime.strptime(x['ex_date'], '%d-%m-%Y') if x['ex_date'] else datetime.min,
                    reverse=True
                )
            
            return {
                "dividends": dividend_items,
                "count": len(dividend_items),
                "ticker": clean_ticker,
                "source": "bse_india_api",
                "cached_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[BSEDividendAPI] Error fetching dividends for {ticker}: {e}")
            return {
                "dividends": [],
                "count": 0,
                "ticker": clean_ticker if 'clean_ticker' in locals() else ticker,
                "source": "bse_india_api",
                "error": str(e)
            }


# Global instance
bse_dividend_api_tool = BSEDividendAPITool()
