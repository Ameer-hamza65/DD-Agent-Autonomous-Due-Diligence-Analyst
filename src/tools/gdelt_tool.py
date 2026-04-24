"""GDELT - free real-time news data."""
import requests
from typing import List, Dict
from urllib.parse import quote


def get_news_events(query: str, limit: int = 25, timespan: str = "3months") -> List[Dict]:
    try:
        q = quote(f'"{query}"')
        url = (f"https://api.gdeltproject.org/api/v2/doc/doc"
               f"?query={q}&mode=ArtList&maxrecords={limit}"
               f"&timespan={timespan}&format=json&sort=DateDesc")
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return []
        events = []
        for a in r.json().get("articles", []):
            events.append({
                "title": a.get("title"),
                "url": a.get("url"),
                "domain": a.get("domain"),
                "date": a.get("seendate"),
                "tone": a.get("tone"),
            })
        return events
    except Exception as e:
        print(f"GDELT error: {e}")
        return []


def summarize_news_sentiment(events: List[Dict]) -> Dict:
    if not events:
        return {"avg_tone": 0, "count": 0, "negative_pct": 0}
    tones = [float(e["tone"]) for e in events if e.get("tone") is not None]
    if not tones:
        return {"avg_tone": 0, "count": len(events), "negative_pct": 0}
    neg = sum(1 for t in tones if t < -2)
    return {
        "avg_tone": sum(tones) / len(tones),
        "count": len(tones),
        "negative_pct": (neg / len(tones)) * 100,
    }
