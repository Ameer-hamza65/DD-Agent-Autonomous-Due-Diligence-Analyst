# Step-by-Step Implementation Guide (FastAPI Edition)

## Day 1: Local Setup & Tool Tests

```bash
cd dd-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY + SEC_USER_AGENT
```

Test each data tool independently:
```bash
python -c "from src.tools.yfinance_tool import get_financial_snapshot; print(get_financial_snapshot('AAPL'))"
python -c "from src.tools.sec_edgar import get_recent_filings; print(get_recent_filings('AAPL'))"
python -c "from src.tools.gdelt_tool import get_news_events; print(get_news_events('Apple', limit=3))"
python -c "from src.tools.github_tool import get_tech_signals; print(get_tech_signals('apple'))"
```

## Day 2: Run the FastAPI Backend

```bash
uvicorn src.api.main:app --reload
```

Open `http://localhost:8000/docs` — you get a full Swagger UI. Try the `/analyze` endpoint with `{"ticker": "AAPL"}`. Copy the returned `job_id` and poll `/jobs/{job_id}`.

## Day 3: Connect the Streamlit UI

In a second terminal:
```bash
streamlit run app.py
```

The UI will show ✅ green status if the API is reachable. Submit a ticker and watch the live progress.

## Day 4-5: Iterate on Agent Prompts

Open `src/agents/financial_analyst.py` etc. — improve the `SYSTEM_PROMPT`. Each agent runs independently, so you can test one at a time:

```python
from src.agents.financial_analyst import financial_analyst_node
print(financial_analyst_node({"ticker": "AAPL"}))
```

## Day 6-7: Enable Real Critic Debate Loop

Currently `src/graph/builder.py` routes `should_continue` safely to `scorer`. To enable cycling:
1. Add a `revise_router` node that re-invokes specific analyst nodes based on critique targets
2. Map `"revise" → "revise_router" → analyst nodes`
3. Cap iterations at 2 to avoid infinite loops

## Day 8: Add LLM Caching (saves money)

In `src/api/main.py`, add at the top:
```python
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
set_llm_cache(SQLiteCache(database_path=".langchain.db"))
```

Re-running the same ticker is now free.

## Day 9-10: Build Eval Suite

Create `src/evals/benchmark.py` that loops through known companies (healthy: AAPL, MSFT, COST; troubled: WBA, PARA) and validates the agent's red-flag detection.

## Day 11: Swap In-Memory Jobs for Redis (Optional Production Upgrade)

`src/api/jobs.py` uses a dict + threading lock. For multi-worker production:
1. `pip install redis`
2. Replace `_jobs` dict with Redis hash operations
3. Use Celery or RQ instead of `BackgroundTasks` for true distributed execution

## Day 12-13: Deploy

### Option A: Docker on any VPS (Render, Railway, Fly.io free tier)
```bash
docker-compose up -d
```

### Option B: Split deployment
- Backend → Render (free web service tier)
- Frontend → HuggingFace Spaces (Streamlit, free)
- Set `API_BASE_URL` env var in Spaces to your Render URL

## Day 14: Resume Polish

Your repo MUST have:
- ✅ Architecture diagram in README
- ✅ Sample real-company PDF committed to `reports/`
- ✅ OpenAPI Swagger screenshot
- ✅ 90-second Loom demo
- ✅ Medium blog post explaining the architecture

## Costs

- ~$0.05–$0.15 per analysis with `gpt-4o-mini`
- With LangChain SQLiteCache: dev iteration is free
- Hosting: $0 on free tiers
