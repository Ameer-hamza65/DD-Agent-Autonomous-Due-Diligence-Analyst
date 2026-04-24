"""In-memory job store. Swap for Redis in production."""
import uuid
import threading
from typing import Dict, Optional
from datetime import datetime

_jobs: Dict[str, dict] = {}
_lock = threading.Lock()


def create_job(ticker: str) -> str:
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "ticker": ticker.upper(),
            "status": "pending",
            "progress": 0,
            "current_step": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
            "error": None,
        }
    return job_id


def update_job(job_id: str, **fields) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(fields)


def get_job(job_id: str) -> Optional[dict]:
    with _lock:
        return _jobs.get(job_id)


def list_jobs(limit: int = 50) -> list:
    with _lock:
        items = sorted(_jobs.values(), key=lambda j: j["created_at"],
                       reverse=True)
        return items[:limit]
