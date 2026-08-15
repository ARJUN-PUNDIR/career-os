import os
from typing import Dict, Any
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from app.config.model_factory import get_llm
from app.mcp.ats_scanner import generate_jobscan_report
from app.schemas.models import CandidateProfile, UnifiedJobListing
from app.graph.state import AgentState

LATEX_ARCHITECT_PROMPT = """You are a World-Class LaTeX Resume Architect & Senior Technical Recruiter.
Your task is to generate complete, compilation-ready LaTeX code for a candidate's resume tailored to a specific target job.

INPUT 1: ORIGINAL CANDIDATE RESUME
Name: {candidate_name}
Email: {candidate_email} | Phone: {candidate_phone} | Location: {candidate_location}
Skills: {candidate_skills}
Projects: {candidate_projects}
Experiences: {candidate_experiences}
Education: {candidate_education}

INPUT 2: TARGET JOB DESCRIPTION
Title: {job_title}
Company: {job_company}
Location: {job_location}
JD Snippet: {jd_text}

INPUT 3: JOBSCAN ATS SCANNER MCP REPORT
{jobscan_report}

STRICT LATEX GENERATION RULES:
1. Return ONLY pure, clean, compilable LaTeX code starting with \\documentclass and ending with \\end{{document}}.
2. DO NOT wrap the response in markdown backticks (no ```latex or ```).
3. FACT PRESERVATION: Do NOT invent fake companies, dates, or degrees. Keep all original facts 100% truthful.
4. KEYWORD INFUSION: Seamlessly incorporate the MISSING HIGH-IMPACT KEYWORDS from the Jobscan MCP report into the candidate's existing project bullet points.
5. FORMATTING: Use clean, single-page LaTeX packages (e.g. geometry, hyperref, enumitem, titlesec). Escape special characters like %, &, $, _, # as \\%, \\&, \\$, \\_, \\#.
"""

def generate_latex_resume_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Takes Jobscan MCP Report + Original Resume + Selected JD,
    and calls NVIDIA Nemotron LLM to generate clean, tailored LaTeX code.
    """
    candidate: CandidateProfile = state.get("candidate_profile")
    selected_job: UnifiedJobListing = state.get("selected_job")
    
    if not selected_job:
        ranked = state.get("ranked_jobs", [])
        selected_job = ranked[0] if ranked else None

    if not candidate or not selected_job:
        raise ValueError("Cannot run LaTeX Architect Node without Candidate Profile and Selected Job!")

    print(f"\n🎨 [LaTeX Architect Agent] Running Jobscan MCP Scan & Generating Tailored LaTeX for [{selected_job.company}]...")

    # 1. Run ATS Scanner MCP Tool
    resume_raw_text = f"Skills: {', '.join(candidate.skills)}. Projects: {[p.name for p in candidate.projects]}"
    jobscan_report = generate_jobscan_report(resume_raw_text, selected_job.raw_jd)
    print(f"📊 [Jobscan MCP Report Generated]: Match Score {jobscan_report.splitlines()[2]}")

    # 2. Invoke NVIDIA Nemotron LLM to generate LaTeX code
    prompt = ChatPromptTemplate.from_template(LATEX_ARCHITECT_PROMPT)
    llm = get_llm(temperature=0.2)
    
    chain = prompt | llm
    response = chain.invoke({
        "candidate_name": candidate.full_name,
        "candidate_email": candidate.email,
        "candidate_phone": candidate.phone,
        "candidate_location": candidate.location,
        "candidate_skills": ", ".join(candidate.skills),
        "candidate_projects": str([{"name": p.name, "tech": p.technologies, "bullets": p.bullet_points} for p in candidate.projects]),
        "candidate_experiences": str([{"company": e.company, "role": e.role, "duration": e.duration} for e in candidate.experiences]),
        "candidate_education": str([{"degree": ed.degree, "institution": ed.institution} for ed in candidate.education]),
        "job_title": selected_job.title,
        "job_company": selected_job.company,
        "job_location": selected_job.location,
        "jd_text": selected_job.raw_jd[:1500],
        "jobscan_report": jobscan_report
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
    from app.config.settings import settings
    output_dir = os.path.join(settings.BASE_DIR, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, f"arjun_resume_{selected_job.company.lower().replace(' ', '_')}.tex")
    
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"✅ [LaTeX Architect Agent] Tailored LaTeX code generated & saved to: file://{tex_path}")
    
    return {
        "latex_code": latex_code,
        "tex_path": tex_path
    }
