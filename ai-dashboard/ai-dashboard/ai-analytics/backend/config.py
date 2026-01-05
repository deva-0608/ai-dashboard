# backend/config.py

from pathlib import Path
import os
from pydantic_settings import BaseSettings


# --------------------------------------------------
# ENV / SETTINGS (Pydantic-managed)
# --------------------------------------------------
class Settings(BaseSettings):
    ai_provider: str = "openai"  # openai | groq | gemini

    openai_api_key: str | None = None
    groq_api_key: str | None = None
    gemini_api_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()


# --------------------------------------------------
# APPLICATION CONSTANTS (NOT Pydantic fields)
# --------------------------------------------------

# Project root
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Data root
DATA_ROOT: Path = BASE_DIR / "data" / "projects"

# Allowed report types
ALLOWED_REPORT_TYPES: set[str] = {
    "custom-report",
    "project-report",
    "document-report",
}

# Excel settings
EXCEL_EXTENSIONS: set[str] = {".xlsx", ".xls"}
EXCEL_ENGINE: str = "openpyxl"

# Safety limits
MAX_ROWS_PREVIEW: int = 5000
MAX_COLUMNS: int = 200

# Environment
ENV: str = os.getenv("ENV", "development")
DEBUG: bool = ENV != "production"
