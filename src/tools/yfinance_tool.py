"""yfinance wrapper for financial snapshots."""
import yfinance as yf
from typing import Dict


def get_financial_snapshot(ticker: str) -> Dict:
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="1y")
        return {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "free_cash_flow": info.get("freeCashflow"),
            "total_revenue": info.get("totalRevenue"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            "return_on_equity": info.get("returnOnEquity"),
            "beta": info.get("beta"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "current_price": info.get("currentPrice"),
            "recommendation": info.get("recommendationKey"),
            "business_summary": (info.get("longBusinessSummary") or "")[:1500],
            "price_change_1y_pct": (
                ((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100
                if len(hist) > 0 else None
            ),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}
