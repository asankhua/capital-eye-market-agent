"""Market data integration using nsetools for Indian markets and Finnhub for US markets."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the logger from config
from backend.config import logger

# Import nse_market_tool for Indian market data
try:
    from backend.tools.nse_market_tool import nse_market_tool, NSETOOLS_AVAILABLE
except ImportError:
    NSETOOLS_AVAILABLE = False
    nse_market_tool = None


class TwelveDataTool:
    """Tool for fetching market data - uses nsetools for Indian markets."""
    
    def __init__(self):
        # No API key needed for nsetools - it scrapes NSE website
        self.api_key = "not_required"
        self.api_key_source = "nsetools"
        logger.info("[TwelveData] Initialized - using nsetools for Indian market data")
    
    def get_market_movers(self, direction: str = "gainers", outputsize: int = 10) -> List[Dict]:
        """Get market movers: gainers or losers."""
        if not NSETOOLS_AVAILABLE or nse_market_tool is None:
            # Fallback to Finnhub for US market movers
            logger.info("[TwelveData] NSE tools not available, using Finnhub for movers")
            from backend.tools.finnhub_tool import finnhub_tool
            return finnhub_tool.get_market_movers(direction)[:outputsize]
        
        return nse_market_tool.get_market_movers(direction)[:outputsize]
    
    def get_indices(self) -> List[Dict]:
        """Get major Indian market indices using nsetools."""
        if not NSETOOLS_AVAILABLE or nse_market_tool is None:
            raise RuntimeError("nsetools not available for Indian indices")
        
        return nse_market_tool.get_indices()
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get overall market state/overview."""
        logger.info("[TwelveData] Fetching market state via nsetools...")
        
        if not NSETOOLS_AVAILABLE or nse_market_tool is None:
            raise RuntimeError("nsetools not available for Indian market data")
        
        return nse_market_tool.get_market_state()


# Global instance
twelve_data_tool = TwelveDataTool()
