"""Market data integration using nsetools for Indian markets and Finnhub for US markets."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the logger from config
from backend.config import logger

# Try to import nsetools for Indian market data
try:
    from nsetools import Nse
    NSETOOLS_AVAILABLE = True
except ImportError:
    NSETOOLS_AVAILABLE = False
    logger.warning("[MarketData] nsetools not available for Indian markets")


class NSEMarketTool:
    """Tool for fetching Indian market data from NSE using nsetools."""
    
    def __init__(self):
        if not NSETOOLS_AVAILABLE:
            raise RuntimeError("nsetools library not available")
        self.nse = Nse()
        logger.info("[NSEMarketTool] Initialized nsetools for Indian market data")
    
    def get_indices(self) -> List[Dict]:
        """Get major Indian market indices using nsetools - fetches only specified indices."""
        indices_data = []
        
        # Specific indices to fetch (as requested by user)
        major_indices = [
            "NIFTY 50",
            "NIFTY MIDCAP 150",
            "NIFTY SMALLCAP 250",
            "NIFTY ALPHA 50",
            "NIFTY MIDCAP150 MOMENTUM 50",
            "NIFTY50 EQUAL WEIGHT",
            "NIFTY NEXT 50",
            "NIFTY INDIA RAILWAYS PSU",
            "NIFTY BANK",
            "NIFTY IT",
            "NIFTY AUTO",
            "NIFTY PHARMA",
            "NIFTY FMCG",
            "NIFTY METAL",
            "NIFTY REALTY",
            "NIFTY PSU BANK",
            "NIFTY COMMODITIES",
            "INDIA VIX",
        ]
        
        # Fetch each major index
        for index_name in major_indices:
            try:
                logger.info(f"[NSEMarketTool] Fetching {index_name}")
                idx_data = self.nse.get_index_quote(index_name)
                if idx_data:
                    indices_data.append({
                        "symbol": idx_data.get("indexSymbol", "").replace(" ", ""),
                        "name": idx_data.get("index", index_name),
                        "price": float(idx_data.get("last", 0)),
                        "change": float(idx_data.get("variation", 0)),
                        "change_percent": float(idx_data.get("percentChange", 0))
                    })
                    logger.info(f"[NSEMarketTool] {index_name}: {idx_data.get('last')} ({idx_data.get('percentChange')}%)")
            except Exception as e:
                logger.warning(f"[NSEMarketTool] Could not fetch {index_name}: {e}")
                continue
        
        if not indices_data:
            raise RuntimeError("No index data retrieved from NSE")
        
        logger.info(f"[NSEMarketTool] Total indices fetched: {len(indices_data)}")
        return indices_data
    
    def get_market_movers(self, direction: str = "gainers") -> List[Dict]:
        """Get market movers from NSE."""
        try:
            if direction == "gainers":
                logger.info("[NSEMarketTool] Fetching top gainers")
                movers = self.nse.get_top_gainers()
            elif direction == "losers":
                logger.info("[NSEMarketTool] Fetching top losers")
                movers = self.nse.get_top_losers()
            else:
                # For active, use gainers as proxy
                logger.info("[NSEMarketTool] Fetching top gainers for active")
                movers = self.nse.get_top_gainers()
            
            result = []
            for item in movers[:10]:
                result.append({
                    "symbol": item.get("symbol", ""),
                    "name": item.get("symbol", ""),  # nsetools doesn't provide name
                    "price": float(item.get("ltp", 0)),
                    "change": float(item.get("net_price", 0)),
                    "change_percent": float(item.get("perChange", 0)),
                    "volume": int(item.get("tradedQuantity", 0))
                })
            
            logger.info(f"[NSEMarketTool] Fetched {len(result)} {direction}")
            return result
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error fetching market movers: {e}")
            raise RuntimeError(f"Failed to fetch market movers: {e}")
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get overall market state/overview - indices only (no gainers/losers)."""
        logger.info("[NSEMarketTool] Fetching market state...")
        indices = self.get_indices()
        
        logger.info(f"[NSEMarketTool] Market state: {len(indices)} indices")
        
        return {
            "indices": indices,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
nse_market_tool = None
if NSETOOLS_AVAILABLE:
    try:
        nse_market_tool = NSEMarketTool()
    except Exception as e:
        logger.error(f"[NSEMarketTool] Failed to initialize: {e}")
