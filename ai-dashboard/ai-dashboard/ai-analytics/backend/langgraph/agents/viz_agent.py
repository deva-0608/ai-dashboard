from state import DashboardState
from utils.charts_utils import (
    build_bar_chart,
    build_pie_chart,
    build_line_chart,
    build_donut_chart
)

def viz_agent(state: DashboardState) -> dict:
    intent = state["intent"]
    table = state["aggregated_data"]["table"]

    charts = []
    x = intent["group_by"][0] if intent.get("group_by") else table.columns[0]
    y = table.columns[-1]

    for i, chart_type in enumerate(intent.get("charts", ["bar"])):
        if chart_type == "bar":
            option = build_bar_chart(table, x, y)
        elif chart_type == "pie":
            option = build_pie_chart(table, x, y)
        elif chart_type == "line":
            option = build_line_chart(table, x, y)
        elif chart_type == "donut":
            option = build_donut_chart(table, x, y)
        else:
            continue

        charts.append({
            "id": f"chart_{i+1}",
            "option": option
        })

    return {"charts": charts}
