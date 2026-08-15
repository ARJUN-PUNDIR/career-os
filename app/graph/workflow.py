from typing import Dict, Any
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    # If langgraph is not installed, StateGraph will be compiled cleanly
    StateGraph = None
    END = "__end__"

from app.graph.state import AgentState
from app.agents.parser import parse_resume_node
from app.agents.planner import plan_career_strategy_node
from app.agents.searcher import search_jobs_node
from app.agents.ranker import rank_jobs_node
from app.agents.latex_agent import generate_latex_resume_node
from app.agents.compiler import compile_latex_to_pdf_node
from app.agents.browser import fill_and_apply_job_node

def build_career_os_graph():
    """
    Builds the Master LangGraph Executable State Machine for CareerOS.
    Workflow:
    Parser -> Planner -> Searcher -> Ranker -> [Gate 1] -> LaTeX Architect -> PDF Compiler -> Browser Agent -> [Gate 2] -> END
    """
    if StateGraph is None:
        print("💡 [LangGraph Note] langgraph package not installed. Running linear state execution.")
        return None

    builder = StateGraph(AgentState)

    # 1. Register Graph Nodes
    builder.add_node("resume_parser", parse_resume_node)
    builder.add_node("career_planner", plan_career_strategy_node)
    builder.add_node("job_searcher", search_jobs_node)
    builder.add_node("ats_ranker", rank_jobs_node)
    builder.add_node("latex_architect", generate_latex_resume_node)
    builder.add_node("pdf_compiler", compile_latex_to_pdf_node)
    builder.add_node("browser_agent", fill_and_apply_job_node)

    # 2. Define State Machine Edges
    builder.set_entry_point("resume_parser")
    builder.add_edge("resume_parser", "career_planner")
    builder.add_edge("career_planner", "job_searcher")
    builder.add_edge("job_searcher", "ats_ranker")
    builder.add_edge("ats_ranker", "latex_architect")
    builder.add_edge("latex_architect", "pdf_compiler")
    builder.add_edge("pdf_compiler", "browser_agent")
    builder.add_edge("browser_agent", END)

    # 3. Compile Master Graph
    master_graph = builder.compile()
    return master_graph
