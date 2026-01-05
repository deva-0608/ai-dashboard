# backend/langgraph/agents/kpi_agent.py

from state import DashboardState
import pandas as pd
import json
import math

from utils.llm_factory import generate_with_gemini


# Normalize LLM aggregation names → pandas
AGG_MAP = {
    "sum": "sum",
    "avg": "mean",
    "average": "mean",
    "mean": "mean",
    "count": "count",
    "min": "min",
    "max": "max"
}


def kpi_agent(state: DashboardState) -> dict:
    """
    Generate KPIs safely from the UPDATED dataframe.
    """

    # ✅ USE UPDATED DATAFRAME
    df: pd.DataFrame = (
        state.get("aggregated_data", {}).get("table")
    )

    if df is None or df.empty:
        return {"kpis": []}

    user_prompt: str = state.get("prompt", "")

    # -------------------------------
    # Build LLM prompt
    # -------------------------------
    llm_prompt = f"""
You are a data analyst.

User question:
{user_prompt}

Available numeric columns:
{list(df.select_dtypes(include='number').columns)}

Return ONLY valid JSON in this format:

[
  {{
    "name": "KPI Name",
    "column": "column_name",
    "operation": "sum|avg|count|min|max"
  }}
]

Rules:
- Use COUNT for ID-like columns
- Use AVG / MAX for duration or days
- Use SUM / AVG for financial values
- Do NOT explain anything
"""

    # -------------------------------
    # Ask LLM
    # -------------------------------
    response = generate_with_gemini(
        llm_prompt,
        fallback_text="[]"
    )

    try:
        kpi_plan = json.loads(response)
        if not isinstance(kpi_plan, list):
            return {"kpis": []}
    except Exception:
        return {"kpis": []}

    # -------------------------------
    # Execute KPI plan safely
    # -------------------------------
    kpis = []

    for kpi in kpi_plan:
        col = kpi.get("column")
        op = AGG_MAP.get(kpi.get("operation"))
        name = kpi.get("name", f"{kpi.get('operation')} {col}")

        if col not in df.columns or not op:
            continue

        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue

        try:
            value = getattr(series, op)()

            # ✅ JSON SAFE CHECK
            if value is None:
                continue
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                continue

            # Cast cleanly
            if op == "count":
                value = int(value)
            else:
                value = float(value)

            kpis.append({
                "name": name,
                "value": value
            })

        except Exception as e:
            print(f"⚠️ KPI calc failed for {col}: {e}")

    return {"kpis": kpis}
