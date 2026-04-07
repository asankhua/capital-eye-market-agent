"""
SQLite Cache Wrapper

Provides a persistent caching layer for API calls.
Uses MCP if available, otherwise falls back to direct SQLite.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from typing import Any, Optional

logger = logging.getLogger("market_analyst.tools.sqlite_cache")

# Database path in db folder
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "db",
    "market_analysis.db"
)

# Try to import MCP, but don't fail if it's not available
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP not available (requires Python 3.10+), using direct SQLite fallback")

logger = logging.getLogger("market_analyst.tools.sqlite_mcp")


class SQLiteCacheTool:
    """Caching layer with MCP support and SQLite fallback."""

    _session: Optional[Any] = None
    _exit_stack = None
    _use_mcp = False
    _sqlite_path: str = DB_PATH

    @classmethod
    async def initialize(cls):
        """Initialize the cache - tries MCP first, falls back to SQLite."""
        if cls._session is not None:
            return

        # Try MCP first if available
        if MCP_AVAILABLE:
            try:
                await cls._init_mcp()
                cls._use_mcp = True
                logger.info("SQLite MCP cache initialized at %s", DB_PATH)
                return
            except Exception as e:
                logger.warning("MCP initialization failed: %s. Falling back to SQLite", e)

        # Fall back to direct SQLite
        try:
            await cls._init_sqlite()
            cls._use_mcp = False
            logger.info("Direct SQLite cache initialized at %s", DB_PATH)
            return
        except Exception as sqlite_err:
            logger.error("SQLite fallback also failed: %s", sqlite_err)
            raise

    @classmethod
    async def _init_sqlite(cls):
        """Initialize direct SQLite connection (fallback when MCP unavailable)."""
        # Ensure directory exists
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    UNIQUE(tool_name, cache_key)
                )
            """)
            # Watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL UNIQUE,
                    added_at REAL NOT NULL,
                    notes TEXT
                )
            """)
            # Historical analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historical_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    analysis_data TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            # Earnings calendar table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS earnings_calendar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    earnings_date TEXT NOT NULL,
                    eps_estimate REAL,
                    revenue_estimate REAL,
                    updated_at REAL NOT NULL
                )
            """)
            # Dividend history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dividend_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    ex_date TEXT NOT NULL,
                    payment_date TEXT,
                    amount REAL NOT NULL,
                    yield_percent REAL
                )
            """)
            conn.commit()
            logger.info("SQLite schema initialized with new tables (direct connection)")
        finally:
            conn.close()
    
    @classmethod
    async def _init_mcp(cls):
        """Initialize MCP client connection."""
        server_params = StdioServerParameters(
            command="npx",
            args=["--no", "mcp-sqlite-server", str(DB_PATH)],
        )

        from contextlib import AsyncExitStack
        cls._exit_stack = AsyncExitStack()
        
        stdio_transport = await cls._exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        cls._session = await cls._exit_stack.enter_async_context(ClientSession(read, write))
        await cls._session.initialize()
        
        logger.info("SQLite MCP Client connected successfully.")
        await cls._init_schema()

    @classmethod
    async def shutdown(cls):
        """Close the MCP server connection."""
        if cls._exit_stack:
            await cls._exit_stack.aclose()
            cls._session = None
            logger.info("SQLite MCP connection closed.")

    @classmethod
    async def _init_schema(cls):
        """Create the cache table if it doesn't exist."""
        if not cls._session:
            return
            
        query = """
        CREATE TABLE IF NOT EXISTS api_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL,
            cache_key TEXT NOT NULL,
            response_data TEXT NOT NULL,
            created_at REAL NOT NULL,
            UNIQUE(tool_name, cache_key)
        )
        """
        try:
            await cls._session.call_tool("query", arguments={
                "db": DB_PATH,
                "sql": query,
                "readonly": False
            })
            logger.info("Database schema initialized.")
        except Exception as e:
            logger.error("Error creating schema via MCP: %s", e)

    @classmethod
    async def get_cache(cls, tool_name: str, cache_key: str, max_age_seconds: int = 86400) -> Optional[dict[str, Any]]:
        """
        Retrieve a cached API response if it hasn't expired.
        Uses MCP if available, otherwise direct SQLite.
        """
        # Sanitize inputs to prevent SQL injection
        safe_tool = tool_name.replace("'", "''")
        safe_key = cache_key.replace("'", "''")
        
        oldest_valid_time = time.time() - max_age_seconds
        
        if cls._use_mcp and cls._session:
            return await cls._get_cache_mcp(safe_tool, safe_key, oldest_valid_time)
        else:
            return await cls._get_cache_sqlite(safe_tool, safe_key, oldest_valid_time)

    @classmethod
    async def _get_cache_mcp(cls, tool_name: str, cache_key: str, oldest_valid_time: float) -> Optional[dict[str, Any]]:
        """Get cache via MCP."""
        query = f"SELECT response_data FROM api_cache WHERE tool_name = '{tool_name}' AND cache_key = '{cache_key}' AND created_at > {oldest_valid_time};"
        
        try:
            result = await cls._session.call_tool("query", arguments={
                "db": DB_PATH,
                "sql": query
            })
            
            content = result.content[0].text
            
            if "Rows: 0" in content or "0 rows" in content.lower() or content.strip() == "":
                logger.debug("Cache MISS for %s:%s (or expired)", tool_name, cache_key)
                return None
                
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx+1]
                    logger.info("Cache HIT for %s:%s", tool_name, cache_key)
                    return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON from cache: %s", e)
                
            return None
            
        except Exception as e:
            logger.error("Error reading cache via MCP: %s", e)
            return None

    @classmethod
    async def _get_cache_sqlite(cls, tool_name: str, cache_key: str, oldest_valid_time: float) -> Optional[dict[str, Any]]:
        """Get cache via direct SQLite."""
        import sqlite3
        
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT response_data FROM api_cache WHERE tool_name = ? AND cache_key = ? AND created_at > ?",
                (tool_name, cache_key, oldest_valid_time)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.info("Cache HIT for %s:%s (SQLite)", tool_name, cache_key)
                return json.loads(row[0])
            else:
                logger.debug("Cache MISS for %s:%s (SQLite)", tool_name, cache_key)
                return None
                
        except Exception as e:
            logger.error("Error reading cache via SQLite: %s", e)
            return None

    @classmethod
    async def set_cache(cls, tool_name: str, cache_key: str, data: dict[str, Any], ttl: int = None):
        """
        Store an API response in the cache.
        Uses MCP if available, otherwise direct SQLite.
        
        Args:
            tool_name: Name of the tool
            cache_key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (optional, stored in data for expiry check)
        """
        # Add TTL to data if provided
        if ttl:
            data['_cache_ttl'] = ttl
            data['_cached_at'] = time.time()
        
        # Sanitize inputs to prevent SQL injection
        safe_tool = tool_name.replace("'", "''")
        safe_key = cache_key.replace("'", "''")
        
        if cls._use_mcp and cls._session:
            await cls._set_cache_mcp(safe_tool, safe_key, data)
        else:
            await cls._set_cache_sqlite(safe_tool, safe_key, data)

    @classmethod
    async def _set_cache_mcp(cls, tool_name: str, cache_key: str, data: dict[str, Any]):
        """Set cache via MCP."""
        json_data = json.dumps(data).replace("'", "''")
        now = time.time()
        
        query = f"""
        INSERT INTO api_cache (tool_name, cache_key, response_data, created_at) 
        VALUES ('{tool_name}', '{cache_key}', '{json_data}', {now})
        ON CONFLICT(tool_name, cache_key) DO UPDATE SET 
            response_data=excluded.response_data, 
            created_at=excluded.created_at;
        """
        
        try:
            await cls._session.call_tool("query", arguments={
                "db": DB_PATH,
                "sql": query,
                "readonly": False
            })
            logger.info("Cache SET for %s:%s (MCP)", tool_name, cache_key)
        except Exception as e:
            logger.error("Error writing cache via MCP: %s", e)

    @classmethod
    async def _set_cache_sqlite(cls, tool_name: str, cache_key: str, data: dict[str, Any]):
        """Set cache via direct SQLite."""
        import sqlite3
        
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            now = time.time()
            json_data = json.dumps(data)
            
            cursor.execute(
                """INSERT INTO api_cache (tool_name, cache_key, response_data, created_at) 
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(tool_name, cache_key) DO UPDATE SET 
                   response_data=excluded.response_data, 
                   created_at=excluded.created_at""",
                (tool_name, cache_key, json_data, now)
            )
            conn.commit()
            conn.close()
            logger.info("Cache SET for %s:%s (SQLite)", tool_name, cache_key)
        except Exception as e:
            logger.error("Error writing cache via SQLite: %s", e)

    # ── Watchlist Methods ────────────────────────────────────────────

    @classmethod
    async def add_to_watchlist(cls, ticker: str, notes: str = "") -> bool:
        """Add a stock to the watchlist."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            now = time.time()
            cursor.execute(
                "INSERT OR REPLACE INTO watchlist (ticker, added_at, notes) VALUES (?, ?, ?)",
                (ticker, now, notes)
            )
            conn.commit()
            conn.close()
            logger.info("Added %s to watchlist", ticker)
            return True
        except Exception as e:
            logger.error("Error adding to watchlist: %s", e)
            return False

    @classmethod
    async def remove_from_watchlist(cls, ticker: str) -> bool:
        """Remove a stock from the watchlist."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
            conn.commit()
            conn.close()
            logger.info("Removed %s from watchlist", ticker)
            return True
        except Exception as e:
            logger.error("Error removing from watchlist: %s", e)
            return False

    @classmethod
    async def get_watchlist(cls) -> list[dict]:
        """Get all stocks in the watchlist."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            cursor.execute("SELECT ticker, added_at, notes FROM watchlist ORDER BY added_at DESC")
            rows = cursor.fetchall()
            conn.close()
            return [
                {"ticker": row[0], "added_at": row[1], "notes": row[2]}
                for row in rows
            ]
        except Exception as e:
            logger.error("Error getting watchlist: %s", e)
            return []

    # ── Historical Analysis Methods ──────────────────────────────────

    @classmethod
    async def save_analysis_history(cls, ticker: str, analysis_data: dict) -> bool:
        """Save analysis result for historical tracking."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            now = time.time()
            json_data = json.dumps(analysis_data)
            cursor.execute(
                "INSERT INTO historical_analysis (ticker, analysis_data, created_at) VALUES (?, ?, ?)",
                (ticker, json_data, now)
            )
            conn.commit()
            conn.close()
            logger.info("Saved analysis history for %s", ticker)
            return True
        except Exception as e:
            logger.error("Error saving analysis history: %s", e)
            return False

    @classmethod
    async def get_analysis_history(cls, ticker: str, limit: int = 30) -> list[dict]:
        """Get historical analysis for a ticker."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT analysis_data, created_at FROM historical_analysis WHERE ticker = ? ORDER BY created_at DESC LIMIT ?",
                (ticker, limit)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {"analysis": json.loads(row[0]), "created_at": row[1]}
                for row in rows
            ]
        except Exception as e:
            logger.error("Error getting analysis history: %s", e)
            return []

    # ── Earnings Calendar Methods ────────────────────────────────────

    @classmethod
    async def save_earnings(cls, ticker: str, earnings_date: str, eps_estimate: float = None, revenue_estimate: float = None) -> bool:
        """Save earnings data."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            now = time.time()
            cursor.execute(
                """INSERT OR REPLACE INTO earnings_calendar 
                   (ticker, earnings_date, eps_estimate, revenue_estimate, updated_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (ticker, earnings_date, eps_estimate, revenue_estimate, now)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error("Error saving earnings: %s", e)
            return False

    @classmethod
    async def get_upcoming_earnings(cls, days: int = 30) -> list[dict]:
        """Get upcoming earnings within specified days."""
        import sqlite3
        from datetime import datetime, timedelta
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT ticker, earnings_date, eps_estimate, revenue_estimate FROM earnings_calendar WHERE earnings_date BETWEEN ? AND ? ORDER BY earnings_date",
                (today, future)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "ticker": row[0],
                    "earnings_date": row[1],
                    "eps_estimate": row[2],
                    "revenue_estimate": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error("Error getting earnings: %s", e)
            return []

    # ── Dividend Methods ─────────────────────────────────────────────

    @classmethod
    async def save_dividend(cls, ticker: str, ex_date: str, amount: float, payment_date: str = None, yield_percent: float = None) -> bool:
        """Save dividend data."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO dividend_history 
                   (ticker, ex_date, payment_date, amount, yield_percent) 
                   VALUES (?, ?, ?, ?, ?)""",
                (ticker, ex_date, payment_date, amount, yield_percent)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error("Error saving dividend: %s", e)
            return False

    @classmethod
    async def get_dividend_history(cls, ticker: str) -> list[dict]:
        """Get dividend history for a ticker."""
        import sqlite3
        try:
            conn = sqlite3.connect(cls._sqlite_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ex_date, payment_date, amount, yield_percent FROM dividend_history WHERE ticker = ? ORDER BY ex_date DESC",
                (ticker,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "ex_date": row[0],
                    "payment_date": row[1],
                    "amount": row[2],
                    "yield_percent": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error("Error getting dividend history: %s", e)
            return []


# Backwards compatibility alias
SQLiteMCPTool = SQLiteCacheTool
