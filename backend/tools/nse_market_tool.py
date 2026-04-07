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
        """Get major Indian market indices using nsetools."""
        indices_data = []
        
        # Fetch NIFTY 50
        try:
            logger.info("[NSEMarketTool] Fetching NIFTY 50")
            nifty = self.nse.get_index_quote("NIFTY 50")
            if nifty:
                indices_data.append({
                    "symbol": "NIFTY50",
                    "name": "NIFTY 50",
                    "price": float(nifty.get("last", 0)),
                    "change": float(nifty.get("variation", 0)),
                    "change_percent": float(nifty.get("percentChange", 0))
                })
                logger.info(f"[NSEMarketTool] NIFTY 50: {nifty.get('last')} ({nifty.get('percentChange')}%)")
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error fetching NIFTY 50: {e}")
            raise RuntimeError(f"Failed to fetch NIFTY 50: {e}")
        
        # Fetch NIFTY Bank
        try:
            logger.info("[NSEMarketTool] Fetching NIFTY Bank")
            bank_nifty = self.nse.get_index_quote("NIFTY BANK")
            if bank_nifty:
                indices_data.append({
                    "symbol": "NIFTYBANK",
                    "name": "NIFTY Bank",
                    "price": float(bank_nifty.get("last", 0)),
                    "change": float(bank_nifty.get("variation", 0)),
                    "change_percent": float(bank_nifty.get("percentChange", 0))
                })
                logger.info(f"[NSEMarketTool] NIFTY Bank: {bank_nifty.get('last')}")
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error fetching NIFTY Bank: {e}")
        
        # Fetch all indices to find SENSEX
        try:
            logger.info("[NSEMarketTool] Fetching all indices for SENSEX")
            all_indices = self.nse.get_all_index_quote()
            for idx in all_indices:
                if "SENSEX" in str(idx.get("index", "")):
                    indices_data.append({
                        "symbol": "SENSEX",
                        "name": "BSE SENSEX",
                        "price": float(idx.get("last", 0)),
                        "change": float(idx.get("variation", 0)),
                        "change_percent": float(idx.get("percentChange", 0))
                    })
                    logger.info(f"[NSEMarketTool] SENSEX: {idx.get('last')}")
                    break
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error fetching SENSEX: {e}")
        
        if not indices_data:
            raise RuntimeError("No index data retrieved from NSE")
        
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
        """Get overall market state/overview."""
        logger.info("[NSEMarketTool] Fetching market state...")
        indices = self.get_indices()
        gainers = self.get_market_movers("gainers")[:5]
        losers = self.get_market_movers("losers")[:5]
        
        logger.info(f"[NSEMarketTool] Market state: {len(indices)} indices, {len(gainers)} gainers, {len(losers)} losers")
        
        return {
            "indices": indices,
            "top_gainers": gainers,
            "top_losers": losers,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
nse_market_tool = None
if NSETOOLS_AVAILABLE:
    try:
        nse_market_tool = NSEMarketTool()
    except Exception as e:
        logger.error(f"[NSEMarketTool] Failed to initialize: {e}")
