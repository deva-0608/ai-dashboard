from typing import TypedDict, List, Dict, Any
import pandas as pd


class ChartSpec(TypedDict):
    """
    Frontend-ready chart specification
    (ECharts option object)
    """
    id: str
    option: Dict[str, Any]


class KPI(TypedDict):
    """
    KPI tile definition
    """
    name: str
    value: str


class DashboardState(TypedDict):
    """
    Shared LangGraph state across all agents
    """

    # -----------------------------
    # Context (from FastAPI)
    # -----------------------------
    report_type: str            # custom-report | project-report | document-report
    report_id: int              # folder name
    project_name: str           # derived from Excel filename

    # -----------------------------
    # User input
    # -----------------------------
    dataframe: pd.DataFrame
    aggregated_data: dict
    intent: dict
    schema: dict
    charts: list
    kpis: list
    summary: str
    prompt: str       # textual insights
