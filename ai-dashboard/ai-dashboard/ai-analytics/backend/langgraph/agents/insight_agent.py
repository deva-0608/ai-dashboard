# backend/langgraph/agents/insight_agent.py

from state import DashboardState
from utils.llm_factory import generate_with_gemini


def insight_agent(state: DashboardState) -> dict:
    """
    Generates a human-readable insight / executive summary
    based on KPIs and the user prompt.
    """

    prompt = f"""
You are an analytics assistant.

User question:
{state["prompt"]}

Computed KPIs:
{state.get("kpis", [])}

Write a short, clear executive summary in plain English.
Avoid technical jargon.
"""

    summary = generate_with_gemini(
        prompt,
        fallback_text="No AI insights available for this report."
    )

    return {
        "summary": summary
    }