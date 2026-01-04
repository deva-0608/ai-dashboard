from state import DashboardState
from utils.prompt_utils import intent_prompt
from utils.llm_factory import get_llm
import json

def intent_agent(state: DashboardState) -> dict:
    llm = get_llm(temperature=0)

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
