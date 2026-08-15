import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pdfplumber
import subprocess
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from app.config.settings import settings
from app.config.model_factory import get_llm
from app.agents.parser import parse_resume_node
from app.services.rapidapi_ats import call_rapidapi_ats_scorer
from app.graph.state import AgentState

DIGITALXNODE_JD = """
DigitalXnode - AI/ML Intern (LLMs, RAG, Agentic AI, Multi-Agent Systems)

Calling AI/ML Freshers & Aspiring AI Engineers!
At DigitalXnode, we're looking for enthusiastic, curious, and self-driven AI/ML Interns who are eager to learn, innovate, and contribute to impactful AI products.

What You'll Work On:
- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- Agentic AI Systems & Intelligent Workflows
- Multi-Agent Systems & AI Automation
- Prompt Engineering & Generative AI Applications
- Python for AI Development, REST APIs, and Model Integrations

Skills We're Looking For:
- Python Programming & Machine Learning Fundamentals
- Large Language Models (LLMs), Generative AI, NLP, Prompt Engineering
- LangChain, LangGraph, or LlamaIndex (preferred but not mandatory)
- OpenAI APIs or other LLM APIs, REST APIs
- Git & GitHub, Vector Databases (basic understanding)
- Problem-solving mindset & Strong communication skills

Eligibility:
Students pursuing B.Tech, M.Tech, MCA, BCA or recent graduates. Basic programming knowledge in Python.
"""

STRICT_SURGICAL_LATEX_PROMPT = """You are a Master LaTeX Engineer.
Your task is to take Arjun's EXACT MASTER LATEX CODE and perform SURGICAL ATS KEYWORD INFUSION ONLY.

STRICT LAWS (ZERO STRUCTURAL BREAKAGE):
1. KEEP THE EXACT LATEX PREAMBLE, PACKAGES, MARGINS, HEADINGS, AND CUSTOM COMMANDS (\resumeSubheading, \resumeProjectHeading, \resumeItem) 100% UNCHANGED.
2. KEEP ALL PERSONAL FACTS (KIET University, B.Tech, CGPA 8.66, Nexus AI, CareerOS, AWS certifications, LeetCode 200+) 100% TRUTHFUL.
3. SURGICAL KEYWORD INFUSION: Seamlessly weave the MISSING HIGH-IMPACT KEYWORDS ({missing_keywords}) into the Technical Skills section and the bullet points under \\section{{Projects}} (Nexus AI & CareerOS).
4. Return ONLY valid, compilable LaTeX code. DO NOT wrap the output in markdown backticks.

EXACT MASTER LATEX BASE CODE TO SURGICALLY ENHANCE:
{master_latex_base}

MISSING KEYWORDS TO SEAMLESSLY INFUSE:
{missing_keywords}

JOB DESCRIPTION TARGET:
{jd_text}
"""

def extract_full_raw_pdf_text(pdf_path: str) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    return full_text.strip()

def run_jakes_resume_test():
    pdf_path = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
    template_path = os.path.join(settings.BASE_DIR, "app", "templates", "jake.tex")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Resume PDF not found at {pdf_path}")
        return
        
    if not os.path.exists(template_path):
        print(f"❌ Error: Master LaTeX template not found at {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        master_latex_base = f.read()

    print("\n" + "="*85)
    print("🚀 MASTER JAKE'S RESUME SURGICAL KEYWORD INFUSION & PDF COMPILER TEST")
    print("="*85)

    # 1. Parse Candidate Facts
    state: AgentState = {
        "resume_pdf_path": pdf_path,
        "candidate_profile": None,
        "user_requirements": None,
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
    parser_res = parse_resume_node(state)
    candidate = parser_res["candidate_profile"]

    # 2. Get Dedicated ATS Scanner API Gap Report
    print("\n⚡ [ATS Scanner API] Fetching ATS Gap Analysis for DigitalXnode...")
    resume_text = f"Skills: {', '.join(candidate.skills)}. Projects: {[p.name for p in candidate.projects]}"
    ats_results = call_rapidapi_ats_scorer(resume_text, DIGITALXNODE_JD)
    missing_kw = ", ".join(ats_results.get("missing_skills", ["LlamaIndex", "REST APIs", "Git/GitHub", "OpenAI APIs"]))

    # PART 1: INPUT GIVEN
    print("\n" + "#"*85)
    print("📥 PART 1: INPUT GIVEN TO NVIDIA NEMOTRON LLM LATEX ARCHITECT")
    print("#"*85)
    print(f"👤 Candidate: {candidate.full_name}")
    print(f"🎯 Target Job: DigitalXnode - AI/ML Intern")
    print(f"📊 ATS Match Score: {ats_results.get('ats_match_score')}%")
    print(f"❌ Missing Keywords To Infuse: {missing_kw}")
    print("#"*85)

    # 3. Call NVIDIA Nemotron LLM
    print("\n🎨 [NVIDIA Nemotron LLM] Performing Surgical Keyword Infusion on Master LaTeX Base...")
    prompt = ChatPromptTemplate.from_template(STRICT_SURGICAL_LATEX_PROMPT)
    llm = get_llm(temperature=0.1)
    
    chain = prompt | llm
    response = chain.invoke({
        "master_latex_base": master_latex_base,
        "missing_keywords": missing_kw,
        "jd_text": DIGITALXNODE_JD[:1200]
    })

    latex_code = response.content.strip()
    if latex_code.startswith("```latex"):
        latex_code = latex_code[8:]
    elif latex_code.startswith("```"):
        latex_code = latex_code[3:]
    if latex_code.endswith("```"):
        latex_code = latex_code[:-3]
    latex_code = latex_code.strip()

    output_dir = os.path.join(settings.BASE_DIR, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, "arjun_master_jake_resume_digitalxnode.tex")
    
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    # PART 2: GENERATED LATEX CODE
    print("\n" + "#"*85)
    print("📄 PART 2: SURGICALLY TAILORED JAKE'S RESUME LATEX CODE")
    print("#"*85)
    print(latex_code[:1200])
    print(f"\n... (Complete Master LaTeX code saved to: file://{tex_path})")
    print("#"*85)

    # PART 3: COMPILE LATEX TO PDF
    print("\n" + "#"*85)
    print("⚙️ PART 3: COMPILED SINGLE-PAGE PDF RESUME")
    print("#"*85)
    
    pdf_path = tex_path.replace(".tex", ".pdf")
    pdflatex_cmd = None
    for cmd in ["pdflatex", "xelatex"]:
        try:
            res = subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                pdflatex_cmd = cmd
                break
        except FileNotFoundError:
            continue

    if pdflatex_cmd:
        print(f"🔨 Compiling PDF via local '{pdflatex_cmd}'...")
        subprocess.run([pdflatex_cmd, "-interaction=nonstopmode", f"-output-directory={output_dir}", tex_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)

    print("\n" + "="*85)
    print("🎉 SURGICAL JAKE'S RESUME GENERATION & COMPILATION COMPLETE!")
    print("="*85)
    print(f"📄 Master LaTeX File: file://{tex_path}")
    if os.path.exists(pdf_path):
        print(f"📄 Compiled PDF File: file://{pdf_path}")
    else:
        print(f"📄 Open Overleaf & Paste Code From: file://{tex_path}")
    print("="*85 + "\n")

if __name__ == "__main__":
    run_jakes_resume_test()
