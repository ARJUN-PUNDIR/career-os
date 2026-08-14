from typing import TypedDict, List, Optional, Dict, Any
from app.schemas.models import (
    CandidateProfile,
    JobRequirementsInput,
    UnifiedJobListing,
    TailoredProfile,
    AuditResult
)

class AgentState(TypedDict):
    """Master State Dict passed across all LangGraph nodes."""
    
    # Candidate Data
    resume_pdf_path: str
    candidate_profile: Optional[CandidateProfile]
    
    # User Search Requirements
    user_requirements: Optional[JobRequirementsInput]
    search_strategy: Optional[Dict[str, Any]]
    
    # Job Search & Ranking State
    discovered_jobs: List[UnifiedJobListing]
    ranked_jobs: List[UnifiedJobListing]
    selected_job: Optional[UnifiedJobListing]
    
    # Tailoring & Audit State
    tailored_profile: Optional[TailoredProfile]
    audit_result: Optional[AuditResult]
    compiled_pdf_path: Optional[str]
    cover_letter_text: Optional[str]
    
    # Human Approval Gates
    gate_1_approved: bool  # Job selection gate
    gate_2_approved: bool  # Resume & application submission gate
    
    # Application & Tracking State
    application_status: str
    tracker_logs: List[Dict[str, Any]]
    error_message: Optional[str]
