import hashlib
import requests
import json
from typing import Dict, Any, List
from app.config.settings import settings
from app.schemas.models import UnifiedJobListing
from app.graph.state import AgentState
from app.tracker.db import save_job

def generate_job_hash(company: str, title: str) -> str:
    """Generates a unique MD5 hash string for deduplicating job listings."""
    raw_str = f"{company.strip().lower()}_{title.strip().lower()}"
    return hashlib.md5(raw_str.encode("utf-8")).hexdigest()

# =====================================================================
# FUNCTION 1: PILLAR 1 + 3 (JSearch API Aggregator + Firecrawl Full Text)
# =====================================================================
def search_pillar_1_and_3(query: str) -> List[UnifiedJobListing]:
    """
    Pillar 1 + 3 Combined:
    1. Queries JSearch API (Pillar 1) for mass listings across LinkedIn/Indeed.
    2. If a description is truncated, calls Firecrawl MCP / Reader (Pillar 3) for full JD text.
    """
    print(f"🌐 [Pillar 1+3 Search] Querying JSearch API & Firecrawl for: '{query}'")
    return query_jsearch_api(query)

def query_jsearch_api(query: str) -> List[UnifiedJobListing]:
    """Pillar 1: Queries JSearch API (LinkedIn, Indeed, Glassdoor aggregator via /search-v2)."""
    import time
    if not settings.RAPIDAPI_KEY:
        print("💡 [Pillar 1+3] RAPIDAPI_KEY not set. Using sample listings for testing.")
        return get_mock_pillar_1_and_3_jobs()
        
    url = "https://jsearch.p.rapidapi.com/search-v2"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY.strip(),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    params = {
        "query": query,
        "num_pages": "1",
        "date_posted": "week"
    }
    
    results = []
    try:
        time.sleep(1.2)  # Respect RapidAPI free-tier rate limits
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            data = res_json.get("data", [])
            
            # If /search-v2 returns data as a dict containing {"jobs": [...], "cursor": "..."}, extract the jobs list!
            if isinstance(data, dict):
                data = data.get("jobs", []) or data.get("results", []) or []
                
            print(f"📡 [Pillar 1 JSearch /search-v2] Status: 200 OK | Jobs Received: {len(data)}")
            if not data:
                print(f"⚠️ [Pillar 1 JSearch] API returned 200 OK but data list was empty for query: '{query}'")
            for item in data:
                if not isinstance(item, dict):
                    print(f"⚠️ [JSearch Item Parsing] Expected dict but got {type(item)}: {item}")
                    continue
                    
                company = str(item.get("employer_name") or item.get("company_name") or item.get("company") or "Tech Company")
                title = str(item.get("job_title") or item.get("title") or "AI Role")
                raw_jd = str(item.get("job_description") or item.get("description") or "")
                apply_url = str(item.get("job_apply_link") or item.get("apply_link") or item.get("url") or "https://linkedin.com")
                
                # Check if JD is truncated (Pillar 3 Fallback)
                if len(raw_jd) < 200 and settings.FIRECRAWL_API_KEY and apply_url.startswith("http"):
                    print(f"🔥 [Pillar 3 Firecrawl] JD truncated for {company}. Reading full page URL...")
                    full_jd = fetch_firecrawl_full_jd(apply_url)
                    if full_jd:
                        raw_jd = full_jd
                        
                job_hash = generate_job_hash(company, title)
                source = str(item.get("job_publisher") or item.get("source") or "LinkedIn/Indeed")
                location = str(item.get("job_city") or item.get("job_country") or item.get("location") or "Remote")
                posted = str(item.get("job_posted_at_datetime_utc") or item.get("date_posted") or "Recently")[:10]
                salary = str(item.get("job_salary_period") or item.get("salary") or "Competitive")
                
                job = UnifiedJobListing(
                    job_id=job_hash,
                    title=title,
                    company=company,
                    source_platform=source,
                    location=location,
                    date_posted=posted,
                    raw_jd=raw_jd,
                    apply_url=apply_url,
                    salary_range=salary
                )
                results.append(job)
        else:
            print(f"❌ [Pillar 1 JSearch Error] HTTP Status Code {response.status_code}: {response.text[:150]}")
    except Exception as e:
        print(f"⚠️ [Pillar 1+3 Exception]: {e}")
        
    return results

def fetch_firecrawl_full_jd(apply_url: str) -> str:
    """Pillar 3 Engine: Calls Firecrawl API to turn full web page into clean Markdown."""
    if not settings.FIRECRAWL_API_KEY:
        return ""
    try:
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}"},
            json={"url": apply_url, "formats": ["markdown"]},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("data", {}).get("markdown", "")
    except Exception as e:
        print(f"⚠️ [Firecrawl Fetch Error]: {e}")
    return ""

# =====================================================================
# FUNCTION 2: PILLAR 2 (Google Indexing - Greenhouse/Lever/LinkedIn)
# =====================================================================
def search_pillar_2_google_indexing(query: str = "") -> List[UnifiedJobListing]:
    """
    Pillar 2: Uses SerpAPI / Google Search Engine to query indexed Greenhouse & Lever boards.
    Bypasses anti-bot restrictions using Google's whitelisted cache.
    """
    search_query = query if query else 'site:boards.greenhouse.io OR site:jobs.lever.co "AI Intern"'
    print(f"🔎 [Pillar 2 Google Indexing] Searching ATS boards: '{search_query}'")
    
    if not settings.SERPAPI_KEY:
        print("💡 [Pillar 2] SERPAPI_KEY not set. Using sample Google ATS listings for testing.")
        return get_mock_pillar_2_jobs()
        
    url = "https://serpapi.com/search"
    params = {
        "q": search_query,
        "engine": "google",
        "tbs": "qdr:m",
        "api_key": settings.SERPAPI_KEY
    }
    
    results = []
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            organic_results = response.json().get("organic_results", [])
            for item in organic_results:
                title = item.get("title", "AI Role")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                
                company = "Tech Startup"
                if "greenhouse.io/" in link:
                    parts = link.split("greenhouse.io/")
                    if len(parts) > 1:
                        company = parts[1].split("/")[0].capitalize()
                elif "lever.co/" in link:
                    parts = link.split("lever.co/")
                    if len(parts) > 1:
                        company = parts[1].split("/")[0].capitalize()
                        
                job_hash = generate_job_hash(company, title)
                job = UnifiedJobListing(
                    job_id=job_hash,
                    title=title,
                    company=company,
                    source_platform="Greenhouse/Lever (Google Index)",
                    location="Remote / NCR",
                    date_posted="Recently",
                    raw_jd=snippet,
                    apply_url=link,
                    salary_range="Competitive"
                )
                results.append(job)
    except Exception as e:
        print(f"⚠️ [Pillar 2 Error]: {e}")
        
    return results

# =====================================================================
# MOCK DATA FOR LOCAL TESTING
# =====================================================================
def get_mock_pillar_1_and_3_jobs() -> List[UnifiedJobListing]:
    sample = [
        {
            "company": "OpenAI",
            "title": "AI Engineering Intern - Agents & RAG",
            "source_platform": "LinkedIn",
            "location": "Remote",
            "raw_jd": "Looking for an AI Engineering Intern to build stateful multi-agent workflows using LangGraph, Python, FastAPI, and FAISS. Experience with 2-stage hybrid RAG retrieval and re-ranking models is highly preferred.",
            "apply_url": "https://www.linkedin.com/jobs/view/401928"
        },
        {
            "company": "Anthropic",
            "title": "Model Context Protocol (MCP) Software Intern",
            "source_platform": "Indeed",
            "location": "Remote",
            "raw_jd": "Building next-generation tool integration protocols (MCP) for Claude Desktop and enterprise LLM clients. Must be proficient in Python, TypeScript, Playwright browser automation, and API design.",
            "apply_url": "https://www.indeed.com/viewjob?jk=891023"
        }
    ]
    return [UnifiedJobListing(
        job_id=generate_job_hash(s["company"], s["title"]),
        title=s["title"], company=s["company"], source_platform=s["source_platform"],
        location=s["location"], date_posted="2026-08-12", raw_jd=s["raw_jd"], apply_url=s["apply_url"]
    ) for s in sample]

def get_mock_pillar_2_jobs() -> List[UnifiedJobListing]:
    sample = [
        {
            "company": "Cohere",
            "title": "GenAI Systems Developer",
            "source_platform": "Greenhouse (Google Index)",
            "location": "Remote / India",
            "raw_jd": "Join Cohere to optimize LLM orchestration pipelines. Required skills: Python, PyTorch, LangChain, LangGraph, FastAPI, PostgreSQL, and vector database search.",
            "apply_url": "https://boards.greenhouse.io/cohere/jobs/892014"
        }
    ]
    return [UnifiedJobListing(
        job_id=generate_job_hash(s["company"], s["title"]),
        title=s["title"], company=s["company"], source_platform=s["source_platform"],
        location=s["location"], date_posted="Recently", raw_jd=s["raw_jd"], apply_url=s["apply_url"]
    ) for s in sample]

# =====================================================================
# MAIN LANGGRAPH SEARCH NODE
# =====================================================================
def search_jobs_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Combines Function 1 (Pillar 1+3) and Function 2 (Pillar 2),
    deduplicates all job listings using SQLite MD5 hashes, and returns clean discovered_jobs.
    """
    strategy = state.get("search_strategy") or {}
    pillar_1_queries = strategy.get("pillar_1_queries") or strategy.get("search_queries") or ["AI Intern Gurugram", "GenAI Intern Remote India"]
    pillar_2_queries = strategy.get("pillar_2_queries") or ["site:boards.greenhouse.io OR site:jobs.lever.co 'AI Intern' 'Gurugram'"]
    
    reqs = state.get("user_requirements")
    role = reqs.target_role if reqs else "AI Intern"
    location = reqs.target_locations[0] if reqs and reqs.target_locations else "Gurugram"
    
    print("\n" + "="*60)
    print("🚀 [Searcher Agent] EXECUTING MULTI-PILLAR JOB SEARCH")
    print("="*60)
    
    all_discovered: List[UnifiedJobListing] = []
    seen_hashes = set()
    
    # 1. Execute Function 1: Pillar 1 + 3 (JSearch + Firecrawl Full Text) using clean plain-keyword queries
    for q in pillar_1_queries:
        pillar1_3_jobs = search_pillar_1_and_3(q)
        for job in pillar1_3_jobs:
            if job.job_id not in seen_hashes:
                seen_hashes.add(job.job_id)
                all_discovered.append(job)
                save_job(job)
                
    # 2. Execute Function 2: Pillar 2 (Google Indexing for Greenhouse/Lever) using clean ATS queries
    for p2_q in pillar_2_queries:
        pillar2_jobs = search_pillar_2_google_indexing(query=p2_q)
        for job in pillar2_jobs:
            if job.job_id not in seen_hashes:
                seen_hashes.add(job.job_id)
                all_discovered.append(job)
                save_job(job)
            
    print(f"✅ [Searcher Agent] Total Discovered & Deduplicated Jobs: {len(all_discovered)}")
    return {
        "discovered_jobs": all_discovered
    }
