# backend/langgraph/agents/viz_agent.py

from state import DashboardState
from utils.charts_utils import build_chart
import pandas as pd


def viz_agent(state: DashboardState) -> dict:
    """
    Validate chart feasibility against available dataframe
    and return only workable charts.
    """

    df = state.get("aggregated_data", {}).get("table")
    intent = state.get("intent", {})
    chart_specs = intent.get("charts", [])

    if df is None or df.empty or not isinstance(chart_specs, list):
        return {"charts": []}

    charts = []

    for i, spec in enumerate(chart_specs):
        chart_type = spec.get("type")
        x = spec.get("x")
        y = spec.get("y")
        title = spec.get("title")

        if not chart_type:
            continue

        # -----------------------------
        # FEASIBILITY CHECKS
        # -----------------------------
        try:
            # Bar / Line / Area
            if chart_type in {"bar", "line", "area"}:
                if x not in df.columns or y not in df.columns:
                    continue

            # Histogram
            elif chart_type == "histogram":
                if x not in df.columns:
                    continue
                if not pd.api.types.is_numeric_dtype(df[x]):
                    continue

            # Scatter
            elif chart_type == "scatter":
                if x not in df.columns or y not in df.columns:
                    continue
                if not (
                    pd.api.types.is_numeric_dtype(df[x]) and
                    pd.api.types.is_numeric_dtype(df[y])
                ):
                    continue

            # Pie / Donut
            elif chart_type in {"pie", "donut"}:
                if x not in df.columns:
                    continue

            # Table
            elif chart_type == "table":
                pass  # always valid

            else:
                continue  # unsupported chart

            # -----------------------------
            # CHART IS VALID → APPEND
            # -----------------------------
            chart = build_chart(
                df=df,
                chart_type=chart_type,
                x=x,
                y=y,
                title=title
            )

            charts.append({
                "id": f"chart_{i + 1}",
                "spec": chart
            })

        except Exception:
            continue

    return {"charts": charts}
