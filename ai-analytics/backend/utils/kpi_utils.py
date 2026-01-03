import pandas as pd
from typing import List, Dict


def generate_basic_kpis(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generate generic KPIs valid for any Excel
    """
    kpis = [
        {"name": "Total Rows", "value": str(len(df))},
        {"name": "Total Columns", "value": str(len(df.columns))}
    ]

    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols[:3]:  # limit noise
        kpis.append({
            "name": f"Sum of {col}",
            "value": str(round(df[col].sum(), 2))
        })

    return kpis
