"""BSE Corporate Actions Tool - Fetches dividend and corporate action announcements from BSE India.

Provides:
  - Dividend announcements from BSE listed companies
  - Record dates, ex-dividend dates
  - Bonus, split, and other corporate actions
  - No API key required
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Any
import requests

from backend.tools.sqlite_mcp_tool import SQLiteMCPTool

logger = logging.getLogger("market_analyst.tools.bse_corporate_actions")


class BSECorporateActionsTool:
    """Tool for fetching corporate actions and dividend announcements from BSE India."""

    BSE_CORPORATE_ACTIONS_URL = "https://api.bseindia.com/BseIndiaAPI/api/CorporateAction/w"
    BSE_HOME_URL = "https://www.bseindia.com/"

    @staticmethod
    def _build_headers(referer: str | None = None) -> dict[str, str]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://www.bseindia.com",
            "Referer": referer or BSECorporateActionsTool.BSE_HOME_URL,
        }
        return headers

    @staticmethod
    def _parse_response_json(response: requests.Response) -> tuple[Any, dict[str, Any]]:
        content_type = response.headers.get("Content-Type", "")
        text = response.text or ""
        snippet = text[:240].replace("\n", " ").strip()
        diagnostics: dict[str, Any] = {
            "status_code": response.status_code,
            "content_type": content_type,
            "response_snippet": snippet,
        }

        # Best effort parse with validation and diagnostics.
        if "json" in content_type.lower():
            try:
                return response.json(), diagnostics
            except Exception as e:
                diagnostics["parse_error"] = f"json_content_type_parse_failed: {e}"
                return None, diagnostics

        try:
            return json.loads(text), diagnostics
        except Exception as e:
            diagnostics["parse_error"] = f"non_json_content_type_parse_failed: {e}"
            return None, diagnostics

    @staticmethod
    async def get_dividend_announcements(from_date: str = None, to_date: str = None) -> dict[str, Any]:
        """Fetch dividend announcements from BSE Corporate Actions API.
        
        Args:
            from_date: Start date in DD-MM-YYYY format (defaults to 30 days ago)
            to_date: End date in DD-MM-YYYY format (defaults to today)
            
        Returns:
            Dictionary with dividend announcements list
        """
        cache_key = "bse_dividend_announcements"
        
        # Check cache
        cached = await SQLiteMCPTool.get_cache("corporate_actions", cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time:
                cache_dt = datetime.fromisoformat(cached_time)
                if (datetime.now() - cache_dt).total_seconds() < 3600:  # 1 hour cache
                    return cached

        # Set default dates if not provided
        if not to_date:
            to_date = datetime.now().strftime("%d-%m-%Y")
        if not from_date:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")

        diagnostics: dict[str, Any] = {
            "source": "bse_corporate_actions_api",
            "attempts": 0,
            "status": "error",
        }

        try:
            params = {
                "fromDate": from_date,
                "toDate": to_date
            }

            logger.info(f"[BSECorporateActions] Fetching dividends from {from_date} to {to_date}")
            session = requests.Session()
            data = None
            last_error = None
            last_parse_diag: dict[str, Any] = {}

            # Bootstrap session cookies from BSE home, then retry API.
            for attempt in range(1, 4):
                diagnostics["attempts"] = attempt
                try:
                    if attempt == 1:
                        try:
                            session.get(
                                BSECorporateActionsTool.BSE_HOME_URL,
                                headers=BSECorporateActionsTool._build_headers(),
                                timeout=15,
                            )
                        except Exception as bootstrap_err:
                            logger.debug("[BSECorporateActions] bootstrap failed: %s", bootstrap_err)

                    response = session.get(
                        BSECorporateActionsTool.BSE_CORPORATE_ACTIONS_URL,
                        params=params,
                        headers=BSECorporateActionsTool._build_headers(
                            referer=BSECorporateActionsTool.BSE_HOME_URL
                        ),
                        timeout=20,
                    )
                    response.raise_for_status()
                    parsed, parse_diag = BSECorporateActionsTool._parse_response_json(response)
                    last_parse_diag = parse_diag
                    if parsed is None:
                        last_error = parse_diag.get("parse_error", "unknown_parse_error")
                        logger.warning(
                            "[BSECorporateActions] parse failed attempt %d: %s",
                            attempt,
                            last_error,
                        )
                        continue
                    data = parsed
                    break
                except Exception as attempt_err:
                    last_error = str(attempt_err)
                    logger.warning(
                        "[BSECorporateActions] request failed attempt %d: %s",
                        attempt,
                        attempt_err,
                    )
                    continue

            diagnostics.update(last_parse_diag)
            if data is None:
                diagnostics["status"] = "error"
                diagnostics["error"] = last_error or "all_attempts_failed"
                return {
                    "dividends": [],
                    "count": 0,
                    "from_date": from_date,
                    "to_date": to_date,
                    "error": diagnostics["error"],
                    "source": "bse_india",
                    "cached_at": datetime.now().isoformat(),
                    "diagnostics": diagnostics,
                }
            
            # Parse and filter for dividend announcements
            dividend_items = []
            if isinstance(data, list):
                for item in data:
                    # Check if it's a dividend announcement
                    purpose = item.get("Purpose", "").lower()
                    if "dividend" in purpose or "interim dividend" in purpose or "final dividend" in purpose:
                        dividend_items.append({
                            "company_name": item.get("LongName", item.get("ScripName", "Unknown")),
                            "symbol": item.get("ScripCode", ""),
                            "purpose": item.get("Purpose", ""),
                            "dividend_type": "interim" if "interim" in purpose else ("final" if "final" in purpose else "dividend"),
                            "record_date": item.get("RecDate", ""),
                            "ex_date": item.get("ExDate", ""),
                            "announcement_date": item.get("AnnouncementDate", ""),
                            "face_value": item.get("FaceValue", ""),
                            "source": "BSE India"
                        })
            else:
                diagnostics["status"] = "error"
                diagnostics["error"] = f"unexpected_payload_type:{type(data).__name__}"
                return {
                    "dividends": [],
                    "count": 0,
                    "from_date": from_date,
                    "to_date": to_date,
                    "error": diagnostics["error"],
                    "source": "bse_india",
                    "cached_at": datetime.now().isoformat(),
                    "diagnostics": diagnostics,
                }
            
            result = {
                "dividends": dividend_items,
                "count": len(dividend_items),
                "from_date": from_date,
                "to_date": to_date,
                "source": "bse_india",
                "cached_at": datetime.now().isoformat(),
                "diagnostics": {
                    **diagnostics,
                    "status": "ok" if dividend_items else "empty",
                },
            }
            
            await SQLiteMCPTool.set_cache("corporate_actions", cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"[BSECorporateActions] Error fetching dividends: {e}")
            return {
                "dividends": [],
                "count": 0,
                "from_date": from_date,
                "to_date": to_date,
                "error": str(e),
                "source": "bse_india",
                "cached_at": datetime.now().isoformat(),
                "diagnostics": {
                    **diagnostics,
                    "status": "error",
                    "error": str(e),
                },
            }

    @staticmethod
    async def get_upcoming_dividends(days_ahead: int = 30) -> dict[str, Any]:
        """Get upcoming dividend record dates for the next N days.
        
        Args:
            days_ahead: Number of days to look ahead (default 30)
            
        Returns:
            Dictionary with upcoming dividends
        """
        from_date = datetime.now().strftime("%d-%m-%Y")
        to_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%d-%m-%Y")
        
        result = await BSECorporateActionsTool.get_dividend_announcements(from_date, to_date)
        result["upcoming_days"] = days_ahead
        return result

    @staticmethod
    async def get_recent_dividends(days_back: int = 30) -> dict[str, Any]:
        """Get recently announced dividends from the past N days.
        
        Args:
            days_back: Number of days to look back (default 30)
            
        Returns:
            Dictionary with recent dividends
        """
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%m-%Y")
        to_date = datetime.now().strftime("%d-%m-%Y")
        
        result = await BSECorporateActionsTool.get_dividend_announcements(from_date, to_date)
        result["recent_days"] = days_back
        return result


# Global instance
bse_corporate_actions_tool = BSECorporateActionsTool()
