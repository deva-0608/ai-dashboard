from state import DashboardState
from utils.dataframe_utils import safe_groupby
import pandas as pd

def query_agent(state: DashboardState) -> dict:
    intent = state["intent"]
    df = state["dataframe"]

    group_by = intent.get("group_by", [])
    metric = intent.get("metric")
    agg = intent.get("aggregation", "count")

    if not group_by:
        result = pd.DataFrame({
            "value": [len(df)]
        })
    else:
        result = safe_groupby(df, group_by, metric, agg)

    return {
        "aggregated_data": {
            "table": result
        }
    }
