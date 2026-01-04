from state import DashboardState
from utils.schema_utils import build_schema_context

def schema_agent(state: DashboardState) -> dict:
    df = state["dataframe"]

    if not hasattr(df, "columns"):
        raise ValueError(
            "state['dataframe'] must be a pandas DataFrame"
        )

    schema = build_schema_context(df)
    return {"schema": schema}
