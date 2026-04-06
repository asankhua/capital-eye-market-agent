"""Finnhub API integration for market data - Using DUMMY DATA for testing."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# DUMMY DATA FOR UI TESTING
DUMMY_EARNINGS = [
    {"symbol": "AAPL", "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), "epsEstimate": 1.89, "revenueEstimate": 119200000000, "fiscalPeriod": "Q1 2026"},
    {"symbol": "MSFT", "date": (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"), "epsEstimate": 3.12, "revenueEstimate": 67800000000, "fiscalPeriod": "Q3 2026"},
    {"symbol": "GOOGL", "date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"), "epsEstimate": 1.95, "revenueEstimate": 84500000000, "fiscalPeriod": "Q1 2026"},
    {"symbol": "AMZN", "date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"), "epsEstimate": 1.35, "revenueEstimate": 156800000000, "fiscalPeriod": "Q1 2026"},
    {"symbol": "TSLA", "date": (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d"), "epsEstimate": 0.89, "revenueEstimate": 26800000000, "fiscalPeriod": "Q1 2026"},
    {"symbol": "META", "date": (datetime.now() + timedelta(days=22)).strftime("%Y-%m-%d"), "epsEstimate": 6.12, "revenueEstimate": 42500000000, "fiscalPeriod": "Q1 2026"},
    {"symbol": "NVDA", "date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"), "epsEstimate": 0.95, "revenueEstimate": 31200000000, "fiscalPeriod": "Q4 2025"},
    {"symbol": "NFLX", "date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"), "epsEstimate": 5.45, "revenueEstimate": 10200000000, "fiscalPeriod": "Q1 2026"},
]

DUMMY_MARKET_MOVERS = {
    "gainers": [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "price": 2875.50, "change": 42.80, "change_percent": 5.07, "volume": 4850000},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 4165.20, "change": 182.30, "change_percent": 4.57, "volume": 5230000},
        {"symbol": "INFY", "name": "Infosys Ltd", "price": 1898.75, "change": 71.80, "change_percent": 3.94, "volume": 2150000},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "price": 1575.30, "change": 50.90, "change_percent": 3.35, "volume": 9820000},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "price": 985.45, "change": 27.20, "change_percent": 2.84, "volume": 1270000},
        {"symbol": "ITC", "name": "ITC Ltd", "price": 425.65, "change": 10.85, "change_percent": 2.61, "volume": 4560000},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "price": 1725.80, "change": 42.50, "change_percent": 2.52, "volume": 890000},
        {"symbol": "WIPRO", "name": "Wipro Ltd", "price": 285.45, "change": 6.25, "change_percent": 2.24, "volume": 670000},
        {"symbol": "ADANIENT", "name": "Adani Enterprises", "price": 2185.60, "change": 45.30, "change_percent": 2.12, "volume": 1230000},
        {"symbol": "TITAN", "name": "Titan Company Ltd", "price": 3125.40, "change": 61.80, "change_percent": 2.01, "volume": 890000},
    ],
    "losers": [
        {"symbol": "VEDL", "name": "Vedanta Ltd", "price": 425.80, "change": -26.90, "change_percent": -5.94, "volume": 7850000},
        {"symbol": "YESBANK", "name": "Yes Bank Ltd", "price": 17.80, "change": -0.90, "change_percent": -4.80, "volume": 1560000},
        {"symbol": "ZOMATO", "name": "Zomato Ltd", "price": 228.40, "change": -8.55, "change_percent": -3.60, "volume": 450000},
        {"symbol": "PAYTM", "name": "One97 Communications", "price": 625.30, "change": -18.70, "change_percent": -2.90, "volume": 2340000},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "price": 985.60, "change": -26.75, "change_percent": -2.64, "volume": 1870000},
        {"symbol": "DLF", "name": "DLF Ltd", "price": 685.40, "change": -18.30, "change_percent": -2.60, "volume": 340000},
        {"symbol": "JINDALSTEL", "name": "Jindal Steel & Power", "price": 785.20, "change": -17.80, "change_percent": -2.21, "volume": 98000},
        {"symbol": "BANKBARODA", "name": "Bank of Baroda", "price": 215.80, "change": -4.25, "change_percent": -1.93, "volume": 120000},
        {"symbol": "CANBK", "name": "Canara Bank", "price": 345.60, "change": -6.25, "change_percent": -1.78, "volume": 89000},
        {"symbol": "IOB", "name": "Indian Overseas Bank", "price": 42.15, "change": -0.73, "change_percent": -1.71, "volume": 15600},
    ],
    "active": [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "price": 2875.50, "change": 42.80, "change_percent": 5.07, "volume": 9820000},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "price": 1575.30, "change": 50.90, "change_percent": 3.35, "volume": 4850000},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 4165.20, "change": 182.30, "change_percent": 4.57, "volume": 5230000},
        {"symbol": "ITC", "name": "ITC Ltd", "price": 425.65, "change": 10.85, "change_percent": 2.61, "volume": 4560000},
        {"symbol": "VEDL", "name": "Vedanta Ltd", "price": 425.80, "change": -26.90, "change_percent": -5.94, "volume": 7850000},
        {"symbol": "INFY", "name": "Infosys Ltd", "price": 1898.75, "change": 71.80, "change_percent": 3.94, "volume": 4560000},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "price": 985.45, "change": 27.20, "change_percent": 2.84, "volume": 3870000},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "price": 1725.80, "change": 42.50, "change_percent": 2.52, "volume": 2150000},
        {"symbol": "ADANIENT", "name": "Adani Enterprises", "price": 2185.60, "change": 45.30, "change_percent": 2.12, "volume": 2180000},
        {"symbol": "TITAN", "name": "Titan Company Ltd", "price": 3125.40, "change": 61.80, "change_percent": 2.01, "volume": 2180000},
    ]
}

DUMMY_NEWS = [
    {
        "category": "general",
        "datetime": int((datetime.now() - timedelta(hours=2)).timestamp()),
        "headline": "Reliance Industries Reports Record Q3 Profits",
        "source": "Economic Times",
        "summary": "Reliance Industries Ltd reported a 15% YoY increase in net profit for Q3 FY26, driven by strong performance in retail and Jio segments.",
        "url": ""
    },
    {
        "category": "general",
        "datetime": int((datetime.now() - timedelta(hours=4)).timestamp()),
        "headline": "TCS Wins $500 Million Deal from European Bank",
        "source": "Business Standard",
        "summary": "Tata Consultancy Services secures a major digital transformation contract, boosting its Europe operations significantly.",
        "url": ""
    },
    {
        "category": "general",
        "datetime": int((datetime.now() - timedelta(hours=6)).timestamp()),
        "headline": "HDFC Bank Merger Synergies Exceed Expectations",
        "source": "Mint",
        "summary": "The merged entity shows improved operational efficiency and cross-selling opportunities between banking segments.",
        "url": ""
    },
    {
        "category": "general",
        "datetime": int((datetime.now() - timedelta(hours=8)).timestamp()),
        "headline": "Infosys Announces Special Dividend",
        "source": "CNBC-TV18",
        "summary": "Infosys declared a special dividend of Rs 18 per share alongside quarterly results, rewarding shareholders.",
        "url": ""
    },
    {
        "category": "general",
        "datetime": int((datetime.now() - timedelta(hours=12)).timestamp()),
        "headline": "Bharti Airtel Expands 5G Coverage to 500 Cities",
        "source": "Financial Express",
        "summary": "Airtel accelerates 5G rollout across India, targeting complete coverage by end of 2026.",
        "url": ""
    },
    {
        "category": "forex",
        "datetime": int((datetime.now() - timedelta(hours=3)).timestamp()),
        "headline": "Rupee Strengthens Against Dollar",
        "source": "Moneycontrol",
        "summary": "Indian Rupee gains 0.5% against USD on strong FII inflows and positive trade data.",
        "url": ""
    },
    {
        "category": "crypto",
        "datetime": int((datetime.now() - timedelta(hours=1)).timestamp()),
        "headline": "SEBI Issues New Guidelines for Crypto Trading",
        "source": "Business Line",
        "summary": "Regulator introduces framework for monitoring virtual digital assets and protecting investors.",
        "url": ""
    },
    {
        "category": "merger",
        "datetime": int((datetime.now() - timedelta(hours=5)).timestamp()),
        "headline": "Adani Group Acquires Major Port Assets",
        "source": "Economic Times",
        "summary": "Strategic acquisition strengthens Adani Ports' position as India's largest port operator.",
        "url": ""
    },
]

DUMMY_SECTOR_PERFORMANCE = [
    {"sector": "Technology", "change_percent": 2.85},
    {"sector": "Communication Services", "change_percent": 2.14},
    {"sector": "Consumer Discretionary", "change_percent": 1.67},
    {"sector": "Financials", "change_percent": 0.94},
    {"sector": "Industrials", "change_percent": 0.58},
    {"sector": "Real Estate", "change_percent": 0.32},
    {"sector": "Materials", "change_percent": -0.15},
    {"sector": "Health Care", "change_percent": -0.42},
    {"sector": "Consumer Staples", "change_percent": -0.68},
    {"sector": "Energy", "change_percent": -0.95},
    {"sector": "Utilities", "change_percent": -1.23},
]

DUMMY_COMPANY_NEWS = {
    "AAPL": [
        {
            "category": "company",
            "datetime": int((datetime.now() - timedelta(hours=6)).timestamp()),
            "headline": "Apple iPhone 16 Production Ramping Up",
            "source": "TechCrunch",
            "summary": "Apple suppliers report increased orders ahead of fall launch. New AI features expected to drive upgrade cycle.",
            "url": "https://finance.yahoo.com/news/apple-iphone-16"
        },
        {
            "category": "company",
            "datetime": int((datetime.now() - timedelta(hours=18)).timestamp()),
            "headline": "Apple Vision Pro Sales Exceed Expectations",
            "source": "Bloomberg",
            "summary": "Mixed reality headset showing stronger than anticipated adoption among enterprise customers.",
            "url": "https://finance.yahoo.com/news/apple-vision-pro"
        },
    ],
    "TSLA": [
        {
            "category": "company",
            "datetime": int((datetime.now() - timedelta(hours=3)).timestamp()),
            "headline": "Tesla Robotaxi Service Launch Date Announced",
            "source": "Electrek",
            "summary": "Elon Musk confirms autonomous taxi service will begin operations in Austin, Texas next month.",
            "url": "https://finance.yahoo.com/news/tesla-robotaxi"
        },
        {
            "category": "company",
            "datetime": int((datetime.now() - timedelta(hours=14)).timestamp()),
            "headline": "Tesla Energy Storage Business Booms",
            "source": "Reuters",
            "summary": "Megapack deployments exceed targets as grid storage demand surges globally.",
            "url": "https://finance.yahoo.com/news/tesla-energy"
        },
    ],
}

class FinnhubTool:
    """Tool for fetching market data from Finnhub API - Using DUMMY DATA."""
    
    def __init__(self):
        print("[Finnhub] Initialized with DUMMY DATA mode")
    
    def get_earnings_calendar(self, symbol: Optional[str] = None, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get earnings calendar - Returns DUMMY DATA."""
        print(f"[Finnhub] Returning dummy earnings data for {symbol if symbol else 'all symbols'}")
        if symbol:
            return [e for e in DUMMY_EARNINGS if e["symbol"] == symbol.upper()]
        return DUMMY_EARNINGS
    
    def get_market_news(self, category: str = "general", symbol: Optional[str] = None) -> List[Dict]:
        """Get market news - Returns DUMMY DATA."""
        print(f"[Finnhub] Returning dummy news for category={category}")
        if symbol:
            return DUMMY_COMPANY_NEWS.get(symbol.upper(), [])
        return [n for n in DUMMY_NEWS if category == "general" or n["category"] == category]
    
    def get_company_news(self, symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get company-specific news - Returns DUMMY DATA."""
        print(f"[Finnhub] Returning dummy news for {symbol}")
        return DUMMY_COMPANY_NEWS.get(symbol.upper(), [])
    
    def get_market_movers(self, type: str = "gainers") -> List[Dict]:
        """Get market movers - Returns DUMMY DATA."""
        print(f"[Finnhub] Returning dummy {type} data")
        return DUMMY_MARKET_MOVERS.get(type, DUMMY_MARKET_MOVERS["gainers"])
    
    def get_sector_performance(self) -> List[Dict]:
        """Get sector performance - Returns DUMMY DATA."""
        print("[Finnhub] Returning dummy sector performance data")
        return DUMMY_SECTOR_PERFORMANCE
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get stock quote - Returns DUMMY DATA."""
        print(f"[Finnhub] Returning dummy quote for {symbol}")
        return {
            "c": 150.25,
            "d": 2.15,
            "dp": 1.45,
            "h": 152.30,
            "l": 148.90,
            "o": 149.50,
            "pc": 148.10,
            "t": int(datetime.now().timestamp())
        }
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get company profile - Returns DUMMY DATA."""
        print(f"[Finnhub] Returning dummy profile for {symbol}")
        return {
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "finnhubIndustry": "Technology",
            "ipo": "1980-12-12",
            "logo": "https://logo.clearbit.com/apple.com",
            "marketCapitalization": 2800.5,
            "name": f"{symbol.upper()} Inc",
            "phone": "1-408-996-1010",
            "shareOutstanding": 15400.0,
            "ticker": symbol.upper(),
            "weburl": f"https://www.{symbol.lower()}.com"
        }

# Global instance
finnhub_tool = FinnhubTool()
