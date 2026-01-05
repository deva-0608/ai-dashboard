# backend/utils/chart_utils.py
from typing import Dict, Any


def build_chart(
    df,                 # kept for interface consistency (unused)
    chart_type: str,
    x: str = None,
    y: str = None,
    title: str = None
) -> Dict[str, Any]:
    """
    Return chart SPEC only.
    Frontend will use dataframe to plot.
    """
    return {
        "type": chart_type,
        "x": x,
        "y": y,
        "title": title or ""
    }
