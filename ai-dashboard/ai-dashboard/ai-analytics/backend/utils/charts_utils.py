from typing import Dict, Any
import pandas as pd
import numpy as np


def build_chart(
    df: pd.DataFrame,
    chart_type: str,
    x: str,
    y: str | None = None,
    title: str | None = None
) -> Dict[str, Any]:
    """
    Universal ECharts option builder.

    Rules:
    - If y is None → COUNT plot
    - Histogram & boxplot require numeric x
    - Scatter requires numeric x & y
    """

    option: Dict[str, Any] = {
        "title": {"text": title or ""},
        "tooltip": {}
    }

    # =================================================
    # COUNT-BASED CHARTS (y == None)
    # =================================================
    if y is None:
        counts = df[x].value_counts(dropna=True).reset_index()
        counts.columns = [x, "count"]

        # -------- BAR COUNT --------
        if chart_type == "bar":
            option.update({
                "xAxis": {"type": "category", "data": counts[x].astype(str).tolist()},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "bar",
                    "data": counts["count"].tolist()
                }]
            })
            return option

        # -------- PIE / DONUT COUNT --------
        if chart_type in {"pie", "donut"}:
            option.update({
                "series": [{
                    "type": "pie",
                    "radius": "70%" if chart_type == "pie" else ["40%", "70%"],
                    "data": [
                        {"name": str(r[x]), "value": int(r["count"])}
                        for _, r in counts.iterrows()
                    ]
                }]
            })
            return option

    # =================================================
    # HISTOGRAM (numeric only)
    # =================================================
    if chart_type == "histogram":
        numeric = pd.to_numeric(df[x], errors="coerce").dropna()
        if numeric.empty:
            return None

        bins = pd.cut(numeric, bins=10).value_counts().sort_index()

        option.update({
            "xAxis": {
                "type": "category",
                "data": [str(b) for b in bins.index]
            },
            "yAxis": {"type": "value"},
            "series": [{
                "type": "bar",
                "data": bins.tolist()
            }]
        })
        return option

    # =================================================
    # BOXPLOT (numeric only)
    # =================================================
    if chart_type == "boxplot":
        numeric = pd.to_numeric(df[x], errors="coerce").dropna()
        if numeric.empty:
            return None

        stats = [
            numeric.min(),
            numeric.quantile(0.25),
            numeric.median(),
            numeric.quantile(0.75),
            numeric.max()
        ]

        option.update({
            "xAxis": {"type": "category", "data": [x]},
            "yAxis": {"type": "value"},
            "series": [{
                "type": "boxplot",
                "data": [stats]
            }]
        })
        return option

    # =================================================
    # SCATTER (numeric–numeric)
    # =================================================
    if chart_type == "scatter":
        x_vals = pd.to_numeric(df[x], errors="coerce")
        y_vals = pd.to_numeric(df[y], errors="coerce")

        mask = x_vals.notna() & y_vals.notna()
        points = list(zip(x_vals[mask], y_vals[mask]))

        if not points:
            return None

        option.update({
            "xAxis": {"type": "value"},
            "yAxis": {"type": "value"},
            "series": [{
                "type": "scatter",
                "data": points
            }]
        })
        return option

    # =================================================
    # NORMAL X–Y CHARTS
    # =================================================
    if chart_type == "bar":
        option.update({
            "xAxis": {"type": "category", "data": df[x].astype(str).tolist()},
            "yAxis": {"type": "value"},
            "series": [{
                "type": "bar",
                "data": df[y].tolist()
            }]
        })
        return option

    if chart_type == "line":
        option.update({
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": df[x].astype(str).tolist()},
            "yAxis": {"type": "value"},
            "series": [{
                "type": "line",
                "data": df[y].tolist(),
                "smooth": True
            }]
        })
        return option

    if chart_type == "area":
        option.update({
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": df[x].astype(str).tolist()},
            "yAxis": {"type": "value"},
            "series": [{
                "type": "line",
                "data": df[y].tolist(),
                "smooth": True,
                "areaStyle": {}
            }]
        })
        return option

    # =================================================
    # Unsupported chart
    # =================================================
    return None
