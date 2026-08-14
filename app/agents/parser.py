import pdfplumber
import os
from typing import Dict, Any
from app.config.settings import settings
from app.config.model_factory import get_llm
from app.schemas.models import CandidateProfile
from app.graph.state import AgentState

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
    LangGraph Node: Ingests state['resume_pdf_path'], extracts text, 
    and uses LLM structured output to produce CandidateProfile JSON.
    """
    pdf_path = state.get("resume_pdf_path")
    print(f"📄 [Parser Agent] Reading resume from: {pdf_path}")
    
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
    print(f"✅ [Parser Agent] Successfully extracted profile for: {candidate_profile.full_name}")
    
    return {
        "candidate_profile": candidate_profile
    }

if __name__ == "__main__":
    # Test stub for Parser Agent
    test_pdf = os.path.join(settings.UPLOADS_DIR, "test_resume.pdf")
    if os.path.exists(test_pdf):
        state: AgentState = {"resume_pdf_path": test_pdf} # type: ignore
        result = parse_resume_node(state)
        print(result["candidate_profile"].model_dump_json(indent=2))
    else:
        print("💡 Place a test resume PDF at data/uploads/test_resume.pdf to test parsing!")
