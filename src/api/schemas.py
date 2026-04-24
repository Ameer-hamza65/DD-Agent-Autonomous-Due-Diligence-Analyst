"""Pydantic models for the FastAPI request/response contracts."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10,
                        description="US stock ticker (e.g. AAPL)")
    max_iterations: int = Field(default=2, ge=1, le=3)


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str = "pending"
    message: str = "Job queued for processing"


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | running | completed | failed
    ticker: str
    progress: int = 0  # 0-100
    current_step: Optional[str] = None
    error: Optional[str] = None


class FindingResponse(BaseModel):
    agent: str
    category: str
    claim: str
    evidence: str
    confidence: float
    severity: str
    sources: List[str] = []


class AnalysisResult(BaseModel):
    job_id: str
    status: str
    ticker: str
    company_name: Optional[str] = None
    rating: Optional[str] = None
    red_flag_score: Optional[float] = None
    score_breakdown: Dict[str, float] = {}
    top_red_flags: List[FindingResponse] = []
    top_strengths: List[FindingResponse] = []
    all_findings: List[FindingResponse] = []
    iterations: int = 0
    report_pdf_url: Optional[str] = None
    error: Optional[str] = None
