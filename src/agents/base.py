"""Shared LLM helpers."""
import os
from langchain_openai import ChatOpenAI

DEFAULT_MODEL = os.getenv("DD_MODEL", "gpt-4o-mini")


def get_llm(temperature: float = 0.0, model: str = None):
    return ChatOpenAI(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


SEVERITY_RULES = """
Severity rules:
- "red": Material risk that could meaningfully impact valuation
- "yellow": Notable concern requiring monitoring
- "info": Neutral or positive observation
Confidence: 0.0-1.0 based on source quality and evidence strength.
"""
