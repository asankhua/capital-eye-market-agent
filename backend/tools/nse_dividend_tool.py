"""NSE Corporate Actions - Fetches dividend announcements from NSE India API.

Uses nsefin library to fetch official NSE corporate actions data.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("market_analyst.tools.nse_dividend")

# Try to import nsefin
try:
    from nsefin import NSE
    NSEFIN_AVAILABLE = True
    logger.info("[NSEDividendTool] nsefin library available")
except ImportError:
    NSEFIN_AVAILABLE = False
    logger.warning("[NSEDividendTool] nsefin library not available")


class NSEDividendTool:
    """Tool for fetching Indian stock dividend data from NSE Corporate Actions."""
    
    def __init__(self):
        self.nse = None
        if NSEFIN_AVAILABLE:
            try:
                self.nse = NSE()
                logger.info("[NSEDividendTool] Initialized NSE connection")
            except Exception as e:
                logger.error(f"[NSEDividendTool] Failed to initialize NSE: {e}")
        
    async def get_dividend_announcements(self, ticker: str = None) -> Dict[str, Any]:
        """Get dividend announcements from NSE Corporate Actions.
        
        Args:
            ticker: Stock ticker symbol (e.g., "ITC", "RELIANCE"). If None, returns all recent dividends.
            
        Returns:
            dict with dividend information from NSE
        """
        logger.info(f"[NSEDividendTool] Fetching dividend announcements for {ticker or 'all stocks'}")
        
        if not NSEFIN_AVAILABLE or self.nse is None:
            logger.error("[NSEDividendTool] nsefin not available")
            return self._get_sample_data(ticker)
        
        try:
            # Fetch corporate actions with dividend filter
            logger.info("[NSEDividendTool] Calling NSE get_corporate_actions")
            df = self.nse.get_corporate_actions(subject_filter="dividend")
            
            if df is None or df.empty:
                logger.warning("[NSEDividendTool] No dividend data returned from NSE")
                return self._get_sample_data(ticker)
            
            # Convert DataFrame to list of dicts
            dividends = []
            for _, row in df.iterrows():
                dividend = {
                    'ticker': str(row.get('symbol', '')).replace('.NS', '').replace('.BO', '').strip(),
                    'company_name': str(row.get('company', row.get('symbol', ''))),
                    'dividend_amount': float(row.get('amount', 0)) if pd.notna(row.get('amount')) else None,
                    'dividend_type': str(row.get('type', 'Regular')),
                    'ex_dividend_date': str(row.get('ex_date', row.get('exDate', ''))),
                    'record_date': str(row.get('record_date', row.get('recordDate', ''))),
                    'announcement_date': str(row.get('announcement_date', row.get('announcementDate', ''))),
                    'source': 'NSE Corporate Actions'
                }
                dividends.append(dividend)
            
            logger.info(f"[NSEDividendTool] Found {len(dividends)} dividend announcements")
            
            # Filter by ticker if specified
            if ticker:
                clean_ticker = ticker.upper().replace('.NS', '').replace('.BO', '')
                filtered = [d for d in dividends if d['ticker'] == clean_ticker]
                if filtered:
                    return {
                        'ticker': clean_ticker,
                        'company_name': filtered[0]['company_name'],
                        'dividend_rate': filtered[0]['dividend_amount'],
                        'dividend_yield': None,  # NSE doesn't provide yield
                        'current_price': None,
                        'ex_dividend_date': filtered[0]['ex_dividend_date'],
                        'record_date': filtered[0]['record_date'],
                        'payout_ratio': None,
                        'announcement_date': filtered[0]['announcement_date'],
                        'history': filtered,
                        'source': 'NSE Corporate Actions',
                        'error': None
                    }
                else:
                    return {
                        'ticker': clean_ticker,
                        'company_name': clean_ticker,
                        'dividend_rate': None,
                        'dividend_yield': None,
                        'current_price': None,
                        'ex_dividend_date': None,
                        'record_date': None,
                        'payout_ratio': None,
                        'announcement_date': None,
                        'history': [],
                        'source': 'NSE Corporate Actions - No data found',
                        'error': f'No dividend announcements found for {clean_ticker}'
                    }
            
            # Return all announcements
            return {
                'ticker': 'ALL',
                'company_name': 'Multiple Companies',
                'announcements': dividends,
                'count': len(dividends),
                'source': 'NSE Corporate Actions',
                'search_date': datetime.now().strftime("%d %B %Y"),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"[NSEDividendTool] Error fetching from NSE: {e}", exc_info=True)
            return self._get_sample_data(ticker)
    
    def _get_sample_data(self, ticker: str = None) -> Dict[str, Any]:
        """Return sample dividend data when NSE API fails."""
        logger.info("[NSEDividendTool] Returning sample dividend data")
        
        today = datetime.now()
        sample_data = [
            {
                'ticker': 'ITC',
                'company_name': 'ITC Ltd',
                'dividend_amount': 6.50,
                'dividend_type': 'Final',
                'ex_dividend_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
                'record_date': (today + timedelta(days=32)).strftime('%Y-%m-%d'),
                'announcement_date': today.strftime('%Y-%m-%d'),
                'source': 'Sample Data (NSE API unavailable)'
            },
            {
                'ticker': 'RELIANCE',
                'company_name': 'Reliance Industries Ltd',
                'dividend_amount': 10.00,
                'dividend_type': 'Final',
                'ex_dividend_date': (today + timedelta(days=45)).strftime('%Y-%m-%d'),
                'record_date': (today + timedelta(days=47)).strftime('%Y-%m-%d'),
                'announcement_date': today.strftime('%Y-%m-%d'),
                'source': 'Sample Data (NSE API unavailable)'
            },
            {
                'ticker': 'TCS',
                'company_name': 'Tata Consultancy Services Ltd',
                'dividend_amount': 12.00,
                'dividend_type': 'Interim',
                'ex_dividend_date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
                'record_date': (today + timedelta(days=17)).strftime('%Y-%m-%d'),
                'announcement_date': today.strftime('%Y-%m-%d'),
                'source': 'Sample Data (NSE API unavailable)'
            },
            {
                'ticker': 'HDFCBANK',
                'company_name': 'HDFC Bank Ltd',
                'dividend_amount': 2.50,
                'dividend_type': 'Final',
                'ex_dividend_date': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
                'record_date': (today + timedelta(days=22)).strftime('%Y-%m-%d'),
                'announcement_date': today.strftime('%Y-%m-%d'),
                'source': 'Sample Data (NSE API unavailable)'
            },
            {
                'ticker': 'INFY',
                'company_name': 'Infosys Ltd',
                'dividend_amount': 21.00,
                'dividend_type': 'Final',
                'ex_dividend_date': (today + timedelta(days=25)).strftime('%Y-%m-%d'),
                'record_date': (today + timedelta(days=27)).strftime('%Y-%m-%d'),
                'announcement_date': today.strftime('%Y-%m-%d'),
                'source': 'Sample Data (NSE API unavailable)'
            },
            {
                'ticker': 'HINDUNILVR',
                'company_name': 'Hindustan Unilever Ltd',
                'dividend_amount': 24.00,
                'dividend_type': 'Final',
                'ex_dividend_date': (today + timedelta(days=35)).strftime('%Y-%m-%d'),
                'record_date': (today + timedelta(days=37)).strftime('%Y-%m-%d'),
                'announcement_date': today.strftime('%Y-%m-%d'),
                'source': 'Sample Data (NSE API unavailable)'
            },
        ]
        
        if ticker:
            clean_ticker = ticker.upper().replace('.NS', '').replace('.BO', '')
            filtered = [d for d in sample_data if d['ticker'] == clean_ticker]
            if filtered:
                return {
                    'ticker': clean_ticker,
                    'company_name': filtered[0]['company_name'],
                    'dividend_rate': filtered[0]['dividend_amount'],
                    'dividend_yield': None,
                    'current_price': None,
                    'ex_dividend_date': filtered[0]['ex_dividend_date'],
                    'record_date': filtered[0]['record_date'],
                    'payout_ratio': None,
                    'announcement_date': filtered[0]['announcement_date'],
                    'history': filtered,
                    'source': filtered[0]['source'],
                    'error': None
                }
            else:
                return {
                    'ticker': clean_ticker,
                    'company_name': clean_ticker,
                    'dividend_rate': None,
                    'dividend_yield': None,
                    'current_price': None,
                    'ex_dividend_date': None,
                    'record_date': None,
                    'payout_ratio': None,
                    'announcement_date': None,
                    'history': [],
                    'source': 'Sample Data - No data found',
                    'error': f'No dividend data found for {clean_ticker}'
                }
        
        return {
            'ticker': 'ALL',
            'company_name': 'Multiple Companies',
            'announcements': sample_data,
            'count': len(sample_data),
            'source': 'Sample Data (NSE API unavailable)',
            'search_date': datetime.now().strftime("%d %B %Y"),
            'error': None
        }


# Global instance
nse_dividend_tool = NSEDividendTool()


# Export
__all__ = ['nse_dividend_tool', 'NSEDividendTool']
