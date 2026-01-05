from state import DashboardState
from utils.llm_factory import generate_with_gemini
import json


INTENT_PROMPT = INTENT_PROMPT = """
You are an analytics planner AI.

You MUST produce an analysis plan.
You are NOT allowed to return empty JSON.

Rules:
- Always return at least ONE computation
- Always return at least THREE charts
- Use ONLY columns from the provided schema
- If dates are present and the question mentions relationship, lag, duration, or difference:
  compute a difference
- If numeric columns exist:
  include at least one distribution chart (pie or histogram)

Return JSON ONLY.

FORMAT:
{
  "analysis_goal": "short text",
  "computations": [
    {
      "operation": "difference | sum | count | avg | groupby | trend | correlation",
      "columns": ["col1", "col2"],
      "new_column": "optional"
    }
  ],
  "charts": [
    {
      "type": "bar | line | scatter | pie | donut | histogram | boxplot | area",
      "x": "column",
      "y": "column",
      "title": "optional"
    }
  ]
}
"""



def intent_agent(state: DashboardState) -> dict:
    schema = {
    "columns": state["schema"]["columns"],
    "dtypes": state["schema"]["types"]
}

    prompt = f"""
User question:
{state["prompt"]}

Available columns and types:
{schema}

{INTENT_PROMPT}
"""

    print(state["prompt"])

    response = generate_with_gemini(
        prompt,
        fallback_text="{}"
    )
    

    try:
        intent = json.loads(response)
        print(intent)
    except Exception:
        intent = {}

    # -------------------------
    # NORMALIZE (NO RULES)
    # -------------------------
    if not isinstance(intent, dict):
        intent = {}

    intent.setdefault("analysis_goal", "")
    intent.setdefault("computations", [])
    intent.setdefault("charts", [])

    # Ensure lists are lists
    if not isinstance(intent["computations"], list):
        intent["computations"] = []

    if not isinstance(intent["charts"], list):
        intent["charts"] = []

    print("INTENT OUTPUT:", intent)

    return {"intent": intent}

