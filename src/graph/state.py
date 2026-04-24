"""Shared state schema for the LangGraph."""
from typing import TypedDict, Annotated, List, Dict, Optional
from operator import add
from pydantic import BaseModel, Field


class Finding(BaseModel):
    agent: str = Field(description="Which agent produced this")
    category: str = Field(description="financial | news | tech | market | risk")
    claim: str = Field(description="The factual claim")
    evidence: str = Field(description="Supporting evidence/data")
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str = Field(description="info | yellow | red")
    sources: List[str] = Field(default_factory=list)


class FindingList(BaseModel):
    findings: List[Finding]


class Critique(BaseModel):
    target_agent: str
    finding_index: int
    issue: str
    required_action: str
    severity: str  # low | medium | high


class CritiqueList(BaseModel):
    critiques: List[Critique]
    overall_assessment: str


class DDState(TypedDict, total=False):
    company_name: str
    ticker: str
    sec_filings: Dict
    financials: Dict
    news_events: List[Dict]
    github_metrics: Dict
    market_data: Dict
    findings: Annotated[List[Dict], add]
    critiques: Annotated[List[Dict], add]
    red_flag_score: Optional[float]
    score_breakdown: Dict
    rating: str
    top_red_flags: List[Dict]
    top_strengths: List[Dict]
    report_markdown: Optional[str]
    report_pdf_path: Optional[str]
    iteration: int
    max_iterations: int
