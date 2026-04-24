"""SEC EDGAR wrapper - free, only User-Agent header required."""
import os
import requests
from typing import Dict, Optional

USER_AGENT = os.getenv("SEC_USER_AGENT", "DDAgent research@example.com")
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}


def ticker_to_cik(ticker: str) -> Optional[str]:
    try:
        r = requests.get("https://www.sec.gov/files/company_tickers.json",
                         headers=HEADERS, timeout=15)
        r.raise_for_status()
        for v in r.json().values():
            if v["ticker"].upper() == ticker.upper():
                return str(v["cik_str"]).zfill(10)
    except Exception as e:
        print(f"CIK lookup failed: {e}")
    return None


def get_recent_filings(ticker: str, limit: int = 5) -> Dict:
    cik = ticker_to_cik(ticker)
    if not cik:
        return {"error": "CIK not found", "ticker": ticker}
    try:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        filings = []
        for i, form in enumerate(forms):
            if form in ("10-K", "10-Q", "8-K", "20-F", "DEF 14A"):
                accession_clean = accessions[i].replace("-", "")
                filings.append({
                    "form": form,
                    "date": dates[i],
                    "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{primary_docs[i]}",
                })
                if len(filings) >= limit:
                    break
        return {
            "cik": cik,
            "company_name": data.get("name"),
            "sic_description": data.get("sicDescription"),
            "filings": filings,
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def get_risk_factors_summary(ticker: str) -> str:
    f = get_recent_filings(ticker, limit=3)
    if "error" in f:
        return f"Could not fetch SEC filings: {f['error']}"
    lines = [f"Company: {f.get('company_name')} | SIC: {f.get('sic_description')}"]
    lines.append("Recent filings:")
    for x in f.get("filings", []):
        lines.append(f"  - {x['form']} ({x['date']}): {x['url']}")
    return "\n".join(lines)
