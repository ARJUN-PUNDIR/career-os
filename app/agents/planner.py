from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.config.model_factory import get_llm
from app.schemas.models import CandidateProfile, JobRequirementsInput
from app.graph.state import AgentState

class SearchStrategyOutput(BaseModel):
    clean_role: str = Field(description="Normalized target role title, e.g., 'AI Intern'")
    clean_locations: List[str] = Field(description="Normalized locations list, e.g., ['Gurugram', 'Noida', 'Delhi', 'Remote']")
    pillar_1_queries: List[str] = Field(description="SIMPLE 2-3 word search strings for JSearch (Pillar 1). Must be simple keywords like 'AI Intern Gurugram', 'GenAI Intern Remote' so search engines find high volume results.")
    pillar_2_queries: List[str] = Field(description="Clean Google ATS queries for Pillar 2 without slashes or complex quotes, e.g., site:boards.greenhouse.io 'AI Intern'")
    include_keywords: List[str] = Field(description="Must-have technical skill keywords used by ATS Ranker Node (e.g., LangGraph, RAG, Python)")
    exclude_keywords: List[str] = Field(description="Negative filter keywords used by ATS Ranker Node (e.g., Senior, Lead, Manager, Sales)")
    rationale: str = Field(description="Short rationale explaining the broad-search, strict-ranking strategy.")

def plan_career_strategy_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Generates simple, high-yield search queries (2-3 words max per query)
    to maximize search engine hit rates, while leaving deep keyword filtering to the ATS Ranker node.
    """
    candidate: CandidateProfile = state.get("candidate_profile")
    requirements: JobRequirementsInput = state.get("user_requirements")
    
    if not requirements:
        requirements = JobRequirementsInput(
            target_role="AI Intern",
            target_locations=["Gurugram", "Noida", "Remote"],
            min_stipend_lpa="10k - 25k/month",
            days_posted=10
        )
        
    print(f"🎯 [Planner Agent] Generating simple high-yield search queries...")
    
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(SearchStrategyOutput)
    
    prompt = f"""
    You are an expert AI Career Planner. Generate SIMPLE, HIGH-YIELD job search queries.

    RAW USER PREFERENCES:
    - Target Role: "{requirements.target_role}"
    - Locations: "{', '.join(requirements.target_locations)}"

    CRITICAL RULES FOR HIGH SEARCH YIELD (PREVENT 0 RESULTS):
    1. KEEP PILLAR 1 QUERIES VERY SIMPLE (MAX 3 WORDS PER QUERY): Never combine 5 tech stack keywords in one query! Search engines require exact matches for every word. Use simple 2-3 word phrases.
       GOOD Pillar 1 Examples:
       - "AI Intern Gurugram"
       - "GenAI Intern Remote"
       - "Python AI Intern Noida"
       - "Machine Learning Intern Delhi"
       
    2. KEEP PILLAR 2 QUERIES CLEAN (NO SLASHES OR COMPLEX QUOTES):
       GOOD Pillar 2 Examples:
       - "site:boards.greenhouse.io 'AI Intern'"
       - "site:jobs.lever.co 'AI Intern'"
       - "site:boards.greenhouse.io 'GenAI Intern'"
       
    3. Include technical skills (LangGraph, RAG, FAISS, PyTorch) in include_keywords. The ATS Ranking Agent will use these to rank the jobs AFTER they are fetched!
    """
    
    strategy: SearchStrategyOutput = structured_llm.invoke(prompt)
    print(f"✅ [Planner Agent] Generated {len(strategy.pillar_1_queries)} high-yield JSearch queries & {len(strategy.pillar_2_queries)} clean ATS queries!")
    
    strategy_dict = strategy.model_dump()
    strategy_dict["search_queries"] = strategy.pillar_1_queries
    
    clean_reqs = JobRequirementsInput(
        target_role=strategy.clean_role,
        target_locations=strategy.clean_locations,
        min_stipend_lpa=requirements.min_stipend_lpa,
        days_posted=10
    )
    
    return {
        "user_requirements": clean_reqs,
        "search_strategy": strategy_dict
    }
