from state import DashboardState
from utils.charts_utils import (
    build_bar_chart,
    build_horizontal_bar_chart,
    build_pie_chart,
    build_donut_chart,
    build_line_chart,
    build_area_chart,
    build_scatter_chart,
    build_histogram
)

import pandas as pd


def viz_agent(state: DashboardState) -> dict:
    intent = state["intent"]
    df: pd.DataFrame = state["aggregated_data"]["table"]

    charts = []
    chart_id = 1

    # Safe axis detection
    x = intent.get("group_by", [df.columns[0]])[0]
    y = df.columns[-1]

    requested_charts = intent.get(
        "charts",
        ["bar"]  # default
    )

    for chart_type in requested_charts:
        try:
            if chart_type == "bar":
                option = build_bar_chart(df, x, y, f"{y} by {x}")

            elif chart_type == "horizontal_bar":
                option = build_horizontal_bar_chart(df, x, y, f"{y} by {x}")

            elif chart_type == "line":
                option = build_line_chart(df, x, y, f"{y} trend")

            elif chart_type == "area":
                option = build_area_chart(df, x, y, f"{y} trend")

            elif chart_type == "pie":
                option = build_pie_chart(df, x, y, f"{y} distribution")

            elif chart_type == "donut":
                option = build_donut_chart(df, x, y, f"{y} distribution")

            elif chart_type == "scatter" and len(df.columns) >= 2:
                option = build_scatter_chart(df, df.columns[0], df.columns[1], "Scatter")

            elif chart_type == "histogram":
                option = build_histogram(df, y, f"{y} distribution")

            else:
                continue

            charts.append({
                "id": f"chart_{chart_id}",
                "option": option
            })
            chart_id += 1

        except Exception:
            # Skip unsafe chart instead of breaking dashboard
            continue

    return {"charts": charts}
