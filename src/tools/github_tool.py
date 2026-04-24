"""GitHub API for tech health signals."""
import os
import requests
from typing import Dict, Optional

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def search_company_org(company_name: str) -> Optional[str]:
    try:
        q = company_name.lower().replace(" ", "")
        r = requests.get(f"https://api.github.com/orgs/{q}",
                         headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json().get("login")
    except Exception:
        pass
    return None


def get_org_metrics(org: str) -> Dict:
    try:
        r = requests.get(
            f"https://api.github.com/orgs/{org}/repos?per_page=100&sort=updated",
            headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return {"error": f"GitHub returned {r.status_code}"}
        repos = r.json()
        languages = {}
        for repo in repos:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        return {
            "org": org,
            "public_repos": len(repos),
            "total_stars": sum(r.get("stargazers_count", 0) for r in repos),
            "total_forks": sum(r.get("forks_count", 0) for r in repos),
            "top_languages": dict(sorted(languages.items(), key=lambda x: -x[1])[:5]),
        }
    except Exception as e:
        return {"error": str(e)}


def get_tech_signals(company_name: str) -> Dict:
    org = search_company_org(company_name)
    if not org:
        return {"has_github_presence": False, "note": "No public GitHub org found"}
    metrics = get_org_metrics(org)
    metrics["has_github_presence"] = True
    return metrics
