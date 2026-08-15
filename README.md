# 🚀 CareerOS: Autonomous Multi-Agent ATS Resume & Job Application Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![LLM](https://img.shields.io/badge/LLM-NVIDIA%20Nemotron--3-green.svg)](https://build.nvidia.com/)
[![Automation](https://img.shields.io/badge/Browser-Playwright-red.svg)](https://playwright.dev/)
[![Template](https://img.shields.io/badge/LaTeX-Jake's%20Resume-brightgreen.svg)](https://github.com/jakegut/resume)

**CareerOS** is an autonomous, multi-agent AI engineering platform that automates the end-to-end job discovery, ATS gap analysis, surgical resume tailoring (via Jake's Resume Overleaf LaTeX engine), and automated portal form submission for software engineers and AI freshers.

---

## 🌟 Key Technical Highlights & Innovations

### 1. ⚡ $0-Token Smart MD5 Hash Resume Caching (< 1ms Execution)
- Computes an **MD5 cryptographic checksum** of candidate resume PDFs.
- Bypasses LLM re-parsing completely on unchanged resume uploads, retrieving structured candidate profiles instantly from SQLite DB in **< 1ms with 0 token consumption**.

### 2. 🌐 3-Pillar Universal Job Search Architecture
Aggregates live job postings across 3 distinct search pillars with SQLite deduplication:
- **Pillar 1 (JSearch API `/search-v2`)**: Targeted API queries filtered with `date_posted: week` and rate-limit controls.
- **Pillar 2 (SerpAPI Google Indexing)**: Scrapes direct company ATS application pages (`boards.greenhouse.io`, `jobs.lever.co`, `ashbyhq.com`) with `tbs: qdr:m` recency filters.
- **Pillar 3 (Firecrawl Web Scraper)**: Extracts raw, un-truncated Job Descriptions directly from company career portals.

### 3. 📊 100% Pure Python ATS Ranking & Hard Disqualification Engine (< 10ms)
Executes deterministic hard disqualification rules **before** LLM invocation (0 LLM tokens, < 10ms speed):
- **YOE Gap Filtering**: Disqualifies roles requiring 2+ YOE for fresher candidates (`candidate_yoe <= 1`).
- **Seniority Filtering**: Disqualifies `Senior`, `Lead`, `Manager`, `Staff`, `Principal` titles.
- **Geographic Filtering**: Disqualifies foreign locations (US/NYC/Utah) for India-based candidates unless global/worldwide remote is specified.
- **Recency Filtering**: Purges old or expired postings.

### 4. 🎨 NVIDIA Nemotron LLM Surgical LaTeX Architect
- Utilizes the gold-standard **Jake Gutierrez Overleaf LaTeX Template (`jakegut/resume`)**.
- Performs **Surgical Keyword Infusion**: Weaves missing ATS keywords (*LlamaIndex, REST APIs, Git/GitHub, OpenAI APIs*) into existing technical project bullet points without fabricating fake experience or altering real dates/degrees.
- Guarantees **0 Structural Breakage**: Preserves all custom LaTeX macros (`\resumeSubheading`, `\resumeProjectHeading`), margins, and document formatting.

### 5. 🛡️ Dual Human Approval Interrupt Gates
- **Gate 1 (Job Selection)**: Interactive terminal selection to pick 1 target job from the ATS-sorted qualified feed.
- **Gate 2 (Pre-Submission Form Review)**: Playwright pauses live on screen with pre-filled fields and attached single-page PDF resume before submitting.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Start([User Request / Preferences]) --> Parser[1. Resume Parser Node<br/>$0-Token MD5 SQLite Cache]
    
    Parser --> Planner[2. Career Strategy Planner Node<br/>NVIDIA Nemotron LLM]
    
    Planner --> Searcher[3. 3-Pillar Search Engine Node<br/>JSearch API, Google ATS Indexing, Firecrawl]
    
    Searcher --> Ranker[4. ATS Multi-Factor Ranker Node<br/>Hard Disqualifications: YOE, Location, Title]
    
    Ranker --> Gate1{5. Human Approval Gate 1<br/>Select Target Job 1 - N}
    
    Gate1 --> ATS_Scanner[6. Dedicated ATS Scanner API<br/>Match Score %, Missing Keyword Extraction]
    
    ATS_Scanner --> LaTeX_Architect[7. NVIDIA Nemotron LLM LaTeX Architect<br/>Surgical Keyword Infusion on Master jake.tex]
    
    LaTeX_Architect --> PDF_Compiler[8. Single-Page PDF Compiler<br/>Compiles arjun_master_jake_resume_company.pdf]
    
    PDF_Compiler --> Browser_Agent[9. Playwright Browser Application Agent<br/>Auto-Fills Form, Attaches PDF Resume]
    
    Browser_Agent --> Gate2{10. Human Approval Gate 2<br/>Pre-Submission Form Review & Approval}
    
    Gate2 --> END([Complete Application Cycle])
```

---

## 🛠️ Core Technology Stack

| Component | Technology / Framework | Purpose |
| :--- | :--- | :--- |
| **LLM Engine** | NVIDIA Nemotron-3 LLM | Career Strategy Planning & Surgical LaTeX Keyword Infusion |
| **Orchestration** | LangGraph / StateGraph | Executable state machine workflow with human interrupts |
| **Browser Engine** | Playwright (Firefox / Chromium) | Form detection, auto-filling, & PDF resume attachment |
| **Search Engines** | JSearch API, SerpAPI, Firecrawl | Multi-pillar job discovery & full JD extraction |
| **ATS Matcher** | RapidAPI ATS Scanner API | Real-time ATS match scoring & keyword gap reporting |
| **PDF Renderer** | Jake's Resume Overleaf LaTeX Engine | Single-page ATS-compliant PDF resume generation |
| **Database** | SQLite3 | MD5 resume caching, job deduplication, & application tracking |

---

## 📂 Project Layout

```text
career-os/
├── app/
│   ├── agents/
│   │   ├── parser.py       # Resume Parser Agent ($0-Token MD5 SQLite Cache)
│   │   ├── planner.py      # Career Strategy Planner Agent (NVIDIA Nemotron LLM)
│   │   ├── searcher.py     # 3-Pillar Job Search Engine (JSearch, Google ATS, Firecrawl)
│   │   ├── ranker.py       # Deterministic ATS Multi-Factor Ranking Engine
│   │   ├── latex_agent.py  # NVIDIA Nemotron LLM Surgical LaTeX Architect Agent
│   │   ├── compiler.py     # Single-Page PDF Resume Compiler Agent
│   │   └── browser.py      # Playwright Browser Application Agent
│   ├── config/
│   │   ├── settings.py     # Centralized Environment Configuration
│   │   └── model_factory.py # Model Factory (NVIDIA Nemotron LLM)
│   ├── graph/
│   │   ├── state.py        # Master AgentState TypedDict
│   │   └── workflow.py     # Master LangGraph Orchestration Graph
│   ├── schemas/
│   │   └── models.py       # Pydantic Data Models (CandidateProfile, UnifiedJobListing)
│   ├── services/
│   │   └── rapidapi_ats.py # Dedicated External ATS Scanner API Client
│   ├── templates/
│   │   └── jake.tex        # Master Jake's Resume Overleaf LaTeX Base Code
│   └── tracker/
│       └── db.py           # SQLite Tracker & MD5 Hash Deduplication Engine
├── tests/                  # Standalone Modular Test Runners
│   ├── test_full_resume_ats_api.py
│   ├── test_jakes_resume_latex.py
│   ├── test_browser_agent.py
│   └── export_report.py
├── data/                   # 🔒 100% Gitignored (DB, uploads, compiled PDFs, outputs)
├── main.py                 # 🚀 Master Production Entrypoint CLI
├── .gitignore              # Privacy & Data Protection Ignore Rules
├── .env.example            # Environment Variable Template
└── requirements.txt        # Production Python Dependencies
```

---

## ⚡ Getting Started

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.14)
- macOS / Linux

### 2. Environment Setup
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/ARJUN-PUNDIR/career-os.git
cd career-os

python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
playwright install firefox
```

### 3. Configure API Keys
Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
```

Set your keys inside `.env`:
```env
NVIDIA_API_KEY=your_nvidia_nemotron_api_key
RAPIDAPI_KEY=your_rapidapi_key
SERPAPI_KEY=your_serpapi_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

---

## 🚀 Usage & Execution

### Run Master Autonomous Pipeline
Execute `main.py` for full end-to-end execution:

```bash
python main.py
```

### Standalone Test Suite
Run individual module tests inside `tests/`:

```bash
# Test ATS Scanner API
python tests/test_full_resume_ats_api.py

# Test Surgical LaTeX Architect & PDF Compiler
python tests/test_jakes_resume_latex.py

# Test Playwright Browser Agent & Gate 2
python tests/test_browser_agent.py

# Export SQLite Database Jobs to Markdown Report
python tests/export_report.py
```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
