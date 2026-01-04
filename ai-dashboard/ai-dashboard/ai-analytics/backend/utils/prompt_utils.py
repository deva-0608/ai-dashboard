def intent_prompt(user_prompt: str, schema: dict) -> str:
    return f"""
You are an analytics planner.

User question:
{user_prompt}

Available columns:
{schema['columns']}

Column types:
{schema['types']}

Return JSON ONLY:
{{
  "group_by": ["column"],
  "metric": "column",
  "aggregation": "count | sum | avg",
  "charts": ["bar", "pie"]
}}
"""


def insight_prompt(user_prompt: str, summary: dict) -> str:
    return f"""
Generate concise insights.

User question:
{user_prompt}

Computed data:
{summary}
"""
