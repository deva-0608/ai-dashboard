from state import DashboardState
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
import json

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
)

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

def query_agent(state: DashboardState) -> dict:
    df = state["dataframe"]
    schema = state["schema"]
    intent = state["intent"]

    prompt = f"""
You are a data analyst.

User request:
{state['prompt']}

Intent:
{intent}

Available columns:
{schema['columns']}

Column types:
{schema['types']}

{QUERY_PLAN_SCHEMA}
"""

    response = llm.invoke(prompt).content

    try:
        plan = json.loads(response)
    except Exception:
        raise ValueError("LLM returned invalid JSON query plan")

    # -----------------------------
    # SAFETY VALIDATION
    # -----------------------------
    allowed_cols = set(schema["columns"])

    for f in plan.get("filters", []):
        if f["column"] not in allowed_cols:
            raise ValueError(f"Invalid filter column: {f['column']}")

    for g in plan.get("group_by", []):
        if g not in allowed_cols:
            raise ValueError(f"Invalid group_by column: {g}")

    for a in plan.get("aggregations", []):
        if a["column"] not in allowed_cols:
            raise ValueError(f"Invalid aggregation column: {a['column']}")

    # -----------------------------
    # EXECUTE QUERY PLAN
    # -----------------------------
    dfq = df.copy()

    # Apply filters
    for f in plan.get("filters", []):
        col = f["column"]
        op = f["operator"]
        val = f["value"]

        if op == "==":
            dfq = dfq[dfq[col] == val]
        elif op == "!=":
            dfq = dfq[dfq[col] != val]
        elif op == ">":
            dfq = dfq[dfq[col] > val]
        elif op == "<":
            dfq = dfq[dfq[col] < val]
        elif op == ">=":
            dfq = dfq[dfq[col] >= val]
        elif op == "<=":
            dfq = dfq[dfq[col] <= val]

    # Group & aggregate
    group_by = plan.get("group_by", [])
    aggs = plan.get("aggregations", [])

    if aggs:
        agg_dict = {}
        for a in aggs:
            agg_dict[a["alias"]] = (a["column"], a["agg"])

        result = (
            dfq
            .groupby(group_by)
            .agg(**agg_dict)
            .reset_index()
        )
    else:
        result = dfq

    # Sort
    sort = plan.get("sort")
    if sort:
        result = result.sort_values(
            by=sort["by"],
            ascending=(sort["order"] == "asc")
        )

    # Limit
    limit = plan.get("limit")
    if limit:
        result = result.head(limit)

    return {
        "aggregated_data": {
            "table": result
        }
    }
