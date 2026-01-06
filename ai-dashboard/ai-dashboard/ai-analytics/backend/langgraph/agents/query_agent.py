from state import DashboardState
from utils.llm_factory import generate_with_gemini
import pandas as pd
import json


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def sanitize_column_name(name: str) -> str:
    """Convert unsafe column names to python-safe ones"""
    return (
        name.strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("__", "_")
    )


# --------------------------------------------------
# Prompt for pandas code
# --------------------------------------------------
PANDAS_TRANSFORM_PROMPT = """
You are a pandas expert.

You are given:
- A pandas DataFrame named `df`
- A user analytics question

Rules:
- ALWAYS start with: df_new = df.copy()
- NEVER modify df in-place
- ALWAYS assign result to df_new
- ALWAYS use pd.to_datetime(..., errors="coerce") for date math
- Use ONLY pandas
- Do NOT import anything
- Do NOT explain anything
- Do NOT print anything

Return ONLY valid Python code.

User request:
{user_prompt}

Available columns:
{columns}
"""


# --------------------------------------------------
# Safe executor
# --------------------------------------------------
def execute_pandas_transform(df: pd.DataFrame, code: str) -> pd.DataFrame:
    if not code or not isinstance(code, str):
        return df

    local_vars = {
        "df": df.copy(),
        "pd": pd
    }

    try:
        exec(code, {"__builtins__": {}}, local_vars)
        df_new = local_vars.get("df_new")

        if isinstance(df_new, pd.DataFrame):
            return df_new

        print("⚠️ LLM did not return df_new")
        return df

    except Exception as e:
        print("⚠️ Pandas transform execution failed:", e)
        return df


# --------------------------------------------------
# Query Agent
# --------------------------------------------------
def query_agent(state: DashboardState) -> dict:
    df: pd.DataFrame = state.get("dataframe")

    if df is None or df.empty:
        return {"aggregated_data": {"table": df}}

    user_prompt = state.get("prompt", "")
    intent = state.get("intent", {})

    # -----------------------------
    # Ask LLM for pandas code
    # -----------------------------
    prompt = PANDAS_TRANSFORM_PROMPT.format(
        user_prompt=user_prompt,
        columns=list(df.columns)
    )

    pandas_code = generate_with_gemini(prompt, fallback_text="")
    df_new = execute_pandas_transform(df, pandas_code)

    # -----------------------------
    # SAFETY: enforce intent computations
    # -----------------------------
    computations = intent.get("computations", [])

    for comp in computations:
        if comp.get("operation") == "difference":
            cols = comp.get("columns", [])
            raw_new_col = comp.get("new_column")

            if not raw_new_col or len(cols) != 2:
                continue

            safe_col = sanitize_column_name(raw_new_col)
            comp["new_column"] = safe_col  # 🔑 keep intent + df aligned

            if (
                safe_col not in df_new.columns
                and all(c in df_new.columns for c in cols)
            ):
                df_new[safe_col] = (
                    pd.to_datetime(df_new[cols[1]], errors="coerce") -
                    pd.to_datetime(df_new[cols[0]], errors="coerce")
                ).dt.days

    print("✅ FINAL DF COLUMNS:", df_new.columns.tolist())

    return {
        "aggregated_data": {
            "table": df_new
        }
    }
