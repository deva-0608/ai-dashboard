from typing import Dict, Any, List
import pandas as pd

import pandas as pd
from typing import Dict, Any


def build_line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> Dict[str, Any]:
    return {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": df[x].astype(str).tolist()},
        "yAxis": {"type": "value"},
        "series": [{
            "type": "line",
            "data": df[y].tolist(),
            "smooth": True
        }]
    }


def build_area_chart(df: pd.DataFrame, x: str, y: str, title: str) -> Dict[str, Any]:
    option = build_line_chart(df, x, y, title)
    option["series"][0]["areaStyle"] = {}
    return option


def build_donut_chart(df: pd.DataFrame, label: str, value: str, title: str) -> Dict[str, Any]:
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [{
            "type": "pie",
            "radius": ["40%", "70%"],
            "data": [
                {"name": str(r[label]), "value": r[value]}
                for _, r in df.iterrows()
            ]
        }]
    }


def build_horizontal_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> Dict[str, Any]:
    return {
        "title": {"text": title},
        "tooltip": {},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category", "data": df[x].astype(str).tolist()},
        "series": [{
            "type": "bar",
            "data": df[y].tolist()
        }]
    }


def build_scatter_chart(df: pd.DataFrame, x: str, y: str, title: str) -> Dict[str, Any]:
    return {
        "title": {"text": title},
        "tooltip": {},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "value"},
        "series": [{
            "type": "scatter",
            "data": list(zip(df[x], df[y]))
        }]
    }


def build_histogram(df: pd.DataFrame, col: str, title: str) -> Dict[str, Any]:
    bins = pd.cut(df[col], bins=10).value_counts().sort_index()
    return {
        "title": {"text": title},
        "tooltip": {},
        "xAxis": {"type": "category", "data": bins.index.astype(str).tolist()},
        "yAxis": {"type": "value"},
        "series": [{
            "type": "bar",
            "data": bins.tolist()
        }]
    }

def build_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str
) -> Dict[str, Any]:
    return {
        "title": {"text": title},
        "tooltip": {},
        "xAxis": {
            "type": "category",
            "data": df[x].astype(str).tolist()
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "type": "bar",
                "data": df[y].tolist()
            }
        ]
    }


def build_pie_chart(
    df: pd.DataFrame,
    label: str,
    value: str,
    title: str
) -> Dict[str, Any]:
    return {
        "title": {"text": title},
        "tooltip": {},
        "series": [
            {
                "type": "pie",
                "data": [
                    {"name": str(r[label]), "value": r[value]}
                    for _, r in df.iterrows()
                ]
            }
        ]
    }
