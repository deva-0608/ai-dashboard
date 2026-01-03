from state import DashboardState
from utils.prompt_utils import insight_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
)

def insight_agent(state: DashboardState) -> dict:
    prompt = insight_prompt(
        user_prompt=state["prompt"],
        summary={
            "intent": state["intent"],
            "kpis": state["kpis"]
        }
    )

    summary = llm.invoke(prompt).content
    return {"summary": summary}
