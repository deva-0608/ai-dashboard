import pandas as pd
from typing import Dict, Any
from utils.dataframe_utils import infer_column_types


def build_schema_context(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Build schema context sent to LangGraph agents
    """
    return {
        "columns": df.columns.tolist(),
        "types": infer_column_types(df),
        "row_count": len(df)
    }
