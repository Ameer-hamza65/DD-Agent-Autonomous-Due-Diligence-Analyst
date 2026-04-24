#!/bin/bash
# Starts both API + UI in dev mode
echo "Starting FastAPI on :8000 and Streamlit on :8501..."
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 2
streamlit run app.py
kill $API_PID
