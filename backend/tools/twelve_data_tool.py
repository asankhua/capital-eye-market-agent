"""Twelve Data API integration for market overview - Using DUMMY DATA for testing."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# DUMMY DATA FOR UI TESTING
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
    """Tool for fetching market data from Twelve Data API - Using DUMMY DATA."""
    
    def __init__(self):
        print("[TwelveData] Initialized with DUMMY DATA mode")
    
    def get_market_movers(self, direction: str = "gainers", outputsize: int = 10) -> List[Dict]:
        """Get market movers: gainers or losers - Returns DUMMY DATA."""
        print(f"[TwelveData] Returning dummy {direction} data")
        movers = DUMMY_MOVERS.get(direction, DUMMY_MOVERS["gainers"])
        return movers[:outputsize]
    
    def get_indices(self) -> List[Dict]:
        """Get major market indices data - Returns DUMMY DATA."""
        print("[TwelveData] Returning dummy indices data")
        return DUMMY_INDICES
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get overall market state/overview - Returns DUMMY DATA."""
        print("[TwelveData] Returning dummy market state")
        return {
            "indices": DUMMY_INDICES,
            "top_gainers": DUMMY_MOVERS["gainers"],
            "top_losers": DUMMY_MOVERS["losers"],
            "timestamp": datetime.now().isoformat()
        }

# Global instance
twelve_data_tool = TwelveDataTool()
