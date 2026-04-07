"""Market data integration using nsetools for Indian markets and Finnhub for US markets."""
import os
import requests
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
        
        # Try to fetch missing indices via direct NSE API
        missing_indices = ["NIFTY SMALLCAP 250", "NIFTY MIDCAP150 MOMENTUM 50", "NIFTY50 EQUAL WEIGHT", "NIFTY INDIA RAILWAYS PSU"]
        for idx_name in missing_indices:
            if idx_name not in [d.get("name", "") for d in indices_data]:
                try:
                    data = self._fetch_index_from_nse_api(idx_name)
                    if data:
                        indices_data.append(data)
                        logger.info(f"[NSEMarketTool] {idx_name} fetched via direct API: {data['price']} ({data['change_percent']}%)")
                except Exception as e:
                    logger.warning(f"[NSEMarketTool] Could not fetch {idx_name} via direct API: {e}")
        
        if not indices_data:
            raise RuntimeError("No index data retrieved from NSE")
        
        logger.info(f"[NSEMarketTool] Total indices fetched: {len(indices_data)}")
        return indices_data
    
    def _fetch_index_from_nse_api(self, index_name: str) -> Optional[Dict]:
        """Fetch a specific index directly from NSE API using requests."""
        # Map index names to NSE API symbols (URL encoded)
        index_symbol_map = {
            "NIFTY 50": "NIFTY%2050",
            "NIFTY MIDCAP 150": "NIFTY%20MIDCAP%20150",
            "NIFTY SMALLCAP 250": "NIFTY%20SMALLCAP%20250",
            "NIFTY ALPHA 50": "NIFTY%20ALPHA%2050",
            "NIFTY MIDCAP150 MOMENTUM 50": "NIFTY%20MIDCAP150%20MOMENTUM%2050",
            "NIFTY50 EQUAL WEIGHT": "NIFTY50%20EQUAL%20WEIGHT",
            "NIFTY NEXT 50": "NIFTY%20NEXT%2050",
            "NIFTY INDIA RAILWAYS PSU": "NIFTY%20INDIA%20RAILWAYS%20PSU",
            "NIFTY BANK": "NIFTY%20BANK",
            "NIFTY IT": "NIFTY%20IT",
            "NIFTY AUTO": "NIFTY%20AUTO",
            "NIFTY PHARMA": "NIFTY%20PHARMA",
            "NIFTY FMCG": "NIFTY%20FMCG",
            "NIFTY METAL": "NIFTY%20METAL",
            "NIFTY REALTY": "NIFTY%20REALTY",
            "NIFTY PSU BANK": "NIFTY%20PSU%20BANK",
            "NIFTY COMMODITIES": "NIFTY%20COMMODITIES",
            "INDIA VIX": "INDIA%20VIX"
        }
        
        symbol = index_symbol_map.get(index_name, index_name.replace(" ", "%20"))
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/market-data/live-equity-market",
            "Connection": "keep-alive"
        }
        
        try:
            session = requests.Session()
            # Get initial cookies
            session.get("https://www.nseindia.com", headers=headers, timeout=15)
            
            # Fetch all indices data
            url = "https://www.nseindia.com/api/allIndices"
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # data is a dict with 'data' key containing list of indices
                indices_list = data.get("data", []) if isinstance(data, dict) else data
                
                for idx in indices_list:
                    if idx.get("indexName") == index_name or idx.get("index", "") == index_name:
                        return {
                            "symbol": index_name.replace(" ", ""),
                            "name": index_name,
                            "price": float(idx.get("last", 0) or idx.get("close", 0) or 0),
                            "change": float(idx.get("change", 0) or idx.get("variation", 0) or 0),
                            "change_percent": float(idx.get("percentChange", 0) or idx.get("pChange", 0) or 0)
                        }
            
            logger.warning(f"[NSEMarketTool] Index {index_name} not found in allIndices response")
            return None
        except Exception as e:
            logger.warning(f"[NSEMarketTool] Direct API fetch failed for {index_name}: {e}")
            return None
    
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
            for item in movers[:20]:  # Increased from 10 to 20
                # Try multiple possible volume field names from nsetools
                volume = (
                    item.get("tradedQuantity") or 
                    item.get("quantityTraded") or 
                    item.get("totalTradedQuantity") or 
                    item.get("volume") or 
                    item.get("tradedVolume") or 
                    0
                )
                result.append({
                    "symbol": item.get("symbol", ""),
                    "name": item.get("symbol", ""),  # nsetools doesn't provide name
                    "price": float(item.get("ltp", 0)),
                    "change": float(item.get("net_price", 0)),
                    "change_percent": float(item.get("perChange", 0)),
                    "volume": int(float(volume))
                })
            
            logger.info(f"[NSEMarketTool] Fetched {len(result)} {direction}, sample volume: {result[0]['volume'] if result else 'N/A'}")
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
    
    def get_sector_performance(self) -> List[Dict]:
        """Get Indian sector performance from NSE sectoral indices."""
        logger.info("[NSEMarketTool] Fetching Indian sector performance...")
        
        # NSE Sectoral Indices mapping
        sector_indices = {
            "NIFTY BANK": "Banking",
            "NIFTY IT": "Information Technology",
            "NIFTY AUTO": "Automobile",
            "NIFTY PHARMA": "Pharma",
            "NIFTY FMCG": "FMCG",
            "NIFTY METAL": "Metal",
            "NIFTY REALTY": "Realty",
            "NIFTY PSU BANK": "PSU Bank",
            "NIFTY ENERGY": "Energy",
            "NIFTY FIN SERVICE": "Financial Services",
            "NIFTY MEDIA": "Media",
            "NIFTY HEALTHCARE": "Healthcare"
        }
        
        sectors = []
        for index_name, sector_name in sector_indices.items():
            try:
                logger.info(f"[NSEMarketTool] Fetching sector: {sector_name}")
                idx_data = self.nse.get_index_quote(index_name)
                if idx_data:
                    change_pct = float(idx_data.get("percentChange", 0))
                    sectors.append({
                        "name": sector_name,
                        "change_percent": round(change_pct, 2),
                        "index_name": index_name,
                        "price": float(idx_data.get("last", 0))
                    })
                    logger.info(f"[NSEMarketTool] {sector_name}: {change_pct}%")
            except Exception as e:
                logger.warning(f"[NSEMarketTool] Could not fetch {sector_name}: {e}")
                continue
        
        # Sort by change percent descending
        sectors.sort(key=lambda x: x["change_percent"], reverse=True)
        
        logger.info(f"[NSEMarketTool] Total sectors fetched: {len(sectors)}")
        return sectors
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote for a specific symbol from NSE."""
        try:
            # Remove .NS suffix if present
            clean_symbol = symbol.upper().replace('.NS', '').replace('.BO', '')
            logger.info(f"[NSEMarketTool] Fetching stock quote for {clean_symbol}")
            
            quote = self.nse.get_stock_quote(clean_symbol)
            if quote:
                result = {
                    "symbol": clean_symbol,
                    "name": quote.get("companyName", clean_symbol),
                    "price": float(quote.get("lastPrice", 0)),
                    "change": float(quote.get("change", 0)),
                    "change_percent": float(quote.get("pChange", 0)),
                    "day_high": float(quote.get("dayHigh", 0)),
                    "day_low": float(quote.get("dayLow", 0)),
                    "volume": int(quote.get("totalTradedVolume", 0)),
                    "open": float(quote.get("open", 0)),
                    "previous_close": float(quote.get("previousClose", 0))
                }
                logger.info(f"[NSEMarketTool] {clean_symbol}: {result['price']} ({result['change_percent']}%)")
                return result
            else:
                raise RuntimeError(f"No data returned for {clean_symbol}")
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error fetching stock quote for {symbol}: {e}")
            raise RuntimeError(f"Failed to fetch stock quote for {symbol}: {e}")
    
    def get_all_stocks(self) -> List[Dict]:
        """Get list of all stocks traded on NSE."""
        try:
            logger.info("[NSEMarketTool] Fetching all stocks list")
            stocks = self.nse.get_stock_codes()
            logger.info(f"[NSEMarketTool] Found {len(stocks)} stocks")
            return stocks
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error fetching stock list: {e}")
            raise RuntimeError(f"Failed to fetch stock list: {e}")
    
    def is_valid_symbol(self, symbol: str) -> bool:
        """Check if a symbol is valid/traded on NSE."""
        try:
            clean_symbol = symbol.upper().replace('.NS', '').replace('.BO', '')
            stocks = self.nse.get_stock_codes()
            return clean_symbol in stocks.values() or clean_symbol in stocks.keys()
        except Exception as e:
            logger.error(f"[NSEMarketTool] Error checking symbol validity: {e}")
            return False
nse_market_tool = None
if NSETOOLS_AVAILABLE:
    try:
        nse_market_tool = NSEMarketTool()
    except Exception as e:
        logger.error(f"[NSEMarketTool] Failed to initialize: {e}")
