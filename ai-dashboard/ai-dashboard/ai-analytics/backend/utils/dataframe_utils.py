import pandas as pd
from typing import Dict, List


def infer_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infer semantic column types for LLM grounding
    """
    types = {}

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            types[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            types[col] = "datetime"
        else:
            types[col] = "categorical"

    return types


def safe_groupby(
    df: pd.DataFrame,
    group_by: List[str],
    metric: str,
    agg: str = "count"
) -> pd.DataFrame:
    """
    Safe groupby with validation
    """
    for col in group_by + [metric]:
        if col not in df.columns:
            raise ValueError(f"Column not found: {col}")

    if agg == "count":
        return df.groupby(group_by).size().reset_index(name="count")

    return (
        df.groupby(group_by)[metric]
        .agg(agg)
        .reset_index()
    )
