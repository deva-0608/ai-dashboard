from state import DashboardState
from utils.llm_factory import generate_with_gemini
import json
import pandas as pd


QUERY_PLAN_SCHEMA = """
Return JSON ONLY in this format:

{
  "filters": [
    {"column": "col", "operator": "==|!=|>|<|>=|<=", "value": "any"}
  ],
  "group_by": ["column"],
  "aggregations": [
    {"column": "col", "agg": "count|sum|avg|min|max", "alias": "name"}
  ],
  "sort": {"by": "column", "order": "asc|desc"},
  "limit": 20
}
"""

AGG_MAP = {
    "avg": "mean",
    "average": "mean",
    "mean": "mean",
    "count": "count",
    "sum": "sum",
    "min": "min",
    "max": "max"
}


def query_agent(state: DashboardState) -> dict:
    df: pd.DataFrame = state["dataframe"]
    intent = state.get("intent", {})
    dfq = df.copy()

    # --------------------------------------------------
    # 1️⃣ APPLY AI COMPUTATIONS (KEEP DATAFRAME)
    # --------------------------------------------------
    for step in intent.get("computations", []):
        if (
            step.get("operation") == "difference"
            and len(step.get("columns", [])) == 2
        ):
            c1, c2 = step["columns"]
            new_col = step.get("new_column", "difference")

            if c1 in dfq.columns and c2 in dfq.columns:
                dfq[c1] = pd.to_datetime(dfq[c1], errors="coerce")
                dfq[c2] = pd.to_datetime(dfq[c2], errors="coerce")
                dfq[new_col] = (dfq[c2] - dfq[c1]).dt.days

    # --------------------------------------------------
    # 2️⃣ ASK LLM FOR FILTER / KPI PLAN
    # --------------------------------------------------
    prompt = f"""
You are a data analyst.

User request:
{state["prompt"]}

Available columns:
{dfq.columns.tolist()}

Column types:
{dfq.dtypes.astype(str).to_dict()}

{QUERY_PLAN_SCHEMA}
"""

    response = generate_with_gemini(prompt, fallback_text="{}")

    try:
        plan = json.loads(response)
    except Exception:
        plan = {}

    # --------------------------------------------------
    # 3️⃣ APPLY FILTERS (NON-DESTRUCTIVE)
    # --------------------------------------------------
    for f in plan.get("filters", []):
        col, op, val = f.get("column"), f.get("operator"), f.get("value")
        if col not in dfq.columns:
            continue

        try:
            if op == "==": dfq = dfq[dfq[col] == val]
            elif op == "!=": dfq = dfq[dfq[col] != val]
            elif op == ">": dfq = dfq[dfq[col] > val]
            elif op == "<": dfq = dfq[dfq[col] < val]
            elif op == ">=": dfq = dfq[dfq[col] >= val]
            elif op == "<=": dfq = dfq[dfq[col] <= val]
        except Exception:
            continue

    # --------------------------------------------------
    # 4️⃣ COMPUTE KPIs (WITHOUT MODIFYING dfq)
    # --------------------------------------------------
    kpis = []

    for a in plan.get("aggregations", []):
        col = a.get("column")
        agg = AGG_MAP.get(a.get("agg"))
        name = a.get("alias")

        if col in dfq.columns and agg and hasattr(dfq[col], agg):
            try:
                value = getattr(dfq[col], agg)()
                kpis.append({
                    "name": name,
                    "value": float(value) if pd.notna(value) else None
                })
            except Exception:
                continue

    # --------------------------------------------------
    # 5️⃣ SORT & LIMIT (SAFE)
    # --------------------------------------------------
    sort = plan.get("sort")
    if sort and sort.get("by") in dfq.columns:
        dfq = dfq.sort_values(
            by=sort["by"],
            ascending=(sort.get("order") == "asc")
        )

    if plan.get("limit"):
        dfq = dfq.head(int(plan["limit"]))

    return {
        "aggregated_data": {
            "table": dfq    # ✅ dataframe AFTER computations
        },
        "kpis": kpis
    }
