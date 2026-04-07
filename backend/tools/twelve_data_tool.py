"""Market data integration using Twelve Data API for US markets and yfinance for Indian markets."""
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the logger from config
from backend.config import logger

# Try to import yfinance for Indian market data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("[MarketData] yfinance not available for Indian markets")

TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"


class TwelveDataTool:
    """Tool for fetching market data from Twelve Data API."""
    
    def __init__(self):
        # Read API key at runtime, not import time (for HF Secrets compatibility)
        self.api_key = os.getenv("TWELVE_DATA_API_KEY", "").strip()
        self.api_key_source = "HF Secrets" if self.api_key else "NOT SET"
        
        if self.api_key:
            masked_key = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
            logger.info(f"[TwelveData] Initialized with API key from {self.api_key_source}: {masked_key}")
        else:
            logger.error("[TwelveData] NO API KEY FOUND - Check HF Secrets for TWELVE_DATA_API_KEY")
            raise ValueError("TWELVE_DATA_API_KEY not set in environment")
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated request to Twelve Data API."""
        if not self.api_key:
            raise ValueError("TWELVE_DATA_API_KEY not set")
        
        url = f"{TWELVE_DATA_BASE_URL}/{endpoint}"
        params = params or {}
        params['apikey'] = self.api_key
        
        try:
            logger.info(f"[TwelveData] Requesting: {endpoint}")
            response = requests.get(url, params=params, timeout=15)
            logger.info(f"[TwelveData] Response status: {response.status_code}")
            
            response.raise_for_status()
            
            if not response.text:
                logger.error("[TwelveData] Empty response")
                raise RuntimeError("Empty response from Twelve Data API")
            
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"[TwelveData] JSON parse error: {e}")
                raise RuntimeError(f"Invalid JSON response from Twelve Data API: {e}")
            
            if data.get("status") == "error":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"[TwelveData] API error: {error_msg}")
                raise RuntimeError(f"Twelve Data API error: {error_msg}")
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"[TwelveData] API request failed: {e}")
            raise RuntimeError(f"Twelve Data API request failed: {e}")
    
    def get_market_movers(self, direction: str = "gainers", outputsize: int = 10) -> List[Dict]:
        """Get market movers: gainers or losers."""
        # Use Finnhub for movers (Twelve Data doesn't have direct movers endpoint)
        from backend.tools.finnhub_tool import finnhub_tool
        return finnhub_tool.get_market_movers(direction)[:outputsize]
    
    def get_indices(self) -> List[Dict]:
        """Get major Indian market indices using Yahoo Finance (yfinance)."""
        if not YFINANCE_AVAILABLE:
            logger.error("[MarketData] yfinance not available for Indian indices")
            raise RuntimeError("yfinance library not available for Indian market data")
        
        indices_data = []
        
        # Use yfinance with Yahoo Finance ticker symbols for Indian indices
        indices_to_fetch = [
            ("^NSEI", "NIFTY 50"),      # NIFTY 50 on NSE
            ("^BSESN", "BSE SENSEX"),  # SENSEX on BSE
            ("^NSEBANK", "NIFTY Bank"), # NIFTY Bank
        ]
        
        for symbol, name in indices_to_fetch:
            logger.info(f"[MarketData] Fetching {name} ({symbol}) via Yahoo Finance")
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if len(hist) >= 2:
                    current = float(hist['Close'].iloc[-1])
                    prev_close = float(hist['Close'].iloc[-2])
                    change = current - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0
                    
                    indices_data.append({
                        "symbol": symbol.replace("^", ""),
                        "name": name,
                        "price": round(current, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2)
                    })
                    logger.info(f"[MarketData] {name}: {current:,.2f} ({change_pct:+.2f}%)")
                else:
                    logger.error(f"[MarketData] Insufficient data for {name}")
                    raise RuntimeError(f"Insufficient historical data for {name}")
            except Exception as e:
                logger.error(f"[MarketData] Error fetching {name}: {e}")
                raise RuntimeError(f"Failed to fetch {name}: {e}")
        
        return indices_data
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get overall market state/overview."""
        logger.info("[TwelveData] Fetching market state...")
        indices = self.get_indices()
        gainers = self.get_market_movers("gainers", 5)
        losers = self.get_market_movers("losers", 5)
        
        logger.info(f"[TwelveData] Market state: {len(indices)} indices, {len(gainers)} gainers, {len(losers)} losers")
        
        return {
            "indices": indices,
            "top_gainers": gainers,
            "top_losers": losers,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
twelve_data_tool = TwelveDataTool()
