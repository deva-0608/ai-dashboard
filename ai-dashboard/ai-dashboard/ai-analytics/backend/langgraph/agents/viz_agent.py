# backend/langgraph/agents/viz_agent.py

from state import DashboardState
from utils.charts_utils import build_chart
import pandas as pd


COUNT_ALIASES = {
    "count",
    "total",
    "frequency",
    "species_count",
    "row_count"
}


def viz_agent(state: DashboardState) -> dict:
    """
    Viz agent:
    - Uses FINAL dataframe (after computations)
    - Fixes bad LLM chart specs automatically
    - Produces only meaningful charts
    """

    df: pd.DataFrame | None = state.get("aggregated_data", {}).get("table")
    intent = state.get("intent", {})
    chart_specs = intent.get("charts", [])

    if df is None or df.empty or not isinstance(chart_specs, list):
        return {"charts": []}

    charts = []

    for spec in chart_specs:
        try:
            chart_type = spec.get("type")
            x = spec.get("x")
            y = spec.get("y")
            title = spec.get("title")

            # -------------------------
            # BASIC VALIDATION
            # -------------------------
            if not chart_type or not x or x not in df.columns:
                continue

            # -------------------------
            # NORMALIZE y = count aliases
            # -------------------------
            if isinstance(y, str) and y.lower() in COUNT_ALIASES:
                y = None  # force COUNT plot

            # -------------------------
            # HISTOGRAM FIX
            # categorical histogram → bar count
            # -------------------------
            if chart_type == "histogram":
                if not pd.api.types.is_numeric_dtype(df[x]):
                    chart_type = "bar"
                    y = None

            # -------------------------
            # BUILD CHART
            # -------------------------
            option = build_chart(
                df=df,
                chart_type=chart_type,
                x=x,
                y=y,
                title=title
            )

            if option:
                charts.append({
                    "id": f"chart_{len(charts) + 1}",
                    "option": option
                })

        except Exception as e:
            print("⚠️ Chart skipped:", e)
            continue

    return {"charts": charts}
