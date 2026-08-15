from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class WorkExperience(BaseModel):
    title: str = Field(description="Job title, e.g., AI Developer")
    company: str = Field(description="Company name")
    location: Optional[str] = Field(default="Remote", description="Job location")
    start_date: Optional[str] = Field(default="", description="Start date, e.g., Jan 2024")
    end_date: Optional[str] = Field(default="Present", description="End date or Present")
    bullet_points: List[str] = Field(description="Key achievements and bullet points")

class Project(BaseModel):
    name: str = Field(description="Project name, e.g., Nexus AI")
    technologies: List[str] = Field(description="Tech stack used, e.g., LangGraph, FAISS")
    description: str = Field(description="Short project summary")
    bullet_points: List[str] = Field(description="Detailed project feature bullet points")
    link: Optional[str] = Field(default="", description="GitHub or live URL")

class Education(BaseModel):
    degree: str = Field(description="Degree name, e.g., B.Tech in Computer Science")
    institution: str = Field(description="University or college name")
    graduation_year: str = Field(description="Year of completion, e.g., 2025")
    cgpa_or_percentage: Optional[str] = Field(default="", description="CGPA or grade")

class CandidateProfile(BaseModel):
    full_name: str = Field(description="Full name of candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    location: str = Field(description="Current city/country")
    years_of_experience: int = Field(default=0, description="Total years of professional experience (0 for fresher/interns)")
    experience_level: str = Field(default="Fresher", description="Candidate level: Fresher, Junior (1-2 YOE), Mid-Level (3-5 YOE), Senior (5+ YOE)")
    linkedin_url: Optional[str] = Field(default="", description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default="", description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default="", description="Personal website portfolio URL")
    summary: str = Field(description="Professional summary statement")
    skills: List[str] = Field(description="List of technical skills and frameworks")
    experiences: List[WorkExperience] = Field(description="List of work experience entries")
    projects: List[Project] = Field(description="List of key technical projects")
    education: List[Education] = Field(description="List of educational qualifications")

class JobRequirementsInput(BaseModel):
    target_role: str = Field(description="Target role, e.g., GenAI Engineer / AI Intern")
    target_locations: List[str] = Field(default_factory=lambda: ["Remote", "India"], description="Target cities or remote")
    min_stipend_lpa: Optional[str] = Field(default="15+ LPA", description="Target stipend or salary range")
    days_posted: int = Field(default=10, description="Fetch jobs posted within last N days")

class UnifiedJobListing(BaseModel):
    job_id: str = Field(description="Unique hash ID of the job listing")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    source_platform: str = Field(description="Source platform, e.g., LinkedIn, Greenhouse, Lever, Indeed")
    location: str = Field(description="Location or Remote status")
    date_posted: str = Field(default="", description="Date or timeframe posted")
    raw_jd: str = Field(description="Full Job Description text")
    apply_url: str = Field(description="Direct apply URL")
    salary_range: Optional[str] = Field(default="Not specified", description="Salary or stipend details if listed")
    ats_score: Optional[float] = Field(default=0.0, description="Calculated ATS fit score (0-100%)")
    missing_skills: List[str] = Field(default_factory=list, description="Key skills present in JD but missing in profile")

class AuditResult(BaseModel):
    passed: bool = Field(description="True if audit passed all 6 checks")
    metrics_preserved: bool = Field(description="True if numbers/metrics were strictly preserved")
    length_valid: bool = Field(description="True if bullet character length is within +-10%")
    anti_hallucination_passed: bool = Field(description="True if no fake skills/companies were added")
    matched_keywords: List[str] = Field(description="List of JD keywords successfully aligned")
    audit_report: str = Field(description="Detailed human-readable audit status summary")

class TailoredProfile(BaseModel):
    candidate_profile: CandidateProfile
    target_job: UnifiedJobListing
    tailored_experiences: List[WorkExperience]
    tailored_projects: List[Project]
    audit_result: AuditResult
    compiled_pdf_path: Optional[str] = Field(default="", description="Path to generated ATS PDF")
    cover_letter_text: Optional[str] = Field(default="", description="Generated cover letter content")

class ApplicationStatusEnum(str, Enum):
    DISCOVERED = "DISCOVERED"
    RANKED = "RANKED"
    APPROVED_BY_USER = "APPROVED_BY_USER"
    TAILORED = "TAILORED"
    AUDITED = "AUDITED"
    APPLIED_SUCCESS = "APPLIED_SUCCESS"
    HANDOFF_REQUIRED = "HANDOFF_REQUIRED"
    REJECTED = "REJECTED"
    INTERVIEW_INVITE = "INTERVIEW_INVITE"
