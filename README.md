# 🤖 CAREEROS: AUTONOMOUS MULTI-AGENT ATS RESUME & JOB APPLICATION PLATFORM

> **A modular multi-agent job application orchestrator built with LangGraph, NVIDIA Nemotron-3 LLM, Playwright, and RapidAPI Hub. It combines 3-pillar universal job search, 0-token deterministic ATS ranking, dedicated Jobscan gap analytics, surgical LaTeX keyword infusion (Jake's Resume layout), single-page PDF compilation, and automated browser form submissions with human-in-the-loop review gates.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Workflows-FF6F61?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/langgraph)
[![NVIDIA Nemotron](https://img.shields.io/badge/LLM-NVIDIA_Nemotron--3-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![RapidAPI Hub](https://img.shields.io/badge/RapidAPI-API_Hub-0055FF?style=for-the-badge&logo=rapidapi&logoColor=white)](https://rapidapi.com/)
[![SQLite3](https://img.shields.io/badge/SQLite3-MD5_Cache-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 🌟 Core Engineering Achievements

### 1. 🌐 3-Pillar Universal Job Search Architecture
Aggregates live job postings across 3 distinct search pillars with SQLite deduplication:
- **Pillar 1 (JSearch API `/search-v2`)**: Targeted API queries filtered with `date_posted: week` and rate-limit controls via RapidAPI Hub.
- **Pillar 2 (SerpAPI Google Indexing)**: Direct company ATS application pages (`boards.greenhouse.io`, `jobs.lever.co`, `ashbyhq.com`) with `tbs: qdr:m` recency filters.
- **Pillar 3 (Firecrawl Web Scraper)**: Full raw Job Description extraction directly from company career portals.

### 2. 🤖 Fully Automated Job Application Submission (Playwright Engine)
- Launches Playwright (Firefox Engine) with **0 profile lock conflicts**.
- Automatically navigates to the target apply URL, auto-detects form fields (*Name, Email, Phone, LinkedIn, GitHub*), and attaches your compiled **single-page ATS-tailored PDF resume**.
- Includes **Guided Human Handoff** and **Pre-Submission Review Interrupt (Gate 2)** for 100% application accuracy.

### 3. 🎨 NVIDIA Nemotron LLM Surgical LaTeX Architect (Jake's Resume Layout)
- Utilizes the gold-standard **Jake Gutierrez Overleaf LaTeX Template (`jakegut/resume`)**.
- Performs **Surgical Keyword Infusion**: Weaves missing ATS keywords (*LlamaIndex, REST APIs, Git/GitHub, OpenAI APIs*) into project bullet points and technical skills without fabricating fake experience or altering real dates/degrees.
- **0 Structural Breakage**: Preserves all custom LaTeX macros (`\resumeSubheading`, `\resumeProjectHeading`), margins, and single-page ATS layout formatting.

### 4. ⚡ $0-Token Smart MD5 Hash Resume Caching (< 1ms Execution)
- Computes an **MD5 cryptographic checksum** of candidate resume PDFs.
- Bypasses LLM re-parsing completely on unchanged resume uploads, retrieving structured candidate profiles instantly from SQLite DB in **< 1ms with 0 token consumption**.

### 5. 📊 100% Pure Python ATS Ranking & Hard Disqualification Engine (< 10ms)
Executes deterministic hard disqualification rules **before** LLM invocation (0 LLM tokens, < 10ms speed):
- **YOE Gap Filtering**: Disqualifies roles requiring 2+ YOE for fresher candidates (`candidate_yoe <= 1`).
- **Seniority Filtering**: Disqualifies `Senior`, `Lead`, `Manager`, `Staff`, `Principal` titles.
- **Geographic Filtering**: Disqualifies foreign locations for India-based candidates unless global/worldwide remote is specified.
- **Recency Filtering**: Purges old or expired postings (>30 days).

### 6. 🛑 Dual Human-in-the-Loop Approval Interrupt Gates
- **Gate 1 (Job Selection)**: Interactive terminal menu to select 1 target job from the ATS-sorted qualified feed.
- **Gate 2 (Pre-Submission Form Review)**: Playwright pauses live on screen with pre-filled fields and attached single-page PDF resume before submitting.

### 7. 🌐 Dedicated Jobscan ATS Scanner API Integration
- Connects directly to dedicated external ATS match scoring APIs on RapidAPI Hub (`AI Resume Screener & ATS Scorer API`).
- Extracts match score percentages (0-100%), matched hard/soft skills, missing keywords, and recruiter recommendations.

### 8. 🔀 Centralized Multi-Provider Model Factory & SQLite Tracking
- Configurable model factory supporting **NVIDIA Nemotron-3 LLM (NIM API)**, **OpenAI**, and **Local Ollama**.
- Maintains stateful application tracking and deduplication using SQLite (`data/career_os.db`).

---

## 🧠 Master System Architecture & Visual Flowchart

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CAREEROS AGENTIC ENGINE PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 0] USER TARGET PREFERENCES                                                               │
│ • Prompts Role, Preferred Locations (Remote, Gurugram, Delhi), Stipend Target                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 1] RESUME PARSER AGENT ($0-Token MD5 SQLite Cache)                                       │
│ • Computes MD5 Cryptographic Checksum of Uploaded PDF Resume                                    │
│ • Cache HIT -> Loads Profile from SQLite in <1ms (0 LLM Tokens Spent!)                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 2] CAREER STRATEGY PLANNER AGENT (NVIDIA Nemotron LLM)                                  │
│ • Formulates 3-Pillar Search Strategy & Platform-Agnostic Query Sets                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 3] 3-PILLAR MULTI-AGENT JOB SEARCH ENGINES                                               │
│ ├── Pillar 1: JSearch API (/search-v2, date_posted: week via RapidAPI Hub)                       │
│ ├── Pillar 2: SerpAPI Google ATS Indexing (boards.greenhouse.io, jobs.lever.co, ashbyhq.com)    │
│ └── Pillar 3: Firecrawl Web Scraper (Full Raw JD Content Extraction)                            │
│ └── SQLite Deduplication Engine (Preserves Unique Job ID Records in data/career_os.db)          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 4] ATS MULTI-FACTOR RANKING ENGINE (<10ms, 0 Tokens)                                     │
│ • Enforces Hard YOE Disqualifier (disqualifies 2+ YOE for candidates <= 1 YOE)                   │
│ • Enforces Senior Title Disqualifier (purges Senior, Lead, Manager, Staff, Principal)           │
│ • Enforces Geographic Disqualifier (purges US/Foreign roles for India candidates)               │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛑 [STAGE 5] HUMAN APPROVAL GATE 1 INTERRUPT                                                    │
│ • Displays Sorted ATS Qualified Jobs Feed (1 to N)                                              │
│ • Prompts Candidate: "Select Job Number [1 - N] to Target for Resume Tailoring"                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 6] DEDICATED ATS SCANNER API (RapidAPI Hub)                                              │
│ • Evaluates Resume vs Target JD -> Returns Match Score %, Missing Hard & Soft Keywords          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 7] NVIDIA NEMOTRON LLM SURGICAL LATEX ARCHITECT                                          │
│ • Uses Master Jake's Resume Overleaf Base Code (jakegut/resume)                                 │
│ • Weaves Missing ATS Keywords into Technical Skills & Project Bullet Points                     │
│ • 100% Fact Preservation (Zero Hallucination of Dates, Degrees, or Companies)                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 8] SINGLE-PAGE PDF RESUME COMPILER                                                       │
│ • Compiles arjun_master_jake_resume_<company>.tex -> Single-Page PDF Resume                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 9] PLAYWRIGHT BROWSER APPLICATION AGENT (Firefox Engine)                                 │
│ • Launches Firefox Persistent Profile (Zero Profile Locks & Saved Logins)                       │
│ • Navigates to Target Apply URL -> Auto-clicks 'Apply / Register' Button                        │
│ • Auto-fills Name, Email, Phone -> Attaches Tailored Single-Page PDF Resume                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛑 [STAGE 10] HUMAN APPROVAL GATE 2 INTERRUPT                                                   │
│ • Pre-Submission Live Review Interrupt on Screen before final submission                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎉 COMPLETE AUTONOMOUS APPLICATION CYCLE                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 3-Pillar Search & Intent Execution Matrix

| Search Pillar | Description | Target Platforms | API / Protocol Engine | Storage & Deduplication |
|---|---|---|---|---|
| 🌐 **`Pillar 1`** | Live job API search filtered by recency (`date_posted: week`) | RapidAPI JSearch (`/search-v2`) | Dedicated REST API Client | SQLite DB (`data/career_os.db`) |
| 🔍 **`Pillar 2`** | Google ATS Indexing (`tbs: qdr:m`) targeting direct ATS portals | `boards.greenhouse.io`, `jobs.lever.co`, `ashbyhq.com` | SerpAPI Google Search Engine | SQLite DB (`data/career_os.db`) |
| 📚 **`Pillar 3`** | Full raw Job Description web extraction | Direct Company Career Portals | Firecrawl Scraper | SQLite DB (`data/career_os.db`) |

---

## 📁 Domain-Grouped Directory Structure

```text
career-os/
├── app/
│   ├── agents/              # 📁 Autonomous Agent Workflow Nodes
│   │   ├── parser.py        # Resume Parser Agent ($0-Token MD5 SQLite Cache)
│   │   ├── planner.py       # Career Strategy Planner Agent (NVIDIA Nemotron LLM)
│   │   ├── searcher.py      # 3-Pillar Universal Job Search Engine Node
│   │   ├── ranker.py        # Deterministic ATS Multi-Factor Ranking Engine Node
│   │   ├── latex_agent.py   # NVIDIA Nemotron LLM Surgical LaTeX Architect Agent
│   │   ├── compiler.py      # Single-Page PDF Resume Compiler Agent Node
│   │   └── browser.py       # Playwright Browser Application Agent Node
│   ├── config/              # Centralized environment settings & Model Factory
│   │   ├── settings.py      # Environment variables & directory paths
│   │   └── model_factory.py # NVIDIA Nemotron / OpenAI / Ollama Model Factory
│   ├── graph/               # 📁 LangGraph State Machine & Orchestration
│   │   ├── state.py         # AgentState TypedDict schema
│   │   └── workflow.py      # Master LangGraph edge wiring & state machine compilation
│   ├── schemas/             # Pydantic data models (CandidateProfile, UnifiedJobListing)
│   ├── services/            # Dedicated RapidAPI ATS Scanner API Client
│   ├── templates/           # 📄 Master Jake's Resume Overleaf LaTeX Base Code (jake.tex)
│   └── tracker/             # SQLite DB Tracker & MD5 Hash Deduplication Engine
├── tests/                   # 🧪 Standalone Modular Test Suite
│   ├── test_full_resume_ats_api.py # ATS Scanner API Test Runner
│   ├── test_jakes_resume_latex.py # Surgical LaTeX Architect & PDF Compiler Test
│   ├── test_browser_agent.py      # Playwright Browser Agent Test Runner
│   ├── test_playwright_visual_demo.py # Visual Playwright Demo Script
│   └── export_report.py           # SQLite DB Job Exporter to Markdown Report
├── data/                    # 🔒 100% Gitignored (SQLite DB, uploads, compiled PDFs, logs)
├── main.py                  # 🚀 Master Production Entrypoint CLI
├── LICENSE                  # 📜 MIT License Legal Document
├── .env.example             # Environment configuration template
├── .gitignore               # Privacy & data protection ignore rules
└── requirements.txt         # Project dependencies
```

---

## 🚀 Quickstart & Setup Guide

### 1. Environment Setup (`.env`)
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/ARJUN-PUNDIR/career-os.git
cd career-os

python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
playwright install firefox
```

### 2. Configure API Credentials in `.env`
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

```env
# NVIDIA Nemotron-3 LLM Engine
NVIDIA_API_KEY=nvapi-your-nvidia-api-key-here

# RapidAPI Hub Key (JSearch & ATS Matcher API)
RAPIDAPI_KEY=your_rapidapi_key_here

# SerpAPI Google ATS Search
SERPAPI_KEY=your_serpapi_key_here

# Firecrawl Web Scraper
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 3. Run Master Production Pipeline
```bash
python main.py
```

### 4. Run Standalone Test Runners
```bash
# Test Dedicated ATS Scanner API
python tests/test_full_resume_ats_api.py

# Test Surgical LaTeX Architect & PDF Compiler
python tests/test_jakes_resume_latex.py

# Test Playwright Browser Application Agent
python tests/test_browser_agent.py

# Export SQLite Jobs DB to Markdown Report
python tests/export_report.py
```

---

## 🧪 Running Unit Tests

Run the standalone modular test suite inside `tests/`:
```bash
python tests/test_browser_agent.py
```

```text
=====================================================================================
🎉 REAL DEMO: PLAYWRIGHT BROWSER AGENT COMPLETE!
   Attached Resume PDF: arjun_master_jake_resume_digitalxnode.pdf
   Application Status:  SUBMITTED_OR_REVIEWED
=====================================================================================
```

---

## 📜 License & Copyright

```text
MIT License

Copyright (c) 2026 Arjun Singh Pundir

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

### 💡 Designed & Engineered with ❤️ by **Arjun Singh Pundir**

*Crafted with precision using [LangGraph](https://www.langchain.com/langgraph), [NVIDIA Nemotron LLM](https://build.nvidia.com/), [Playwright](https://playwright.dev/), [RapidAPI Hub](https://rapidapi.com/), and [Jake's Resume Overleaf Engine](https://github.com/jakegut/resume).*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com)

*“Empowering candidate applications with autonomous multi-agent pipelines, zero-token caching, and surgical precision.”*

</div>
