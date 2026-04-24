from src.tools.yfinance_tool import get_financial_snapshot


def orchestrator_node(state: dict) -> dict:
    ticker = state["ticker"].upper().strip()
    snapshot = get_financial_snapshot(ticker)
    company_name = snapshot.get("company_name") or state.get("company_name") or ticker
    return {
        "ticker": ticker,
        "company_name": company_name,
        "iteration": 0,
        "max_iterations": state.get("max_iterations", 2),
        "findings": [],
        "critiques": [],
    }
