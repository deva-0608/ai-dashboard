# backend/langgraph/runner.py

from langgraph.graph import StateGraph
from state import DashboardState

from langgraph.agents.schema_agent import schema_agent
from langgraph.agents.intent_agent import intent_agent
from langgraph.agents.query_agent import query_agent
from langgraph.agents.viz_agent import viz_agent
from langgraph.agents.kpi_agent import kpi_agent
from langgraph.agents.insight_agent import insight_agent

from dotenv import load_dotenv
import math
import numpy as np

load_dotenv()


# --------------------------------------------------
# JSON safety helper
# --------------------------------------------------
def make_json_safe(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    else:
        return obj


# --------------------------------------------------
# Helper node: inject final columns (SAFE)
# --------------------------------------------------
def inject_final_columns(state: DashboardState) -> dict:
    table = state.get("aggregated_data", {}).get("table")
    if table is not None:
        return {
            "intent": {
                **state.get("intent", {}),
                "_available_columns": table.columns.tolist()
            }
        }
    return {}


# --------------------------------------------------
# LangGraph runner
# --------------------------------------------------
def run_langgraph(initial_state: DashboardState):
    graph = StateGraph(DashboardState)

    # Register nodes
    graph.add_node("schema", schema_agent)
    graph.add_node("intent", intent_agent)
    graph.add_node("query", query_agent)
    graph.add_node("inject_columns", inject_final_columns)
    graph.add_node("viz", viz_agent)
    graph.add_node("kpi", kpi_agent)
    graph.add_node("insight", insight_agent)

    # Wire graph
    graph.set_entry_point("schema")
    graph.add_edge("schema", "intent")
    graph.add_edge("intent", "query")
    graph.add_edge("query", "inject_columns")
    graph.add_edge("inject_columns", "viz")
    graph.add_edge("viz", "kpi")
    graph.add_edge("kpi", "insight")

    # Compile & RUN ONCE
    app = graph.compile()
    final_state = app.invoke(initial_state)

    # -------------------------
    # Extract dataframe
    # -------------------------
    table = final_state.get("aggregated_data", {}).get("table")

    if table is not None:
        safe_table = (
            table
            .replace([np.inf, -np.inf], None)
            .where(table.notna(), None)
        )
        data = safe_table.to_dict("records")
    else:
        data = []

    # -------------------------
    # Final response
    # -------------------------
    response = {
        "summary": final_state.get("summary", ""),
        "kpis": final_state.get("kpis", []),
        "charts": final_state.get("charts", []),
        "data": data
    }

    print("✅ FINAL DASHBOARD OUTPUT:", response)

    return make_json_safe(response)
