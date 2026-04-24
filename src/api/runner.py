"""Background job execution wrapper around the LangGraph."""
from src.api.jobs import update_job
from src.graph.builder import build_graph

# Order of nodes for progress reporting
NODE_ORDER = ["orchestrator", "financial", "news", "tech", "market", "risk",
              "join", "critic", "scorer", "report"]


def run_analysis(job_id: str, ticker: str, max_iterations: int = 2):
    """Runs the full graph synchronously inside a background thread."""
    try:
        update_job(job_id, status="running", progress=5,
                   current_step="building graph")
        graph = build_graph()
        initial = {"ticker": ticker.upper(), "max_iterations": max_iterations}

        # Stream events for progress tracking
        executed_nodes = []
        for event in graph.stream(initial, {"recursion_limit": 50}):
            for node_name in event.keys():
                executed_nodes.append(node_name)
                pct = min(int((len(executed_nodes) / len(NODE_ORDER)) * 90), 90)
                update_job(job_id, progress=pct, current_step=node_name)

        # Re-invoke for final state
        final_state = graph.invoke(initial, {"recursion_limit": 50})

        update_job(
            job_id,
            status="completed",
            progress=100,
            current_step="done",
            result=final_state,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        update_job(job_id, status="failed", error=str(e), progress=100)
