from state import DashboardState
from utils.kpi_utils import generate_basic_kpis

def kpi_agent(state: DashboardState) -> dict:
    kpis = generate_basic_kpis(state["dataframe"])
    return {"kpis": kpis}
