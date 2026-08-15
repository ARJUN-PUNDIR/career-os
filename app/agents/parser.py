import pdfplumber
import os
import hashlib
from typing import Dict, Any
from app.config.settings import settings
from app.config.model_factory import get_llm
from app.schemas.models import CandidateProfile
from app.graph.state import AgentState
from app.tracker.db import get_cached_resume_profile, save_resume_profile_cache

def calculate_pdf_hash(pdf_path: str) -> str:
    """Calculates MD5 hash of raw PDF file contents to detect file changes."""
    with open(pdf_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text content from a PDF file using pdfplumber."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Resume PDF not found at path: {pdf_path}")
        
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
                
    return extracted_text.strip()

def parse_resume_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node with $0-Token Smart Caching:
    1. Computes MD5 hash of PDF file.
    2. If hash matches SQLite DB, loads profile in <1ms (0 LLM Tokens spent!).
    3. If PDF is new or updated, calls LLM and saves to cache.
    """
    pdf_path = state.get("resume_pdf_path")
    print(f"📄 [Parser Agent] Checking resume file: {pdf_path}")
    
    # 1. Compute PDF MD5 Hash
    pdf_hash = calculate_pdf_hash(pdf_path)
    
    # 2. Check SQLite DB Cache
    cached_profile_dict = get_cached_resume_profile(pdf_hash)
    if cached_profile_dict:
        print("💾 [Parser Cache HIT] Resume PDF unchanged. Loaded profile from SQLite DB (0 LLM Tokens spent)!")
        candidate_profile = CandidateProfile.model_validate(cached_profile_dict)
        return {"candidate_profile": candidate_profile}
        
    # 3. Cache MISS: Parse PDF via LLM
    print("⚡ [Parser Cache MISS] New or updated PDF detected! Parsing via LLM...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(CandidateProfile)
    
    prompt = f"""
    You are an expert Resume Parsing System. 
    Analyze the following raw resume text and extract all details into the required structured schema.
    Ensure all work experiences, projects, technical skills, metrics, and education entries are captured accurately.

    RAW RESUME TEXT:
    ---
    {raw_text}
    ---
    """
    
    candidate_profile: CandidateProfile = structured_llm.invoke(prompt)
    
    # 4. Save to Cache
    save_resume_profile_cache(pdf_hash, candidate_profile.model_dump())
    print(f"✅ [Parser Agent] Successfully parsed & cached profile for: {candidate_profile.full_name}")
    
    return {
        "candidate_profile": candidate_profile
    }
