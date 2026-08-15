import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.settings import settings
from app.agents.parser import parse_resume_node
from app.agents.browser import fill_and_apply_job_node
from app.schemas.models import UnifiedJobListing
from app.graph.state import AgentState

DIGITALXNODE_SHINE_URL = "https://www.shine.com/jobs/ai-ml-internship-llm-rag-agentic-ai-real-projects-apply-now/digitalxnode/19166341"

def run_browser_agent_test():
    pdf_path = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
    output_dir = os.path.join(settings.BASE_DIR, "data", "output")
    tailored_pdf = os.path.join(output_dir, "arjun_master_jake_resume_digitalxnode.pdf")
    
    if not os.path.exists(tailored_pdf):
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".pdf")] if os.path.exists(output_dir) else []
        tailored_pdf = files[0] if files else pdf_path

    print("\n" + "="*85)
    print("🚀 REAL DEMO: PLAYWRIGHT BROWSER APPLICATION AGENT (LIVE SHINE.COM JOB PAGE)")
    print("="*85)
    print(f"🎯 Target Company: DigitalXnode")
    print(f"🎯 Target Job:     AI/ML Internship (LLMs, RAG, Agentic AI)")
    print(f"🔗 Live Apply URL: {DIGITALXNODE_SHINE_URL}")
    print(f"📄 Tailored PDF:   file://{tailored_pdf}")
    print("="*85)

    # 1. Parse Candidate Profile
    state: AgentState = {
        "resume_pdf_path": pdf_path,
        "candidate_profile": None,
        "user_requirements": None,
        "search_strategy": None,
        "discovered_jobs": [],
        "ranked_jobs": [],
        "selected_job": UnifiedJobListing(
            job_id="digitalxnode_shine_19166341",
            title="AI/ML Internship (LLM, RAG, Agentic AI)",
            company="DigitalXnode",
            source_platform="Shine.com",
            location="Remote / Gurugram",
            date_posted="Live",
            raw_jd="AI/ML Internship working on LLMs, RAG, Agentic AI, Prompt Engineering, Python",
            apply_url=DIGITALXNODE_SHINE_URL,
            salary_range="10k - 25k/month"
        ),
        "tailored_profile": None,
        "audit_result": None,
        "compiled_pdf_path": tailored_pdf,
        "cover_letter_text": None,
        "gate_1_approved": True,
        "gate_2_approved": False,
        "application_status": "DISCOVERED",
        "tracker_logs": [],
        "error_message": None
    }

    parser_res = parse_resume_node(state)
    state["candidate_profile"] = parser_res["candidate_profile"]

    # 2. Run Playwright Browser Application Agent Node
    res = fill_and_apply_job_node(state)

    print("\n" + "="*85)
    print("🎉 REAL DEMO: PLAYWRIGHT BROWSER AGENT COMPLETE!")
    print(f"   Attached Resume PDF: {os.path.basename(tailored_pdf)}")
    print(f"   Application Status:  {res.get('application_status')}")
    print("="*85 + "\n")

if __name__ == "__main__":
    run_browser_agent_test()
