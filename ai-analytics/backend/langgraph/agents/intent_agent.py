from state import DashboardState
from utils.prompt_utils import intent_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
import json

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
)

def intent_agent(state: DashboardState) -> dict:
    prompt = intent_prompt(
        user_prompt=state["prompt"],
        schema=state["schema"]
    )

    response = llm.invoke(prompt).content

    try:
        intent = json.loads(response)
    except Exception:
        intent = {
            "group_by": [],
            "metric": None,
            "aggregation": "count",
            "charts": ["bar"]
        }

    return {"intent": intent}
