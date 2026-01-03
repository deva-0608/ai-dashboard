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
    prompt: str                 # chatbot question

    # -----------------------------
    # Data
    # -----------------------------
    dataframe: pd.DataFrame     # loaded Excel data
    schema: Dict[str, Any]      # inferred schema context

    # -----------------------------
    # Agent outputs
    # -----------------------------
    intent: Dict[str, Any]      # parsed intent (planner agent)
    aggregated_data: Dict[str, Any]  # grouped / computed results

    charts: List[ChartSpec]     # multiple charts (ECharts-ready)
    kpis: List[KPI]             # KPI tiles
    summary: str                # textual insights
