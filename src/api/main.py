"""FastAPI backend for the DD Agent."""
import os
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from src.api.schemas import (
    AnalyzeRequest, JobCreatedResponse, JobStatus, AnalysisResult,
    FindingResponse,
)
from src.api.jobs import create_job, get_job, list_jobs
from src.api.runner import run_analysis

load_dotenv()

app = FastAPI(
    title="Autonomous DD Agent API",
    description="Multi-agent due diligence system powered by LangGraph",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "Autonomous DD Agent",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "POST /analyze": "Start a new DD analysis (returns job_id)",
            "GET /jobs/{job_id}": "Get job status",
            "GET /jobs/{job_id}/result": "Get full result when completed",
            "GET /jobs/{job_id}/report.pdf": "Download PDF report",
            "GET /jobs": "List recent jobs",
        }
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok",
            "openai_configured": bool(os.getenv("OPENAI_API_KEY"))}


@app.post("/analyze", response_model=JobCreatedResponse, tags=["analysis"])
def start_analysis(req: AnalyzeRequest, background: BackgroundTasks):
    """Kick off a DD analysis as a background job. Returns immediately."""
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY not configured on server")
    job_id = create_job(req.ticker)
    background.add_task(run_analysis, job_id, req.ticker, req.max_iterations)
    return JobCreatedResponse(job_id=job_id)


@app.get("/jobs/{job_id}", response_model=JobStatus, tags=["analysis"])
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        ticker=job["ticker"],
        progress=job["progress"],
        current_step=job.get("current_step"),
        error=job.get("error"),
    )


@app.get("/jobs/{job_id}/result", response_model=AnalysisResult, tags=["analysis"])
def job_result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        return AnalysisResult(
            job_id=job_id, status=job["status"], ticker=job["ticker"],
            error=job.get("error"))

    state = job["result"] or {}

    def to_findings(items):
        return [FindingResponse(**f) for f in items]

    return AnalysisResult(
        job_id=job_id,
        status="completed",
        ticker=state.get("ticker", job["ticker"]),
        company_name=state.get("company_name"),
        rating=state.get("rating"),
        red_flag_score=state.get("red_flag_score"),
        score_breakdown=state.get("score_breakdown", {}),
        top_red_flags=to_findings(state.get("top_red_flags", [])),
        top_strengths=to_findings(state.get("top_strengths", [])),
        all_findings=to_findings(state.get("findings", [])),
        iterations=state.get("iteration", 0),
        report_pdf_url=f"/jobs/{job_id}/report.pdf"
                      if state.get("report_pdf_path") else None,
    )


@app.get("/jobs/{job_id}/report.pdf", tags=["analysis"])
def job_pdf(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        raise HTTPException(409, f"Job is {job['status']}, not completed")
    pdf_path = (job["result"] or {}).get("report_pdf_path")
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(404, "PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf",
                        filename=Path(pdf_path).name)


@app.get("/jobs", tags=["analysis"])
def all_jobs(limit: int = 50):
    jobs = list_jobs(limit)
    return {"count": len(jobs), "jobs": [
        {"job_id": j["job_id"], "ticker": j["ticker"],
         "status": j["status"], "progress": j["progress"],
         "created_at": j["created_at"]} for j in jobs
    ]}
