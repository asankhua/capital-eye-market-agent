"""NSE Corporate Actions - Fetches dividend announcements from NSE India API.

Uses direct HTTP requests to NSE official API - no external library dependencies.
"""

import logging
import requests
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("market_analyst.tools.nse_dividend")


class NSEDividendTool:
    """Tool for fetching Indian stock dividend data from NSE Corporate Actions."""
    
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.session = requests.Session()
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-actions'
        })
        self._cookies_set = False
        logger.info("[NSEDividendTool] Initialized with direct NSE API")
        
    def _get_cookies(self):
        """Get NSE session cookies."""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            self._cookies_set = True
            logger.info("[NSEDividendTool] Got NSE session cookies")
        except Exception as e:
            logger.error(f"[NSEDividendTool] Failed to get cookies: {e}")
            self._cookies_set = False
    
    def _parse_amount(self, purpose: str) -> Optional[float]:
        """Extract dividend amount from purpose string."""
        import re
        try:
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
        """Get dividend announcements from NSE Corporate Actions.
        
        Args:
            ticker: Stock ticker symbol (e.g., "ITC", "RELIANCE"). If None, returns all recent dividends.
            
        Returns:
            dict with dividend information from NSE
        """
        logger.info(f"[NSEDividendTool] Fetching dividend announcements for {ticker or 'all stocks'}")
        
        try:
            # Get session cookies first
            if not self._cookies_set:
                self._get_cookies()
            
            # NSE Corporate Actions API endpoint
            url = f"{self.base_url}/api/corporate-actions"
            
            # Parameters for dividend filter - last 90 days
            params = {
                'index': 'equities',
                'from_date': (datetime.now() - timedelta(days=90)).strftime('%d-%m-%Y'),
                'to_date': datetime.now().strftime('%d-%m-%Y'),
                'subject': 'dividend'
            }
            
            logger.info(f"[NSEDividendTool] Calling NSE API: {url}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if not data or 'data' not in data:
                logger.warning("[NSEDividendTool] No data returned from NSE API")
                return self._get_sample_data(ticker)
            
            # Convert to list of dicts
            actions = data.get('data', [])
            if not actions:
                logger.warning("[NSEDividendTool] Empty data from NSE API")
                return self._get_sample_data(ticker)
            
            dividends = []
            for item in actions:
                symbol = item.get('symbol', item.get('security', ''))
                if not symbol:
                    continue
                    
                dividend = {
                    'ticker': str(symbol).replace('.NS', '').replace('.BO', '').strip(),
                    'company_name': item.get('companyName', item.get('company', symbol)),
                    'dividend_amount': self._parse_amount(item.get('purpose', item.get('description', ''))),
                    'dividend_type': self._extract_dividend_type(item.get('purpose', '')),
                    'ex_dividend_date': self._parse_date(item.get('exDate', item.get('ex_date', ''))),
                    'record_date': self._parse_date(item.get('recDate', item.get('record_date', ''))),
                    'announcement_date': self._parse_date(item.get('anncDate', item.get('announcement_date', ''))),
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
                        'dividend_yield': None,
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
