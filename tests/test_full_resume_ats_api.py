import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pdfplumber
from app.config.settings import settings
from app.services.rapidapi_ats import call_rapidapi_ats_scorer

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

def extract_full_raw_pdf_text(pdf_path: str) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    return full_text.strip()

def run_full_resume_ats_api_test():
    pdf_path = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Resume PDF not found at {pdf_path}")
        return

    full_resume_text = extract_full_raw_pdf_text(pdf_path)

    print("\n" + "="*85)
    print("🚀 DEDICATED ATS SCANNER API TESTER (100% FULL UN-TRUNCATED RESUME CONTENT)")
    print("="*85)

    print("\n" + "#"*85)
    print("📥 PART 1: EXACT INPUT SENT TO DEDICATED ATS SCANNER API")
    print("#"*85)
    print("\n📄 [INPUT 1: FULL UNCUT RESUME CONTENT]:")
    print("-" * 75)
    print(full_resume_text)
    print("-" * 75)
    print("\n🎯 [INPUT 2: TARGET JOB DESCRIPTION]:")
    print("-" * 75)
    print(DIGITALXNODE_JD.strip())
    print("-" * 75)

    print("\n" + "#"*85)
    print("📤 PART 2: OUTPUT RECEIVED FROM DEDICATED ATS SCANNER API")
    print("#"*85)

    print("\n⚡ Sending 100% full resume content & JD to dedicated ATS API...")
    ats_results = call_rapidapi_ats_scorer(full_resume_text, DIGITALXNODE_JD)

    print("\n📊 [API RESULTS SUMMARY]:")
    print(f"   🎯 OVERALL ATS MATCH SCORE: {ats_results.get('ats_match_score')}%")

    print(f"\n   ✅ MATCHED SKILLS ({len(ats_results.get('matched_skills', []))}):")
    for m in ats_results.get('matched_skills', []):
        print(f"      • {m}")

    print(f"\n   ❌ MISSING SKILLS ({len(ats_results.get('missing_skills', []))}):")
    for k in ats_results.get('missing_skills', []):
        print(f"      • {k}")

    print(f"\n   💡 RECRUITER RECOMMENDATIONS:")
    for tip in ats_results.get('recommendations', []):
        print(f"      👉 {tip}")

    print("\n" + "="*85 + "\n")

if __name__ == "__main__":
    run_full_resume_ats_api_test()
