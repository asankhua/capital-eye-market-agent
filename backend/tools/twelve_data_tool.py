"""Twelve Data API integration for market overview."""
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# Get API key from environment
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")
TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"

# DUMMY DATA FOR UI TESTING (fallback when API fails)
DUMMY_INDICES = [
    {"symbol": "NIFTY50", "name": "NIFTY 50", "price": 24150.45, "change": 125.80, "change_percent": 0.52},
    {"symbol": "SENSEX", "name": "BSE SENSEX", "price": 79234.56, "change": 312.45, "change_percent": 0.40},
    {"symbol": "NIFTYBANK", "name": "NIFTY Bank", "price": 48234.78, "change": -89.12, "change_percent": -0.18},
    {"symbol": "NIFTYIT", "name": "NIFTY IT", "price": 38456.23, "change": 245.67, "change_percent": 0.64},
    {"symbol": "INDIAVIX", "name": "India VIX", "price": 14.23, "change": -0.45, "change_percent": -3.07},
]

DUMMY_MOVERS = {
    "gainers": [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "price": 2875.50, "change": 42.80, "change_percent": 5.07, "volume": 4850000},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 4165.20, "change": 182.30, "change_percent": 4.57, "volume": 5230000},
        {"symbol": "INFY", "name": "Infosys Ltd", "price": 1898.75, "change": 71.80, "change_percent": 3.94, "volume": 2150000},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "price": 1575.30, "change": 50.90, "change_percent": 3.35, "volume": 9820000},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "price": 985.45, "change": 27.20, "change_percent": 2.84, "volume": 1270000},
    ],
    "losers": [
        {"symbol": "VEDL", "name": "Vedanta Ltd", "price": 425.80, "change": -26.90, "change_percent": -5.94, "volume": 7850000},
        {"symbol": "YESBANK", "name": "Yes Bank Ltd", "price": 17.80, "change": -0.90, "change_percent": -4.80, "volume": 1560000},
        {"symbol": "ZOMATO", "name": "Zomato Ltd", "price": 228.40, "change": -8.55, "change_percent": -3.60, "volume": 450000},
        {"symbol": "PAYTM", "name": "One97 Communications", "price": 625.30, "change": -18.70, "change_percent": -2.90, "volume": 2340000},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "price": 985.60, "change": -26.75, "change_percent": -2.64, "volume": 1870000},
    ]
}

class TwelveDataTool:
    """Tool for fetching market data from Twelve Data API."""
    
    def __init__(self):
        self.api_key = TWELVE_DATA_API_KEY
        if self.api_key:
            print(f"[TwelveData] Initialized with API key: {self.api_key[:8]}...")
        else:
            print("[TwelveData] No API key found - using dummy data")
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated request to Twelve Data API."""
        if not self.api_key:
            return {}
        
        url = f"{TWELVE_DATA_BASE_URL}/{endpoint}"
        params = params or {}
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "error":
                print(f"[TwelveData] API error: {data.get('message', 'Unknown error')}")
                return {}
            return data
        except Exception as e:
            print(f"[TwelveData] API request failed: {e}")
            return {}
    
    def get_market_movers(self, direction: str = "gainers", outputsize: int = 10) -> List[Dict]:
        """Get market movers: gainers or losers."""
        if not self.api_key:
            print("[TwelveData] Using dummy market movers")
            return DUMMY_MOVERS.get(direction, DUMMY_MOVERS["gainers"])[:outputsize]
        
        # Use Finnhub for movers (Twelve Data doesn't have direct movers endpoint)
        from backend.tools.finnhub_tool import finnhub_tool
        return finnhub_tool.get_market_movers(direction)[:outputsize]
    
    def get_indices(self) -> List[Dict]:
        """Get major market indices data."""
        if not self.api_key:
            print("[TwelveData] Using dummy indices data")
            return DUMMY_INDICES
        
        # Try to fetch real indices - NIFTY 50 and SENSEX
        indices_data = []
        
        for symbol, name in [("NIFTY 50", "NIFTY 50"), ("BSE SENSEX", "BSE SENSEX")]:
            data = self._make_request("quote", {"symbol": symbol, "interval": "1day"})
            if data and "close" in data:
                try:
                    prev_close = float(data.get("previous_close", 0) or 0)
                    current = float(data.get("close", 0) or 0)
                    change = current - prev_close if prev_close else 0
                    change_pct = (change / prev_close * 100) if prev_close else 0
                    
                    indices_data.append({
                        "symbol": symbol.replace(" ", ""),
                        "name": name,
                        "price": round(current, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2)
                    })
                except (ValueError, TypeError):
                    pass
        
        return indices_data if indices_data else DUMMY_INDICES
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get overall market state/overview."""
        if not self.api_key:
            print("[TwelveData] Using dummy market state")
            return {
                "indices": DUMMY_INDICES,
                "top_gainers": DUMMY_MOVERS["gainers"],
                "top_losers": DUMMY_MOVERS["losers"],
                "timestamp": datetime.now().isoformat()
            }
        
        indices = self.get_indices()
        gainers = self.get_market_movers("gainers", 5)
        losers = self.get_market_movers("losers", 5)
        
        return {
            "indices": indices,
            "top_gainers": gainers,
            "top_losers": losers,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
twelve_data_tool = TwelveDataTool()
