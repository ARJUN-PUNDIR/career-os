import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import pdfplumber
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
from app.schemas.models import JobRequirementsInput, UnifiedJobListing
from app.graph.state import AgentState

# Page Configuration
st.set_page_config(
    page_title="CareerOS - Autonomous Job Search & Application Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    # -----------------------------------------------------------------
    # HERO SECTION: CENTERED HEADER & STEP-BY-STEP PROGRESS
    # -----------------------------------------------------------------
    st.markdown("<h1 style='text-align: center;'>🚀 CareerOS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Autonomous Job Search & Application Platform</h3>", unsafe_allow_html=True)
    st.caption("<div style='text-align: center;'>Powered by LangGraph • NVIDIA Nemotron-3 LLM • Playwright • RapidAPI Hub</div>", unsafe_allow_html=True)
    st.divider()

    # Step-by-Step How It Works Banner
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("📄 **1. Upload Resume**\n$0-Token MD5 Hash Cache")
    with col2:
        st.info("🎯 **2. Set Preferences**\nRole, Locations, Stipend")
    with col3:
        st.info("🔍 **3. Search & Rank**\n3-Pillar Engines & ATS Scoring")
    with col4:
        st.info("🚀 **4. Tailor & Apply**\nJake's PDF & Browser Agent")

    st.divider()

    # Initialize Session State Variables
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "agent_state" not in st.session_state:
        st.session_state.agent_state = None
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    if "compiled_pdf" not in st.session_state:
        st.session_state.compiled_pdf = None
    if "application_completed" not in st.session_state:
        st.session_state.application_completed = False

    # -----------------------------------------------------------------
    # STEP 1: CENTERED RESUME FILE UPLOAD & PARSING
    # -----------------------------------------------------------------
    st.header("📄 Step 1: Upload Candidate Resume")
    
    upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
    pdf_path = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    with upload_col2:
        uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"], key="main_resume_uploader")
        if uploaded_file:
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Resume Uploaded Successfully: {uploaded_file.name}")
        elif os.path.exists(pdf_path):
            st.info("📄 Active Resume Loaded: arjun_resume.pdf")

    st.divider()

    # -----------------------------------------------------------------
    # STEP 2: JOB PREFERENCES & REQUIREMENTS
    # -----------------------------------------------------------------
    st.header("🎯 Step 2: Target Job Requirements")
    
    req_col1, req_col2, req_col3 = st.columns(3)
    with req_col1:
        target_role = st.text_input("Target Role", value="AI Intern / GenAI Engineer")
    with req_col2:
        target_locations = st.text_input("Preferred Locations", value="Remote, Gurugram, Noida, Delhi")
    with req_col3:
        target_stipend = st.text_input("Target Salary / Stipend", value="10k - 25k/month")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # SEARCH TRIGGER BUTTON
    search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
    with search_col2:
        run_search = st.button("🔍 Search & Sort Jobs by ATS Match Score", type="primary", use_container_width=True)

    if run_search:
        if not os.path.exists(pdf_path):
            st.error("❌ Please upload a resume PDF file first!")
        else:
            with st.spinner("Parsing resume, generating search strategy, and fetching live jobs across 3-pillar engines..."):
                locs_list = [loc.strip() for loc in target_locations.split(",")]
                user_reqs = JobRequirementsInput(
                    target_role=target_role,
                    target_locations=locs_list,
                    min_stipend_lpa=target_stipend,
                    days_posted=10
                )
                
                state: AgentState = {
                    "resume_pdf_path": pdf_path,
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
                st.session_state.current_step = 3
                st.success(f"Discovered & Sorted {len(state['ranked_jobs'])} jobs by ATS Match Score!")

    # -----------------------------------------------------------------
    # STEP 3: ATS-SORTED JOB FEED & JOB SELECTION
    # -----------------------------------------------------------------
    state = st.session_state.agent_state
    if state and state.get("ranked_jobs"):
        st.divider()
        st.header("📊 Step 3: ATS-Sorted Job Feed (Select Job to Apply)")
        
        ranked_list = state["ranked_jobs"]
        qualified = [j for j in ranked_list if j.ats_score > 0.0]
        
        # Display ATS Score Stats
        st.markdown(f"**Found {len(qualified)} Qualified Postings Sorted by ATS Score**")
        
        for idx, job in enumerate(qualified[:15], 1):
            st.markdown(f"---")
            job_col1, job_col2 = st.columns([4, 1])
            
            with job_col1:
                st.markdown(f"### [{idx}] ATS Score: **{job.ats_score}%** | {job.company} - {job.title}")
                st.write(f"📍 **Location**: {job.location} | 💰 **Salary**: {job.salary_range} | 🌐 **Platform**: `{job.source_platform}`")
                st.write(f"🔗 **Apply Link**: [{job.apply_url}]({job.apply_url})")
                if job.missing_skills:
                    st.warning(f"⚠️ **Missing ATS Keywords**: {', '.join(job.missing_skills)}")
            
            with job_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"🎯 Target & Apply to #{idx}", key=f"target_btn_{idx}", type="primary", use_container_width=True):
                    st.session_state.selected_job = job
                    state["selected_job"] = job
                    st.session_state.current_step = 4
                    st.rerun()

    # -----------------------------------------------------------------
    # STEP 4: TAILOR RESUME PDF & PLAYWRIGHT BROWSER APPLICATION
    # -----------------------------------------------------------------
    selected_job = st.session_state.selected_job
    if selected_job and st.session_state.current_step >= 4:
        st.divider()
        st.header(f"🚀 Step 4: Tailoring Resume & Applying to [{selected_job.company}]")
        st.write(f"**Target Role**: {selected_job.title} | **Location**: {selected_job.location}")

        if not st.session_state.application_completed:
            with st.spinner(f"Running ATS Gap Analysis & Compiling Jake's Resume PDF for {selected_job.company}..."):
                full_resume_text = extract_full_raw_pdf_text(pdf_path)
                ats_results = call_rapidapi_ats_scorer(full_resume_text, selected_job.raw_jd)
                
                state["selected_job"] = selected_job
                latex_res = generate_latex_resume_node(state)
                state["latex_code"] = latex_res["latex_code"]
                state["tex_path"] = latex_res["tex_path"]
                
                compiler_res = compile_latex_to_pdf_node(state)
                state["compiled_pdf_path"] = compiler_res["compiled_pdf_path"]
                st.session_state.compiled_pdf = compiler_res["compiled_pdf_path"]
                
                st.success("✅ Tailored Single-Page Jake's Resume PDF Compiled!")

            compiled_pdf = st.session_state.compiled_pdf
            if compiled_pdf and os.path.exists(compiled_pdf):
                with open(compiled_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download Tailored Jake's Resume PDF",
                        data=pdf_file,
                        file_name=os.path.basename(compiled_pdf),
                        mime="application/pdf"
                    )

            st.subheader("🌐 Launching Playwright Browser Application Agent...")
            if st.button("🚀 Launch Browser & Fill Form Live", type="primary", use_container_width=True):
                with st.spinner("Opening Firefox browser, navigating to portal, and populating form fields..."):
                    state["selected_job"] = selected_job
                    state["compiled_pdf_path"] = compiled_pdf
                    res = fill_and_apply_job_node(state)
                    st.session_state.application_completed = True
                    st.success(f"🎉 Browser Session Complete for [{selected_job.company}]!")
                    st.rerun()

        # -----------------------------------------------------------------
        # LOOPING OPTION: APPLY TO ANOTHER JOB OR EXIT
        # -----------------------------------------------------------------
        if st.session_state.application_completed:
            st.success(f"🎉 Successfully Processed Application for [{selected_job.company} - {selected_job.title}]!")
            st.divider()
            st.subheader("🔄 What would you like to do next?")
            
            loop_col1, loop_col2 = st.columns(2)
            with loop_col1:
                if st.button("🔄 Apply to Another Job from ATS Feed", type="primary", use_container_width=True):
                    st.session_state.selected_job = None
                    st.session_state.compiled_pdf = None
                    st.session_state.application_completed = False
                    st.session_state.current_step = 3
                    st.rerun()
                    
            with loop_col2:
                if st.button("🏁 Finish & Exit Session", use_container_width=True):
                    st.session_state.clear()
                    st.success("Session finished! Thank you for using CareerOS.")
                    st.rerun()

if __name__ == "__main__":
    main()
