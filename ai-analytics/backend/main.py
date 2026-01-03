from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Internal imports (based on locked structure)
from config import settings
from excel_loader import (
    validate_report_type,
    load_excel_dataframe,
    dataframe_to_response,
    get_excel_path
)
from state import DashboardState

# (Stub – replace with real LangGraph runner)
from langgraph.runner import run_langgraph


# --------------------------------------------------
# App setup
# --------------------------------------------------
app = FastAPI(title="AI Reports Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 1️⃣ HEALTH CHECK
# --------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-reports-backend"
    }

# --------------------------------------------------
# 2️⃣ REPORT LIST (PAGE 2)
# URLs:
# /reports/design/custom-report-list
# /reports/design/project-report-list
# /reports/design/document-report-list
# --------------------------------------------------
from excel_loader import find_excel_file

@app.get("/reports/design/{report_type}-list")
def list_reports(report_type: str):
    validate_report_type(report_type)

    base_dir = settings.DATA_ROOT / report_type
    results = []

    for report_dir in base_dir.iterdir():
        try:
            excel_path = find_excel_file(report_type, report_dir.name)
            results.append({
                "report_id": report_dir.name,
                "project_name": excel_path.stem,  # filename = project name
                "excel_file": excel_path.name
            })
        except HTTPException:
            continue

    return results


# --------------------------------------------------
# 3️⃣ REPORT DETAIL – LOAD EXCEL (PAGE 3)
# URL:
# /reports/design/{type}/detail/{id}/data
# --------------------------------------------------
@app.get("/reports/design/{report_type}/detail/{report_id}/data")
def report_detail_data(report_type: str, report_id: str):
    df, project_name = load_excel_dataframe(report_type, report_id)
    return dataframe_to_response(df, project_name)

# --------------------------------------------------
# 4️⃣ REPORT DETAIL – CHATBOT → DASHBOARD
# URL:
# /reports/design/{type}/detail/{id}/chat
# --------------------------------------------------
@app.post("/reports/design/{report_type}/detail/{report_id}/chat")
def chat_and_generate_dashboard(
    report_type: str,
    report_id: str,
    payload: Dict[str, Any]
):
    validate_report_type(report_type)

    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Load Excel
    df = load_excel_dataframe(report_type, report_id)

    # Prepare LangGraph state
    state: DashboardState = {
        "report_type": report_type,
        "report_id": int(report_id),
        "prompt": prompt,
        "dataframe": df,
        "charts": [],
        "data": {},
        "summary": ""
    }

    # 👉 Activate ALL agents via LangGraph
    result = run_langgraph(state)

    # Expected result format (frontend-ready):
    # {
    #   summary: str
    #   kpis: [{name, value}]
    #   charts: [{id, option}]
    # }

    return result
