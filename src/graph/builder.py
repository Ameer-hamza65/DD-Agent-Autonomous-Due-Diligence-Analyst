"""LangGraph wiring - parallel fan-out + critic loop."""
from langgraph.graph import StateGraph, START, END
from src.graph.state import DDState
from src.agents.orchestrator import orchestrator_node
from src.agents.financial_analyst import financial_analyst_node
from src.agents.news_analyst import news_analyst_node
from src.agents.tech_analyst import tech_analyst_node
from src.agents.market_analyst import market_analyst_node
from src.agents.risk_analyst import risk_analyst_node
from src.agents.critic import critic_node
from src.agents.scorer import scoring_node
from src.agents.report_writer import report_writer_node


def _join(state: dict) -> dict:
    return {}


def should_continue(state: dict) -> str:
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", 2)
    has_high = any(c.get("severity") == "high"
                   for c in state.get("critiques", []))
    if iteration >= max_iter or not has_high:
        return "scorer"
    return "scorer"  # safe default; extend to revise router for full cycling


def build_graph():
    g = StateGraph(DDState)
    g.add_node("orchestrator", orchestrator_node)
    g.add_node("financial", financial_analyst_node)
    g.add_node("news", news_analyst_node)
    g.add_node("tech", tech_analyst_node)
    g.add_node("market", market_analyst_node)
    g.add_node("risk", risk_analyst_node)
    g.add_node("join", _join)
    g.add_node("critic", critic_node)
    g.add_node("scorer", scoring_node)
    g.add_node("report", report_writer_node)

    g.add_edge(START, "orchestrator")
    for analyst in ["financial", "news", "tech", "market", "risk"]:
        g.add_edge("orchestrator", analyst)
        g.add_edge(analyst, "join")
    g.add_edge("join", "critic")
    g.add_conditional_edges("critic", should_continue,
                            {"scorer": "scorer"})
    g.add_edge("scorer", "report")
    g.add_edge("report", END)
    return g.compile()
