import pandas as pd
from pathlib import Path
from fastapi import HTTPException
from typing import Dict, Any

# ✅ IMPORT CONSTANTS (NOT settings)
from config import DATA_ROOT, ALLOWED_REPORT_TYPES, EXCEL_EXTENSIONS


# -------------------------------------------------
# Validation
# -------------------------------------------------
def validate_report_type(report_type: str):
    if report_type not in ALLOWED_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type: {report_type}"
        )


# -------------------------------------------------
# Find Excel file dynamically
# -------------------------------------------------
def find_excel_file(report_type: str, report_id: str) -> Path:
    """
    Finds the single Excel file inside a report folder.
    Filename represents the project name.
    """
    validate_report_type(report_type)

    report_dir = DATA_ROOT / report_type / str(report_id)

    if not report_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Report folder not found: {report_id}"
        )

    excel_files = [
        f for f in report_dir.iterdir()
        if f.is_file() and f.suffix.lower() in EXCEL_EXTENSIONS
    ]

    if len(excel_files) == 0:
        raise HTTPException(
            status_code=404,
            detail="No Excel file found in report folder"
        )

    if len(excel_files) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple Excel files found. Only one is allowed per report."
        )

    return excel_files[0]


# -------------------------------------------------
# Load Excel into DataFrame
# -------------------------------------------------
def load_excel_dataframe(report_type: str, report_id: str):
    excel_path = find_excel_file(report_type, report_id)
    df = pd.read_excel(excel_path)
    project_name = excel_path.stem
    return df, project_name


# -------------------------------------------------
# Convert DataFrame → API response
# -------------------------------------------------
def dataframe_to_response(df: pd.DataFrame, project_name: str) -> Dict[str, Any]:
    """
    Converts DataFrame to frontend-safe JSON
    """
    return {
        "project_name": project_name,
        "columns": [str(c) for c in df.columns],
        "rows": df.fillna("").to_dict(orient="records"),
        "row_count": len(df)
    }
