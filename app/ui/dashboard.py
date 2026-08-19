import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
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
from app.tracker.db import get_saved_jobs
from app.schemas.models import JobRequirementsInput, UnifiedJobListing
from app.graph.state import AgentState

# Page Configuration
st.set_page_config(
    page_title="CareerOS - Autonomous Job Application Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def extract_full_raw_pdf_text(pdf_path: str) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    return full_text.strip()

def main():
    st.title("🚀 CareerOS: Multi-Agent Job Search & Application Platform")
    st.caption("Powered by LangGraph • NVIDIA Nemotron-3 LLM • Playwright • RapidAPI Hub")

    # Initialize Session State
    if "agent_state" not in st.session_state:
        st.session_state.agent_state = None
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    if "compiled_pdf" not in st.session_state:
        st.session_state.compiled_pdf = None

    # Sidebar Controls
    with st.sidebar:
        st.header("⚙️ Candidate Settings")
        
        # Resume File Uploader
        uploaded_file = st.file_uploader("📄 Upload Candidate Resume (PDF)", type=["pdf"])
        pdf_path = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
        os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
        
        if uploaded_file:
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded: {uploaded_file.name}")
        elif os.path.exists(pdf_path):
            st.info("Using default resume: arjun_resume.pdf")

        st.divider()
        st.subheader("🎯 Preferences")
        target_role = st.text_input("Target Role", value="AI Intern / GenAI Engineer")
        target_locations = st.text_input("Preferred Locations", value="Remote, Gurugram, Noida, Delhi")
        target_stipend = st.text_input("Target Stipend / Salary", value="10k - 25k/month")
        
        st.divider()
        st.subheader("🔑 API Key Status (Cloud Secrets)")
        st.write(f"NVIDIA API: {'✅ Configured' if settings.NVIDIA_API_KEY else '❌ Missing'}")
        st.write(f"RapidAPI Hub: {'✅ Configured' if settings.RAPIDAPI_KEY else '❌ Missing'}")
        st.write(f"SerpAPI Google: {'✅ Configured' if settings.SERPAPI_KEY else '❌ Missing'}")

    # Tabs Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 1. Job Discovery & ATS Feed",
        "🎨 2. Tailored Resume & LaTeX",
        "🤖 3. Browser Application Agent",
        "📈 4. Database & Analytics Logs"
    ])

    # -----------------------------------------------------------------
    # TAB 1: JOB DISCOVERY & ATS FEED
    # -----------------------------------------------------------------
    with tab1:
        st.header("🌐 Multi-Source Job Discovery & ATS Ranking")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            run_search = st.button("🚀 Run Job Search & ATS Ranking", type="primary", use_container_width=True)
            
        if run_search:
            with st.spinner("Parsing resume, generating search strategy, and searching 3-pillar engines..."):
                locs_list = [loc.strip() for loc in target_locations.split(",")]
                user_reqs = JobRequirementsInput(
                    target_role=target_role,
                    target_locations=locs_list,
                    min_stipend_lpa=target_stipend,
                    days_posted=10
                )
                
                state: AgentState = {
                    "resume_pdf_path": pdf_path if os.path.exists(pdf_path) else None,
                    "candidate_profile": None,
                    "user_requirements": user_reqs,
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
                
                # Execute Pipeline Nodes 1 - 4
                state["candidate_profile"] = parse_resume_node(state)["candidate_profile"]
                planner_res = plan_career_strategy_node(state)
                state["search_strategy"] = planner_res["search_strategy"]
                state["discovered_jobs"] = search_jobs_node(state)["discovered_jobs"]
                state["ranked_jobs"] = rank_jobs_node(state)["ranked_jobs"]
                
                st.session_state.agent_state = state
                st.success(f"Discovered & Ranked {len(state['ranked_jobs'])} jobs successfully!")

        state = st.session_state.agent_state
        if state and state.get("ranked_jobs"):
            ranked_list = state["ranked_jobs"]
            qualified = [j for j in ranked_list if j.ats_score > 0.0]
            
            st.subheader(f"📋 Qualified Job Postings ({len(qualified)} Total)")
            
            for idx, job in enumerate(qualified[:15], 1):
                with st.expander(f"[{idx}] ATS Match: {job.ats_score}% | {job.company} - {job.title} ({job.location})"):
                    st.write(f"**Source Platform**: `{job.source_platform}` | **Salary**: `{job.salary_range}`")
                    st.write(f"**Apply URL**: [{job.apply_url}]({job.apply_url})")
                    if job.missing_skills:
                        st.warning(f"**Missing Keywords**: {', '.join(job.missing_skills)}")
                    st.text_area("Job Description Snippet", job.raw_jd[:400], height=100, key=f"jd_{idx}")
                    
                    if st.button(f"🎯 Target & Tailor Resume for [{job.company}]", key=f"btn_{idx}"):
                        st.session_state.selected_job = job
                        state["selected_job"] = job
                        st.success(f"Selected target job: {job.company} - {job.title}")

    # -----------------------------------------------------------------
    # TAB 2: TAILORED RESUME & LATEX
    # -----------------------------------------------------------------
    with tab2:
        st.header("🎨 NVIDIA Nemotron LLM Surgical LaTeX Architect")
        selected_job = st.session_state.selected_job
        
        if not selected_job:
            st.info("👈 Please select a target job from Tab 1 first!")
        else:
            st.subheader(f"Targeting: {selected_job.company} - {selected_job.title}")
            
            if st.button("🔨 Tailor Resume & Compile PDF", type="primary"):
                with st.spinner("Analyzing ATS keyword gaps & compiling Jake's Resume PDF..."):
                    full_resume_text = extract_full_raw_pdf_text(pdf_path)
                    ats_results = call_rapidapi_ats_scorer(full_resume_text, selected_job.raw_jd)
                    
                    state["selected_job"] = selected_job
                    latex_res = generate_latex_resume_node(state)
                    state["latex_code"] = latex_res["latex_code"]
                    state["tex_path"] = latex_res["tex_path"]
                    
                    compiler_res = compile_latex_to_pdf_node(state)
                    state["compiled_pdf_path"] = compiler_res["compiled_pdf_path"]
                    st.session_state.compiled_pdf = compiler_res["compiled_pdf_path"]
                    st.success("Successfully tailored & compiled single-page PDF resume!")

            compiled_pdf = st.session_state.compiled_pdf
            if compiled_pdf and os.path.exists(compiled_pdf):
                st.subheader("📄 Tailored Single-Page PDF Resume")
                with open(compiled_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download Tailored Jake's Resume PDF",
                        data=pdf_file,
                        file_name=os.path.basename(compiled_pdf),
                        mime="application/pdf",
                        type="primary"
                    )
                st.write(f"**PDF File Location**: `{compiled_pdf}`")

    # -----------------------------------------------------------------
    # TAB 3: BROWSER APPLICATION AGENT
    # -----------------------------------------------------------------
    with tab3:
        st.header("🤖 Playwright Browser Application Agent")
        selected_job = st.session_state.selected_job
        
        if not selected_job:
            st.info("👈 Please select a target job from Tab 1 first!")
        else:
            st.write(f"**Target Company**: {selected_job.company}")
            st.write(f"**Apply URL**: [{selected_job.apply_url}]({selected_job.apply_url})")
            
            if st.button("🚀 Launch Playwright Browser Agent", type="primary"):
                with st.spinner("Opening browser agent, populating fields & attaching PDF resume..."):
                    state["selected_job"] = selected_job
                    if st.session_state.compiled_pdf:
                        state["compiled_pdf_path"] = st.session_state.compiled_pdf
                    res = fill_and_apply_job_node(state)
                    st.success(f"Browser session complete! Status: {res.get('application_status')}")

    # -----------------------------------------------------------------
    # TAB 4: DATABASE & ANALYTICS LOGS
    # -----------------------------------------------------------------
    with tab4:
        st.header("📈 SQLite Database Tracker Logs")
        db_jobs = get_saved_jobs()
        if db_jobs:
            df = pd.DataFrame(db_jobs)
            st.dataframe(df[["job_id", "company", "title", "source_platform", "location", "discovered_at"]], use_container_width=True)
            st.write(f"**Total Jobs Saved in SQLite DB**: `{len(db_jobs)}`")

if __name__ == "__main__":
    main()
