import os
from typing import Dict, Any
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate

from app.config.settings import settings
from app.config.model_factory import get_llm
from app.services.rapidapi_ats import call_rapidapi_ats_scorer
from app.schemas.models import CandidateProfile, UnifiedJobListing
from app.graph.state import AgentState

STRICT_SURGICAL_LATEX_PROMPT = """You are a Master LaTeX Engineer & Senior Technical Recruiter.
Your task is to take Master Jake's Resume LaTeX Code and perform SURGICAL ATS KEYWORD INFUSION ONLY for a candidate's target job.

STRICT LAWS (ZERO STRUCTURAL BREAKAGE):
1. KEEP THE EXACT LATEX PREAMBLE, PACKAGES, MARGINS, HEADINGS, AND CUSTOM COMMANDS (\\resumeSubheading, \\resumeProjectHeading, \\resumeItem) 100% UNCHANGED.
2. KEEP ALL PERSONAL FACTS 100% TRUTHFUL. Reflection-based verification prevents unsupported additions.
3. SURGICAL KEYWORD INFUSION: Seamlessly weave the MISSING HIGH-IMPACT KEYWORDS ({missing_keywords}) into the Technical Skills section and the bullet points under \\section{{Projects}}.
4. Return ONLY valid, compilable LaTeX code starting with \\documentclass and ending with \\end{{document}}.
5. DO NOT wrap the response in markdown backticks (no ```latex or ```).

EXACT MASTER LATEX BASE CODE TO SURGICALLY ENHANCE:
{master_latex_base}

MISSING KEYWORDS TO INFUSE:
{missing_keywords}

TARGET JOB DESCRIPTION:
Title: {job_title} | Company: {job_company}
{jd_text}
"""

def generate_latex_resume_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Performs surgical keyword infusion on Master Jake's Resume LaTeX base
    using dedicated ATS Scanner API report and NVIDIA Nemotron LLM.
    """
    candidate: CandidateProfile = state.get("candidate_profile")
    selected_job: UnifiedJobListing = state.get("selected_job")
    
    if not selected_job:
        ranked = state.get("ranked_jobs", [])
        selected_job = ranked[0] if ranked else None

    if not candidate or not selected_job:
        raise ValueError("Cannot run LaTeX Architect Node without Candidate Profile and Selected Job!")

    print(f"\n🎨 [LaTeX Architect Agent] Running ATS Gap Scanner & Surgical LaTeX Architect for [{selected_job.company}]...")

    # 1. Load Master Jake's Resume LaTeX Base Template
    template_path = os.path.join(settings.BASE_DIR, "app", "templates", "jake.tex")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            master_latex_base = f.read()
    else:
        master_latex_base = "\\documentclass{article}\\begin{document}Resume Base\\end{document}"

    # 2. Get Dedicated ATS Scanner API Gap Report
    resume_raw_text = f"Skills: {', '.join(candidate.skills)}. Projects: {[p.name for p in candidate.projects]}"
    ats_results = call_rapidapi_ats_scorer(resume_raw_text, selected_job.raw_jd)
    missing_kw = ", ".join(ats_results.get("missing_skills", ["LlamaIndex", "REST APIs", "Git/GitHub", "OpenAI APIs"]))

    # 3. Call NVIDIA Nemotron LLM for Surgical Keyword Infusion
    prompt = ChatPromptTemplate.from_template(STRICT_SURGICAL_LATEX_PROMPT)
    llm = get_llm(temperature=0.1)
    
    chain = prompt | llm
    response = chain.invoke({
        "master_latex_base": master_latex_base[:3500],
        "missing_keywords": missing_kw,
        "job_title": selected_job.title,
        "job_company": selected_job.company,
        "jd_text": selected_job.raw_jd[:1200]
    })

    latex_code = response.content.strip()
    
    # Strip backticks if model included them
    if latex_code.startswith("```latex"):
        latex_code = latex_code[8:]
    elif latex_code.startswith("```"):
        latex_code = latex_code[3:]
    if latex_code.endswith("```"):
        latex_code = latex_code[:-3]
    latex_code = latex_code.strip()

    # Save LaTeX code to disk
    output_dir = os.path.join(settings.BASE_DIR, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    company_slug = selected_job.company.lower().replace(" ", "_")
    tex_path = os.path.join(output_dir, f"arjun_master_jake_resume_{company_slug}.tex")
    
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"✅ [LaTeX Architect Agent] Tailored LaTeX code generated & saved to: file://{tex_path}")
    
    return {
        "latex_code": latex_code,
        "tex_path": tex_path
    }
