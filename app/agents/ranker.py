import re
import os
from typing import Dict, Any, List, Set, Tuple
from app.schemas.models import CandidateProfile, UnifiedJobListing
from app.graph.state import AgentState

def extract_required_yoe(jd_text: str) -> int:
    """
    Extracts the minimum years of experience required from JD text using regex.
    Matches patterns like '3+ years', '3-5 YOE', '3 yrs', 'minimum 2 years'.
    Returns 0 if no explicit multi-year experience requirement is found.
    """
    jd_lower = jd_text.lower()
    matches = re.findall(r'\b([2-9]|1[0-5])\+?\s*(?:-\s*\d+\s*)?(?:years|yoe|yrs|yr)\b', jd_lower)
    if matches:
        return min([int(m) for m in matches])
    return 0

def score_job_fit_python(candidate: CandidateProfile, job: UnifiedJobListing) -> Tuple[float, List[str]]:
    """
    Production-Grade Dynamic ATS Match Scorer.
    Enforces DYNAMIC HARD DISQUALIFICATION PENALTIES based on candidate's parsed profile JSON.
    Works for ANY Candidate Level & Location (India/NCR vs US/Global).
    """
    if not candidate or not candidate.skills:
        return 50.0, []
        
    jd_text_lower = job.raw_jd.lower()
    title_lower = job.title.lower()
    loc_lower = (job.location + " " + job.raw_jd[:400]).lower()
    
    candidate_yoe = candidate.years_of_experience if candidate else 0
    candidate_loc = candidate.location.lower() if candidate and candidate.location else "india"
    
    # -----------------------------------------------------------------
    # HARD DISQUALIFIER 1: Foreign Location Mismatch (US/UK/EU vs India Target)
    # -----------------------------------------------------------------
    is_india_candidate = any(i in candidate_loc for i in ["india", "gurugram", "noida", "delhi", "haryana"])
    if is_india_candidate:
        us_foreign_indicators = ["united states", "usa", "utah", "new york", "san francisco", "california", "texas", "us remote", "uk remote", "europe"]
        if any(f in loc_lower for f in us_foreign_indicators):
            if not any(in_loc in loc_lower for in_loc in ["india", "gurugram", "noida", "delhi", "worldwide", "global remote"]):
                return 0.0, ["US/Foreign Location Mismatch (US Work Auth Required)"]

    # -----------------------------------------------------------------
    # HARD DISQUALIFIER 2: Experience Gap (Based on Candidate's Parsed YOE)
    # -----------------------------------------------------------------
    required_yoe = extract_required_yoe(job.raw_jd)
    if required_yoe > (candidate_yoe + 1):
        return 0.0, [f"Requires {required_yoe}+ Years Experience (Candidate has {candidate_yoe} YOE)"]
        
    # -----------------------------------------------------------------
    # HARD DISQUALIFIER 3: Senior Title Mismatch for Freshers/Juniors
    # -----------------------------------------------------------------
    if candidate_yoe <= 1:
        senior_titles = ["senior", "sr.", "lead", "principal", "staff", "manager", "director", "head", "architect", "vp"]
        if any(t in title_lower for t in senior_titles):
            return 0.0, ["Senior/Lead Title Mismatch"]

    # -----------------------------------------------------------------
    # HARD DISQUALIFIER 4: Unpaid / Training Fee / Exploitative Jobs
    # -----------------------------------------------------------------
    unpaid_terms = ["unpaid", "training fee", "pay to work", "0 stipend", "no stipend"]
    if any(u in jd_text_lower for u in unpaid_terms):
        return 0.0, ["Unpaid/Training Fee Job"]

    # -----------------------------------------------------------------
    # HARD DISQUALIFIER 5: Expired / Old Job Listings (2024 / 6+ Months Ago)
    # -----------------------------------------------------------------
    posted_text = (job.date_posted + " " + job.raw_jd[:200]).lower()
    if any(old in posted_text for old in ["2024", "2023", "6 months ago", "9 months ago", "1 year ago", "30+ days ago"]):
        return 0.0, ["Expired / Old Job Listing (Posted > 30 Days Ago)"]

    # -----------------------------------------------------------------
    # SCORING ENGINE (Skill Overlap + Target Location Match)
    # -----------------------------------------------------------------
    candidate_skills = [s.strip() for s in candidate.skills if s.strip()]
    matched_skills = [skill for skill in candidate_skills if skill.lower() in jd_text_lower]
    missing_skills = [skill for skill in candidate_skills if skill.lower() not in jd_text_lower]
    
    skill_match_ratio = len(matched_skills) / len(candidate_skills) if candidate_skills else 0.0
    skill_score = skill_match_ratio * 100.0
    
    # Target Location Fit Score (30% Weight)
    location_score = 50.0
    if any(loc in loc_lower for loc in ["gurugram", "noida", "delhi", "ncr"]):
        location_score = 100.0
    elif any(loc in loc_lower for loc in ["india", "remote"]):
        location_score = 80.0
        
    # Final Weighted Formula: 70% Skill Overlap + 30% Location Match
    final_score = (0.70 * skill_score) + (0.30 * location_score)
    
    return round(final_score, 1), missing_skills[:5]

def export_ranked_jobs_to_markdown(candidate: CandidateProfile, ranked_jobs: List[UnifiedJobListing], report_path: str):
    """Exports full ATS-ranked job feed to a clean Markdown report."""
    from datetime import datetime
    
    qualified_jobs = [j for j in ranked_jobs if j.ats_score > 0.0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cand_name = candidate.full_name if candidate else 'Candidate'
    
    md = f"# 📊 CAREEROS ATS RANKED JOB FEED REPORT\n"
    md += f"**Generated On**: {timestamp}  \n"
    md += f"**Candidate Name**: {cand_name}  \n"
    md += f"**Total Jobs Scanned**: {len(ranked_jobs)} | **Qualified Fresher Jobs**: **{len(qualified_jobs)}**\n\n"
    md += "---\n\n## 🏆 Qualified ATS Sorted Jobs Feed (Highest Match to Lowest)\n\n"
    
    for idx, job in enumerate(qualified_jobs, 1):
        missing_str = ", ".join(job.missing_skills) if job.missing_skills else "None"
        jd_snippet = job.raw_jd[:300].replace("\n", " ")
        
        md += f"### [{idx}] ATS Match Score: {job.ats_score}% | {job.company} - {job.title}\n"
        md += f"* **Source Platform**: `{job.source_platform}`\n"
        md += f"* **Location**: {job.location}\n"
        md += f"* **Salary / Stipend**: {job.salary_range}\n"
        md += f"* **Missing Skills**: `{missing_str}`\n"
        md += f"* **Apply Link**: [Click Here to Apply]({job.apply_url})\n"
        md += f"* **Job Description Snippet**:\n  > {jd_snippet}...\n\n---\n"
        
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

def rank_jobs_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Ranks all discovered jobs using Hard-Disqualification ATS Engine.
    0 LLM TOKENS SPENT! Execution time: <10ms for all jobs.
    """
    candidate: CandidateProfile = state.get("candidate_profile")
    discovered_jobs: List[UnifiedJobListing] = state.get("discovered_jobs", [])
    
    print(f"\n📊 [ATS Ranker Agent] Scanning & Ranking {len(discovered_jobs)} jobs with HARD Location & YOE Disqualification...")
    
    ranked_jobs: List[UnifiedJobListing] = []
    disqualified_count = 0
    
    for job in discovered_jobs:
        score, missing = score_job_fit_python(candidate, job)
        job.ats_score = score
        job.missing_skills = missing
        if score == 0.0:
            disqualified_count += 1
        ranked_jobs.append(job)
        
    # Sort descending by ATS Score
    ranked_jobs.sort(key=lambda x: x.ats_score, reverse=True)
    
    qualified_count = len(ranked_jobs) - disqualified_count
    print(f"✅ [ATS Ranker Agent] Ranked {len(ranked_jobs)} jobs ({qualified_count} Qualified | {disqualified_count} Disqualified).")
    if ranked_jobs and ranked_jobs[0].ats_score > 0.0:
        print(f"   🏆 #1 Qualified Match: [{ranked_jobs[0].company} - {ranked_jobs[0].title}] (ATS Score: {ranked_jobs[0].ats_score}%)")
        
    # Export full ATS report to Markdown
    from app.config.settings import settings
    report_file = os.path.join(settings.BASE_DIR, "data", "ats_ranked_jobs.md")
    export_ranked_jobs_to_markdown(candidate, ranked_jobs, report_file)
    print(f"📄 [ATS Report] Qualified ranked report saved to: file://{report_file}")
    
    return {
        "ranked_jobs": ranked_jobs
    }
