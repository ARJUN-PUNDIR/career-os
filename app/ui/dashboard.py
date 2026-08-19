import sys
import os
import time
import pandas as pd
import pdfplumber
import streamlit as st
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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
from app.tracker.db import (
    get_saved_jobs,
    get_today_usage_count,
    increment_daily_usage,
    check_daily_limit_exceeded
)

# Page Configuration & Modern Theme Styling
st.set_page_config(
    page_title="CareerOS - Autonomous Job Search & Application Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Impact Modern CSS Aesthetics
st.markdown("""
<style>
    /* Dark Theme Accent Gradient Header */
    .main-header {
        background: linear-gradient(135deg, #1E1E2F 0%, #0F2027 50%, #2C5364 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .main-header h1 {
        color: #00F2FE;
        font-size: 2.8rem;
        margin-bottom: 0px;
    }
    .main-header p {
        color: #E0E0E0;
        font-size: 1.1rem;
    }
    /* Job Card Glassmorphism Effect */
    .job-card {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        background-color: rgba(255, 255, 255, 0.03);
    }
    /* Badge Custom Styling */
    .ats-badge {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: black;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

def extract_full_raw_pdf_text(pdf_path: str) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    return full_text.strip()

def convert_jobs_to_csv(jobs_list: list) -> str:
    df = pd.DataFrame(jobs_list)
    return df.to_csv(index=False)

def main():
    # -----------------------------------------------------------------
    # HERO MODERN STYLED HEADER
    # -----------------------------------------------------------------
    st.markdown("""
    <div class="main-header">
        <h1>🚀 CareerOS Platform</h1>
        <p>Autonomous Multi-Agent Job Discovery, ATS Ranking & Browser Application Engine</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize Session State
    if "agent_state" not in st.session_state:
        st.session_state.agent_state = None
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    if "compiled_pdf" not in st.session_state:
        st.session_state.compiled_pdf = None
    if "application_completed" not in st.session_state:
        st.session_state.application_completed = False
    if "jobs_per_page" not in st.session_state:
        st.session_state.jobs_per_page = 15
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # Check Daily Rate Limit (Max 2 Runs Per Day)
    today_runs = get_today_usage_count()
    limit_exceeded = check_daily_limit_exceeded(max_limit=2)

    # -----------------------------------------------------------------
    # SIDEBAR: RATE LIMIT STATUS & SEARCH HISTORY DOWNLOAD
    # -----------------------------------------------------------------
    with st.sidebar:
        st.header("⚡ Usage & Rate Limits")
        st.write(f"Today's Executions: **{today_runs} / 2 Allowed**")
        
        if limit_exceeded:
            st.error("🔒 **Daily Limit Reached (2/2 Runs)**")
            st.caption("CareerOS is in testing phase. Daily runs are capped at 2 to protect API credit quotas.")
        else:
            st.success(f"✅ {2 - today_runs} Executions Remaining Today")

        st.divider()
        st.header("📂 Discovered Jobs Drawer")
        state = st.session_state.agent_state
        
        if state and state.get("ranked_jobs"):
            ranked_list = state["ranked_jobs"]
            qualified = [j for j in ranked_list if j.ats_score > 0.0]
            st.success(f"Feed Loaded: {len(qualified)} Jobs")
            
            st.subheader("Quick Jump Drawer")
            job_titles = [f"#{idx+1} [{j.ats_score}%] {j.company} - {j.title[:25]}" for idx, j in enumerate(qualified)]
            selected_drawer = st.selectbox("Jump to Job", options=job_titles, index=0)
            
            if st.button("📌 Select Job from Drawer", use_container_width=True):
                selected_idx = int(selected_drawer.split(" ")[0].replace("#", "")) - 1
                st.session_state.selected_job = qualified[selected_idx]
                st.info(f"Selected: {qualified[selected_idx].company}")
        else:
            st.info("Run search to populate jobs drawer.")

        st.divider()
        st.header("📜 Search History & Export")
        db_jobs = get_saved_jobs()
        if db_jobs:
            st.write(f"Total Stored Jobs in DB: **{len(db_jobs)}**")
            csv_data = convert_jobs_to_csv(db_jobs)
            st.download_button(
                label="⬇️ Download Job History (CSV)",
                data=csv_data,
                file_name=f"career_os_job_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # -----------------------------------------------------------------
    # STEP 1: UPLOAD RESUME & PREFERENCES
    # -----------------------------------------------------------------
    st.header("📄 Step 1: Upload Resume & Set Preferences")
    
    col1, col2 = st.columns([1, 1])
    pdf_path = os.path.join(settings.UPLOADS_DIR, "sample_resume.pdf")
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    with col1:
        uploaded_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"], key="main_uploader")
        if uploaded_file:
            user_pdf_path = os.path.join(settings.UPLOADS_DIR, "candidate_resume.pdf")
            with open(user_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            pdf_path = user_pdf_path
            st.success(f"✅ Active Resume: {uploaded_file.name}")
        elif os.path.exists(pdf_path):
            st.info("📄 Active Resume Loaded: sample_resume.pdf")

    with col2:
        target_role = st.text_input("Target Role", value="AI Intern / GenAI Engineer")
        target_locations = st.text_input("Preferred Locations", value="Remote, Gurugram, Noida, Delhi")
        target_stipend = st.text_input("Target Stipend / Salary", value="10k - 25k/month")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # RATE-LIMIT SAFEGUARD SEARCH TRIGGER
    search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
    with search_col2:
        if limit_exceeded:
            st.warning("⚠️ **Testing Phase Notice**: You have reached the maximum 2 daily runs allowed during the testing phase to prevent API overuse. Please return tomorrow!")
            run_search = False
        else:
            run_search = st.button("⚡ Start Real-Time Job Discovery & ATS Ranking", type="primary", use_container_width=True)

    # -----------------------------------------------------------------
    # REAL-TIME STEPPER & SEARCH EXECUTION
    # -----------------------------------------------------------------
    if run_search:
        if not os.path.exists(pdf_path):
            st.error("❌ Please upload a resume PDF file first!")
        else:
            # Increment Daily Usage Count
            increment_daily_usage()
            
            status_box = st.status("🚀 Launching CareerOS Multi-Agent Pipeline...", expanded=True)
            
            # STEPPER 1: PARSING RESUME
            status_box.write("⏳ **Step 1/4: Parsing Candidate Resume ($0-Token MD5 Cache)...**")
            time.sleep(0.5)
            
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
            
            state["candidate_profile"] = parse_resume_node(state)["candidate_profile"]
            status_box.write("✅ **Step 1 Complete: Resume Parsed Successfully!**")
            
            # STEPPER 2: CAREER PLANNER
            status_box.write("⏳ **Step 2/4: Formulating 3-Pillar Search Queries (NVIDIA Nemotron LLM)...**")
            planner_res = plan_career_strategy_node(state)
            state["search_strategy"] = planner_res["search_strategy"]
            status_box.write("✅ **Step 2 Complete: 3-Pillar Strategy Formulated!**")
            
            # STEPPER 3: 3-PILLAR JOB SEARCH
            status_box.write("⏳ **Step 3/4: Fetching Live Postings from JSearch API & Google ATS...**")
            state["discovered_jobs"] = search_jobs_node(state)["discovered_jobs"]
            status_box.write(f"✅ **Step 3 Complete: Ingested {len(state['discovered_jobs'])} Live Postings!**")
            
            # STEPPER 4: ATS RANKING ENGINE
            status_box.write("⏳ **Step 4/4: Executing Deterministic ATS Ranking Engine (< 10ms)...**")
            state["ranked_jobs"] = rank_jobs_node(state)["ranked_jobs"]
            status_box.write("✅ **Step 4 Complete: All Jobs Ranked & Sorted by ATS Score!**")
            
            status_box.update(label="🎉 Multi-Agent Discovery Complete!", state="complete", expanded=False)
            
            st.session_state.agent_state = state
            st.rerun()

    # -----------------------------------------------------------------
    # STEP 2: INTERACTIVE ATS-SORTED JOB FEED WITH PAGINATION
    # -----------------------------------------------------------------
    state = st.session_state.agent_state
    if state and state.get("ranked_jobs"):
        st.divider()
        st.header("📊 Step 2: ATS-Sorted Job Feed & Target Selection")
        
        ranked_list = state["ranked_jobs"]
        qualified = [j for j in ranked_list if j.ats_score > 0.0]
        
        # Pagination & View Controls
        st_c1, st_c2, st_c3 = st.columns([2, 2, 2])
        with st_c1:
            st.markdown(f"**Total Discovered Jobs**: `{len(qualified)}`")
        with st_c2:
            jobs_per_page = st.selectbox("Jobs per Page", options=[15, 30, 50, "All"], index=0)
            if jobs_per_page == "All":
                st.session_state.jobs_per_page = len(qualified)
            else:
                st.session_state.jobs_per_page = jobs_per_page
        with st_c3:
            total_pages = max(1, (len(qualified) + st.session_state.jobs_per_page - 1) // st.session_state.jobs_per_page)
            current_page = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
            st.session_state.current_page = current_page

        start_idx = (st.session_state.current_page - 1) * st.session_state.jobs_per_page
        end_idx = start_idx + st.session_state.jobs_per_page
        page_jobs = qualified[start_idx:end_idx]

        st.markdown(f"Showing Jobs **#{start_idx+1} to #{min(end_idx, len(qualified))}** (Sorted by ATS Match Score)")
        
        for idx, job in enumerate(page_jobs, start=start_idx+1):
            st.markdown("---")
            job_col1, job_col2 = st.columns([4, 1])
            
            with job_col1:
                st.markdown(f"### [{idx}] ATS Match Score: **{job.ats_score}%** | {job.company} - {job.title}")
                st.write(f"📍 **Location**: {job.location} | 💰 **Salary**: {job.salary_range} | 🌐 **Platform**: `{job.source_platform}`")
                st.write(f"🔗 **Apply Link**: [{job.apply_url}]({job.apply_url})")
                if job.missing_skills:
                    st.warning(f"⚠️ **Missing ATS Keywords**: {', '.join(job.missing_skills)}")
            
            with job_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"🎯 Select Job #{idx}", key=f"target_job_{idx}", type="primary", use_container_width=True):
                    st.session_state.selected_job = job
                    state["selected_job"] = job
                    st.success(f"Selected: {job.company}")
                    st.rerun()

    # -----------------------------------------------------------------
    # STEP 3: TAILOR RESUME PDF & BROWSER APPLICATION AGENT
    # -----------------------------------------------------------------
    selected_job = st.session_state.selected_job
    if selected_job:
        st.divider()
        st.header(f"🚀 Step 3: Application & Browser Agent for [{selected_job.company}]")
        st.write(f"**Selected Role**: {selected_job.title} | **Location**: {selected_job.location}")

        if not st.session_state.application_completed:
            tailor_col1, tailor_col2 = st.columns(2)
            with tailor_col1:
                if st.button("🎨 Tailor Jake's Resume PDF for this Job", type="primary", use_container_width=True):
                    with st.spinner(f"Analyzing ATS keyword gaps & compiling Jake's Resume PDF..."):
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
                st.subheader("📄 Download Tailored PDF Resume")
                with open(compiled_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download Tailored Jake's Resume PDF",
                        data=pdf_file,
                        file_name=os.path.basename(compiled_pdf),
                        mime="application/pdf"
                    )

            st.subheader("🌐 Playwright Persistent Browser Agent")
            st.info("💡 **Persistent Login Session**: Firefox/Brave opens with saved logins (`data/brave_user_profile`). Log in once to Shine, Internshala, or LinkedIn and Playwright auto-fills the rest!")

            if st.button("🚀 Open Browser & Apply Live", type="primary", use_container_width=True):
                with st.spinner("Opening persistent browser window, detecting portal fields, and attaching PDF resume..."):
                    state["selected_job"] = selected_job
                    state["compiled_pdf_path"] = compiled_pdf
                    res = fill_and_apply_job_node(state)
                    st.session_state.application_completed = True
                    st.success(f"🎉 Application Processed for [{selected_job.company}]!")
                    st.rerun()

        # -----------------------------------------------------------------
        # LOOPING OPTION: APPLY TO ANOTHER JOB OR EXIT
        # -----------------------------------------------------------------
        if st.session_state.application_completed:
            st.success(f"🎉 Completed Application for [{selected_job.company} - {selected_job.title}]!")
            st.divider()
            st.subheader("🔄 What would you like to do next?")
            
            loop_col1, loop_col2 = st.columns(2)
            with loop_col1:
                if st.button("🔄 Apply to Another Job from Feed / Drawer", type="primary", use_container_width=True):
                    st.session_state.selected_job = None
                    st.session_state.compiled_pdf = None
                    st.session_state.application_completed = False
                    st.rerun()
                    
            with loop_col2:
                if st.button("🏁 Finish & Exit Session", use_container_width=True):
                    st.session_state.clear()
                    st.success("Session finished! Thank you for using CareerOS.")
                    st.rerun()

if __name__ == "__main__":
    main()
