from langgraph.graph import StateGraph
from state import DashboardState
from langgraph.agents.schema_agent import schema_agent
from langgraph.agents.intent_agent import intent_agent
from langgraph.agents.query_agent import query_agent
from langgraph.agents.viz_agent import viz_agent
from langgraph.agents.kpi_agent import kpi_agent
from langgraph.agents.insight_agent import insight_agent

from dotenv import load_dotenv
load_dotenv()
def run_langgraph(initial_state: DashboardState):
    graph = StateGraph(DashboardState)

    graph.add_node("schema", schema_agent)
    graph.add_node("intent", intent_agent)
    graph.add_node("query", query_agent)
    graph.add_node("viz", viz_agent)
    graph.add_node("kpi", kpi_agent)
    graph.add_node("insight", insight_agent)

    graph.set_entry_point("schema")
    graph.add_edge("schema", "intent")
    graph.add_edge("intent", "query")
    graph.add_edge("query", "viz")
    graph.add_edge("viz", "kpi")
    graph.add_edge("kpi", "insight")

    compiled = graph.compile()
    final_state = compiled.invoke(initial_state)
    dict={
        "summary": final_state["summary"],
        "kpis": final_state["kpis"],
        "charts": final_state["charts"]
    }
    print(dict)

    return {
        "summary": final_state["summary"],
        "kpis": final_state["kpis"],
        "charts": final_state["charts"]
    }
