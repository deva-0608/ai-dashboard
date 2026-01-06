from state import DashboardState
from utils.llm_factory import generate_with_gemini
import json


INTENT_PROMPT = """
You are an analytics planner AI.

Your job is to analyze the user's question and the dataset schema,
then produce a COMPLETE analysis and visualization plan.

You MUST think like a BI analyst.

--------------------------------
GENERAL RULES (MANDATORY)
--------------------------------Ss
- You MUST return a valid JSON object
- You MUST NOT return empty JSON
- You MUST include:
  - at least ONE computation
  - Maximum   FOUR CHARTS   related to user prompt AND  OTHER POSSIBLE  CHARTS from the columns
  -INCLUDE ATLEAST ONE PIE CHART
- You MUST use ONLY columns present in the provided schema
- NEVER invent column names
- Prefer meaningful, interpretable charts over random ones
IMPORTANT:
- NEVER invent new column names like *_Count or *_Total
- For categorical distributions, use y = "count"
- Histograms are ONLY for numeric columns

--------------------------------
COLUMN TYPE AWARENESS
--------------------------------
- CATEGORICAL columns:
  - strings
  - low-cardinality enums
- NUMERIC columns:
  - integers
  - floats
- DATE / TIME columns:
  - dates, timestamps, durations

--------------------------------
HOW TO THINK ABOUT THE QUESTION
--------------------------------
1. If the question compares categories (e.g. by type, class, gender, status):
   - Use COUNT-based analysis
   - Prefer bar / stacked bar / pie

2. If the question asks for distribution:
   - Use histogram or boxplot
   - Only needs ONE column

3. If the question asks for relationship or comparison between two numeric columns:
   - Use scatter or correlation
   - Optionally include trend

4. If the question mentions:
   - difference
   - lag
   - duration
   - delay
   - gap
   - time between
   AND date/time columns exist:
   - Compute a DIFFERENCE
   - Create a new derived column

5. If numeric metrics are grouped by categories:
   - Use group-based aggregation (avg, sum, count)
   - Visualize using bar or line charts

--------------------------------
COMPUTATION RULES
--------------------------------
Each computation MUST describe:
- what operation to perform
- which columns are involved
- what new column (if any) is created

Allowed operations:
- count
- sum
- avg
- difference
- groupby
- trend
- correlation

--------------------------------
CHART RULES
--------------------------------
- Charts MUST align with computations
- If y is "count", the chart represents frequency
- If both x and y are categorical → count distribution
- If x is categorical and y is numeric → aggregated comparison
- If only x is provided → distribution chart
- Prefer MULTIPLE complementary charts

--------------------------------
RETURN FORMAT (STRICT)
--------------------------------
Return JSON ONLY in this format:

{
  "analysis_goal": "short clear description",
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
      "y": "column | count | null",
      "title": "short title"
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

