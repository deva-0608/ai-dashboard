import pandas as pd
from pathlib import Path
from fastapi import HTTPException
from typing import Dict, Any, Tuple

from config import settings


# -------------------------------------------------
# Validation
# -------------------------------------------------
def validate_report_type(report_type: str):
    if report_type not in settings.ALLOWED_REPORT_TYPES:
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

    report_dir = settings.DATA_ROOT / report_type / str(report_id)

    if not report_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Report folder not found: {report_id}"
        )

    excel_files = [
        f for f in report_dir.iterdir()
        if f.is_file() and f.suffix.lower() in settings.EXCEL_EXTENSIONS
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
def load_excel_dataframe(report_type: str, report_id: str) -> Tuple[pd.DataFrame, str]:
    """
    Loads Excel and returns:
    - DataFrame
    - project_name (derived from filename)
    """
    excel_path = find_excel_file(report_type, report_id)

    try:
        df = pd.read_excel(
            excel_path,
            engine=settings.EXCEL_ENGINE
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read Excel: {str(e)}"
        )

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="Excel file is empty"
        )

    # Safety checks
    if len(df.columns) > settings.MAX_COLUMNS:
        raise HTTPException(
            status_code=400,
            detail="Too many columns in Excel"
        )

    if len(df) > settings.MAX_ROWS_PREVIEW:
        df = df.head(settings.MAX_ROWS_PREVIEW)

    project_name = excel_path.stem  # filename without .xlsx

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
