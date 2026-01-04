from state import DashboardState
from utils.llm_factory import get_llm

def insight_agent(state: DashboardState) -> dict:
    llm = get_llm(temperature=0)

    prompt = f"""
Generate a short executive summary.

User question:
{state["prompt"]}

KPIs:
{state.get("kpis", [])}
"""

    summary = llm.invoke(prompt).content
    return {"summary": summary}
