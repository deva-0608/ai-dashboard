from state import DashboardState
from utils.llm_factory import get_llm
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

def query_agent(state: DashboardState) -> dict:
    llm = get_llm(temperature=0)

    df: pd.DataFrame = state["dataframe"]
    schema = state["schema"]

    prompt = f"""
You are a data analyst.

User request:
{state["prompt"]}

Available columns:
{schema["columns"]}

Column types:
{schema["types"]}

{QUERY_PLAN_SCHEMA}
"""

    response = llm.invoke(prompt).content

    try:
        plan = json.loads(response)
    except Exception:
        raise ValueError("Invalid JSON query plan from LLM")

    dfq = df.copy()

    # Apply filters
    for f in plan.get("filters", []):
        col, op, val = f["column"], f["operator"], f["value"]
        if col not in dfq.columns:
            continue
        if op == "==": dfq = dfq[dfq[col] == val]
        elif op == "!=": dfq = dfq[dfq[col] != val]
        elif op == ">": dfq = dfq[dfq[col] > val]
        elif op == "<": dfq = dfq[dfq[col] < val]
        elif op == ">=": dfq = dfq[dfq[col] >= val]
        elif op == "<=": dfq = dfq[dfq[col] <= val]

    # Aggregations
    aggs = plan.get("aggregations", [])
    group_by = plan.get("group_by", [])

    if aggs:
        agg_dict = {
            a["alias"]: (a["column"], a["agg"])
            for a in aggs if a["column"] in dfq.columns
        }
        result = dfq.groupby(group_by).agg(**agg_dict).reset_index()
    else:
        result = dfq

    # Sort
    sort = plan.get("sort")
    if sort and sort["by"] in result.columns:
        result = result.sort_values(
            by=sort["by"],
            ascending=(sort["order"] == "asc")
        )

    # Limit
    if plan.get("limit"):
        result = result.head(plan["limit"])

    return {
        "aggregated_data": {
            "table": result
        }
    }
