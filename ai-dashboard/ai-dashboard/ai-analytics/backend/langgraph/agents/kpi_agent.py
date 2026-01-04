from state import DashboardState
import pandas as pd

def kpi_agent(state: DashboardState) -> dict:
    df: pd.DataFrame = state["dataframe"]

    kpis = []

    for col in df.select_dtypes(include="number").columns:
        kpis.append({
            "name": f"Total {col}",
            "value": float(df[col].sum())
        })

    return {"kpis": kpis}
