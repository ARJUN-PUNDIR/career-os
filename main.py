import sys
import os
import json
import pdfplumber
import subprocess
from datetime import datetime
from app.config.settings import settings
from app.agents.parser import parse_resume_node
from app.agents.planner import plan_career_strategy_node
from app.agents.searcher import search_jobs_node
from app.agents.ranker import rank_jobs_node
from app.services.rapidapi_ats import call_rapidapi_ats_scorer
from app.agents.latex_agent import generate_latex_resume_node
from app.agents.compiler import compile_latex_to_pdf_node
from app.agents.browser import fill_and_apply_job_node
from app.graph.workflow import build_career_os_graph
from app.schemas.models import JobRequirementsInput, UnifiedJobListing
from app.graph.state import AgentState

class LoggerTee:
    """Tee logger that prints to console AND records entire raw text conversation log."""
    def __init__(self, file_path):
        self.terminal = sys.stdout
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.log = open(file_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def extract_full_raw_pdf_text(pdf_path: str) -> str:
    """Extracts 100% un-truncated raw full text from PDF resume file."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    return full_text.strip()

def run_master_career_os_pipeline():
    log_file = os.path.join(settings.BASE_DIR, "data", "full_pipeline_run.log")
    sys.stdout = LoggerTee(log_file)

    pdf_path = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
    if not os.path.exists(pdf_path):
        print(f"\n❌ Error: Resume PDF not found at path:")
        print(f"   {pdf_path}")
        print(f"\n💡 Please copy your resume PDF file to this location:")
        print(f"   /Users/arjunsinghpundir/Desktop/career-os/data/uploads/arjun_resume.pdf\n")
        return

    print("\n" + "="*85)
    print("🚀 CAREEROS: AUTONOMOUS MULTI-AGENT ATS RESUME & JOB APPLICATION PLATFORM")
    print("="*85)
    
    # -----------------------------------------------------------------
    # STEP 0: TARGET JOB PREFERENCES PROMPT
    # -----------------------------------------------------------------
    print("\n📝 STEP 0: ENTER YOUR TARGET JOB PREFERENCES")
    print("-" * 75)
    
    user_role = input("👉 Enter Target Role [default: AI Intern / GenAI Engineer]: ").strip()
    if not user_role:
        user_role = "AI Intern / GenAI Engineer"
        
    user_location = input("👉 Enter Target Location [default: Remote, Gurugram, Noida, Delhi]: ").strip()
    if not user_location:
        user_location = "Remote, Gurugram, Noida, Delhi"
    locations_list = [loc.strip() for loc in user_location.split(",")]
    
    user_stipend = input("👉 Enter Target Salary/Stipend [default: 10k - 25k/month]: ").strip()
    if not user_stipend:
        user_stipend = "10k - 25k/month"
        
    user_requirements = JobRequirementsInput(
        target_role=user_role,
        target_locations=locations_list,
        min_stipend_lpa=user_stipend,
        days_posted=10
    )

    state: AgentState = {
        "resume_pdf_path": pdf_path,
        "candidate_profile": None,
        "user_requirements": user_requirements,
        "search_strategy": None,
        "discovered_jobs": [],
        "ranked_jobs": [],
        "selected_job": None,
        "tailored_profile": None,
        "audit_result": None,
        "compiled_pdf_path": None,
        "cover_letter_text": None,
        "gate_1_approved": False,
        "gate_2_approved": False,
        "application_status": "DISCOVERED",
        "tracker_logs": [],
        "error_message": None
    }

    # -----------------------------------------------------------------
    # STEP 1: RESUME PARSER AGENT (MD5 CACHED: $0 TOKENS IF UNCHANGED)
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("📄 STEP 1: RESUME PARSER AGENT (SMART MD5 CACHED)")
    print("="*85)
    parser_res = parse_resume_node(state)
    state["candidate_profile"] = parser_res["candidate_profile"]

    # -----------------------------------------------------------------
    # STEP 2: CAREER STRATEGY PLANNER AGENT (NVIDIA NEMOTRON LLM)
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("🎯 STEP 2: CAREER STRATEGY PLANNER AGENT (NVIDIA NEMOTRON LLM)")
    print("="*85)
    planner_res = plan_career_strategy_node(state)
    state["search_strategy"] = planner_res["search_strategy"]
    state["user_requirements"] = planner_res["user_requirements"]

    print("\n📋 STRATEGY SUMMARY:")
    print(f"   Pillar 1 Queries (JSearch API):   {state['search_strategy'].get('pillar_1_queries')}")
    print(f"   Pillar 2 Queries (Google ATS):    {state['search_strategy'].get('pillar_2_queries')}")
    
    # -----------------------------------------------------------------
    # STEP 3: 3-PILLAR SEARCH ENGINE EXECUTION
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("🌐 STEP 3: 3-PILLAR MULTI-AGENT JOB SEARCH ENGINES")
    print("="*85)
    search_res = search_jobs_node(state)
    state["discovered_jobs"] = search_res["discovered_jobs"]

    # -----------------------------------------------------------------
    # STEP 4: ATS MULTI-FACTOR RANKING ENGINE (0 TOKENS, <10ms)
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("📊 STEP 4: ATS RANKER ENGINE (HARD DISQUALIFICATION RULES)")
    print("="*85)
    ranker_res = rank_jobs_node(state)
    state["ranked_jobs"] = ranker_res["ranked_jobs"]
    qualified_list = [j for j in state["ranked_jobs"] if j.ats_score > 0.0]

    if not qualified_list:
        print("⚠️ No qualified jobs found matching your criteria!")
        return

    # -----------------------------------------------------------------
    # STEP 5: HUMAN APPROVAL GATE 1 INTERRUPT (SELECT TARGET JOB)
    # -----------------------------------------------------------------
    print("\n" + "#"*85)
    print(f"📊 QUALIFIED FRESHER JOBS FEED ({len(qualified_list)} TOTAL QUALIFIED JOBS)")
    print("#"*85)
    for idx, job in enumerate(qualified_list[:15], 1):
        print(f"\n[{idx}] ATS Score: {job.ats_score}% | {job.company} - {job.title}")
        print(f"    Source Platform: {job.source_platform} | Location: {job.location}")
        print(f"    Apply URL:       {job.apply_url}")
        print(f"    Missing Skills:  {', '.join(job.missing_skills) if job.missing_skills else 'None'}")
        
    print("\n" + "#"*85)
    choice = input(f"\n👉 SELECT A JOB NUMBER [1 - {len(qualified_list)}] TO TARGET FOR RESUME TAILORING (default: #1): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(qualified_list):
        selected_index = int(choice) - 1
    else:
        selected_index = 0
        
    selected_job = qualified_list[selected_index]
    state["selected_job"] = selected_job
    state["gate_1_approved"] = True

    print(f"\n🎉 TARGET JOB SELECTED: [{selected_job.company} - {selected_job.title}] (ATS Score: {selected_job.ats_score}%)")

    # -----------------------------------------------------------------
    # STEP 6: DEDICATED ATS SCANNER API GAP ANALYSIS
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("🌐 STEP 6: DEDICATED ATS SCANNER API GAP ANALYSIS")
    print("="*85)
    full_resume_text = extract_full_raw_pdf_text(pdf_path)
    ats_results = call_rapidapi_ats_scorer(full_resume_text, selected_job.raw_jd)
    
    missing_kw = ", ".join(ats_results.get("missing_skills", ["LlamaIndex", "REST APIs", "Git/GitHub", "OpenAI APIs"]))
    print(f"   ATS Match Score:        {ats_results.get('ats_match_score')}%")
    print(f"   Missing Keywords:      {missing_kw}")

    # -----------------------------------------------------------------
    # STEP 7: NVIDIA NEMOTRON LLM SURGICAL LATEX ARCHITECT
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("🎨 STEP 7: NVIDIA NEMOTRON LLM SURGICAL LATEX ARCHITECT")
    print("="*85)
    latex_res = generate_latex_resume_node(state)
    state["latex_code"] = latex_res["latex_code"]
    state["tex_path"] = latex_res["tex_path"]

    # -----------------------------------------------------------------
    # STEP 8: AUTOMATED SINGLE-PAGE PDF RESUME COMPILER
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("⚙️ STEP 8: AUTOMATED SINGLE-PAGE PDF RESUME COMPILER")
    print("="*85)
    compiler_res = compile_latex_to_pdf_node(state)
    state["compiled_pdf_path"] = compiler_res["compiled_pdf_path"]

    # -----------------------------------------------------------------
    # STEP 9: PLAYWRIGHT BROWSER APPLICATION AGENT & GATE 2 INTERRUPT
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("🌐 STEP 9: PLAYWRIGHT BROWSER APPLICATION AGENT & GATE 2 INTERRUPT")
    print("="*85)
    browser_res = fill_and_apply_job_node(state)
    state["application_status"] = browser_res.get("application_status", "COMPLETED")

    # -----------------------------------------------------------------
    # FINAL SUMMARY & DOWNLOAD LOCATIONS
    # -----------------------------------------------------------------
    print("\n" + "="*85)
    print("🎉 CAREEROS MASTER AUTONOMOUS PIPELINE COMPLETE!")
    print("="*85)
    print(f"1. Target Job Selected:  [{selected_job.company} - {selected_job.title}]")
    print(f"2. Master LaTeX File:    file://{state['tex_path']}")
    if state["compiled_pdf_path"]:
        print(f"3. Single-Page PDF File: file://{state['compiled_pdf_path']}")
    print(f"4. Full Pipeline Log:    file://{log_file}")
    print("="*85 + "\n")

if __name__ == "__main__":
    run_master_career_os_pipeline()
