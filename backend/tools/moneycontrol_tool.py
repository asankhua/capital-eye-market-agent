"""
MoneyControl Dividend Scraper Tool
Fetches live dividend data from MoneyControl website
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class MoneyControlDividendTool:
    """Tool to scrape dividend data from MoneyControl"""
    
    BASE_URL = "https://www.moneycontrol.com/markets/corporate-action/dividends_declared/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def get_dividends(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch dividend data from MoneyControl
        
        Args:
            symbol: Optional stock symbol to filter results
            
        Returns:
            Dictionary with dividend data including history
        """
        try:
            # Fetch the dividend page
            response = self.session.get(self.BASE_URL, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract dividend data from table
            dividends = self._parse_dividend_table(soup)
            
            # Filter by symbol if provided
            if symbol:
                symbol_upper = symbol.upper().replace('.NS', '')
                filtered = [d for d in dividends if symbol_upper in d.get('symbol', '').upper()]
                dividends = filtered
            
            # Calculate summary statistics
            if dividends:
                latest = dividends[0]
                return {
                    'symbol': symbol or 'ALL',
                    'dividend_yield': latest.get('yield', 0),
                    'dividend_rate': latest.get('amount', 0),
                    'ex_dividend_date': latest.get('ex_date', ''),
                    'payout_ratio': None,  # Not available from MoneyControl
                    'history': dividends,
                    'source': 'moneycontrol',
                    'error': None
                }
            else:
                return {
                    'symbol': symbol or 'ALL',
                    'error': 'No dividend data found',
                    'history': []
                }
                
        except Exception as e:
            return {
                'symbol': symbol or 'ALL',
                'error': f'Failed to fetch dividend data: {str(e)}',
                'history': []
            }
    
    def _parse_dividend_table(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse dividend data from HTML table"""
        dividends = []
        
        try:
            # Find the dividend table - MoneyControl uses specific class names
            # The table typically has id or class containing 'dividend' or 'corp_action'
            table = soup.find('table', {'class': re.compile('dvdtbl|corp_action', re.I)})
            
            if not table:
                # Try alternative selectors
                table = soup.find('table', {'id': re.compile('dividend|corp', re.I)})
            
            if not table:
                # Look for any table with dividend-related headers
                tables = soup.find_all('table')
                for t in tables:
                    headers = t.find_all('th')
                    header_text = ' '.join([h.get_text(strip=True).lower() for h in headers])
                    if 'dividend' in header_text or 'ex-date' in header_text:
                        table = t
                        break
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            company_name = cells[0].get_text(strip=True)
                            symbol = self._extract_symbol(cells[0])
                            
                            dividend_data = {
                                'company': company_name,
                                'symbol': symbol,
                                'ex_date': self._parse_date(cells[1].get_text(strip=True)),
                                'record_date': self._parse_date(cells[2].get_text(strip=True)) if len(cells) > 2 else None,
                                'amount': self._parse_amount(cells[3].get_text(strip=True)),
                                'yield': self._calculate_yield(cells),
                                'type': 'cash'
                            }
                            dividends.append(dividend_data)
                        except Exception as e:
                            continue
            
            # If no data found from table parsing, return empty list
            return dividends
            
        except Exception as e:
            return dividends
    
    def _extract_symbol(self, cell) -> str:
        """Extract stock symbol from table cell"""
        # Try to find link with symbol
        link = cell.find('a')
        if link:
            href = link.get('href', '')
            # Extract symbol from URL pattern like /india/stockpricequote/computers-software/tataconsultancyservices/TCS
            match = re.search(r'/([^/]+)$', href)
            if match:
                return match.group(1).upper()
        
        # Return company name as fallback
        return cell.get_text(strip=True).split()[0].upper()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            # Common formats: "20-Jan-2026", "20 Jan 2026", "20/01/2026"
            date_str = date_str.strip()
            
            # Try various formats
            for fmt in ['%d-%b-%Y', '%d %b %Y', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
            
            return date_str
        except:
            return date_str
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse dividend amount from string"""
        try:
            # Remove currency symbols and parse
            cleaned = re.sub(r'[^\d.]', '', amount_str)
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def _calculate_yield(self, cells) -> Optional[float]:
        """Calculate or extract dividend yield"""
        try:
            # Check if there's a yield column
            for cell in cells:
                text = cell.get_text(strip=True)
                if '%' in text:
                    match = re.search(r'(\d+\.?\d*)%', text)
                    if match:
                        return float(match.group(1))
            return None
        except:
            return None


# Global instance
moneycontrol_dividend_tool = MoneyControlDividendTool()


def get_moneycontrol_dividends(symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch dividend data from MoneyControl
    
    Args:
        symbol: Stock symbol (optional, e.g., 'ITC', 'RELIANCE', 'HDFCBANK')
        
    Returns:
        Dictionary with dividend information
    """
    return moneycontrol_dividend_tool.get_dividends(symbol)
