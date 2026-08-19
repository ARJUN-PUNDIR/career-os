# 🤖 CareerOS: Multi-Agent Job Search & Application Platform

> **An automated job discovery, resume tailoring, and application platform built with LangGraph, NVIDIA Nemotron-3 LLM, Playwright, and RapidAPI. CareerOS automates repetitive hiring tasks while keeping the candidate in control through explicit approval checkpoints.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Workflows-FF6F61?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/langgraph)
[![NVIDIA Nemotron](https://img.shields.io/badge/LLM-NVIDIA_Nemotron--3-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![RapidAPI](https://img.shields.io/badge/RapidAPI-API_Hub-0055FF?style=for-the-badge&logo=rapidapi&logoColor=white)](https://rapidapi.com/)
[![SQLite3](https://img.shields.io/badge/SQLite3-Persistence-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 🎯 Problem & Purpose

Current hiring workflows are highly fragmented. Candidates spend hours manually searching across disparate job portals, repeatedly tweaking resume keywords for individual postings, and filling out repetitive web application forms.

**CareerOS** automates these repetitive workflows — aggregating live listings across multiple sources, analyzing keyword gaps, formatting LaTeX resumes, and pre-filling portal forms — while keeping the candidate in full control through explicit human-in-the-loop checkpoints.

---

## 🛠️ Tech Stack & Capabilities

| Domain | Technology / Framework | Implementation Details |
| :--- | :--- | :--- |
| **Agent Orchestration** | `LangGraph`, `StateGraph`, `AgentState` | Multi-agent state machine with human-in-the-loop approval gates |
| **LLM Engine** | `NVIDIA Nemotron-3 LLM` (`NIM API`) | Career strategy planning & context-aware LaTeX keyword infusion |
| **API Integration** | `RapidAPI` (`JSearch API`, `ATS Scorer API`) | REST endpoints for live job discovery & heuristic keyword gap analysis |
| **Browser Automation** | `Playwright` (Firefox Engine) | Automates supported application flows & hands control back when manual interaction is needed |
| **Multi-Source Search** | `JSearch API`, `SerpAPI`, `Firecrawl` | Aggregates listings across job boards & direct company ATS portals |
| **Resume Engine** | `LaTeX Compiler`, `pdfplumber` | Single-page PDF generation (Default: Jake's Resume, supports custom templates) |
| **Storage & Caching** | `SQLite3`, `MD5 Hashing` | Resume hash caching for deduplication & stateful application tracking |

---

## 🌟 Core System Capabilities

### 1. 🌐 Multi-Source Job Discovery Engine
Aggregates live job postings across 3 complementary search sources with SQLite deduplication:
- **Pillar 1 (JSearch API)**: Job board API search filtered by recent posting dates (`date_posted: week`).
- **Pillar 2 (SerpAPI Google Indexing)**: Indexes direct ATS portals (`boards.greenhouse.io`, `jobs.lever.co`, `ashbyhq.com`).
- **Pillar 3 (Firecrawl Web Reader)**: Extracts job description text directly from target career pages.

### 2. 🤖 Browser-Based Application Automation (Playwright Engine)
- Automates supported application flows by detecting common form inputs (*Name, Email, Phone, LinkedIn, GitHub*) and attaching the tailored PDF resume.
- Gracefully hands control back to the user when manual interaction (CAPTCHA, OTP, custom assessments) is required.

### 3. 🎨 LLM-Assisted LaTeX Resume Architect
- **Default Template**: Supports *Jake's Resume* layout with extensibility for custom LaTeX templates.
- **Keyword Alignment**: Weaves missing ATS keywords into technical skills and project descriptions based on target job requirements.
- **Fact Verification**: Reflection-based verification prevents unsupported additions before generating the final resume.

### 4. ⚡ Resume Hash Caching
- Computes an MD5 checksum of uploaded resume PDFs.
- Reuses parsed profile structures on unchanged uploads, skipping unnecessary LLM re-parsing calls.

### 5. 📊 Deterministic ATS Ranking Engine
Applies rule-based heuristic scoring combined with keyword analysis to filter and order listings before candidate review:
- **Experience Filtering**: Filters roles requiring higher YOE thresholds than the candidate's profile.
- **Title Filtering**: Filters senior, lead, or managerial titles for entry-level preferences.
- **Geographic Filtering**: Filters non-matching location requirements based on user preferences.

### 6. 🛑 Human-in-the-Loop Checkpoints
- **Checkpoint 1 (Job Selection)**: Candidate manually inspects the ranked job feed and selects the target position.
- **Checkpoint 2 (Form Review)**: Candidate reviews the pre-filled application form in the browser before final submission.

---

## 🧠 Master System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CAREEROS AGENTIC ENGINE PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 0] USER TARGET PREFERENCES                                                               │
│ • Prompts Role, Preferred Locations, and Compensation Preferences                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 1] RESUME PARSER NODE (MD5 Hash Caching)                                                │
│ • Computes MD5 Hash Checksum of Uploaded PDF Resume                                             │
│ • Cache HIT -> Retrieves Profile from SQLite DB                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 2] CAREER STRATEGY PLANNER NODE (NVIDIA Nemotron LLM)                                   │
│ • Generates Query Sets across Multi-Source Job Channels                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 3] MULTI-SOURCE JOB DISCOVERY ENGINE                                                     │
│ ├── Pillar 1: JSearch API (Job Board Search)                                                    │
│ ├── Pillar 2: SerpAPI Google Indexing (Greenhouse, Lever, Ashby ATS Portals)                   │
│ └── Pillar 3: Firecrawl Web Reader (Direct Job Description Extraction)                         │
│ └── SQLite Deduplication Engine (Deduplicates Postings in data/career_os.db)                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 4] DETERMINISTIC ATS RANKING ENGINE                                                      │
│ • Applies Rule-Based Experience, Title, and Location Filters                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛑 [STAGE 5] HUMAN CHECKPOINT 1: JOB SELECTION                                                  │
│ • Candidate Reviews Ranked Feed & Selects Target Position                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 6] ATS SCANNER API                                                                       │
│ • Compares Resume vs Job Description -> Returns Keyword Analysis & Gap Report                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 7] LATEX RESUME ARCHITECT (NVIDIA Nemotron LLM)                                          │
│ • Infuses Keywords into Selected Template (Default: Jake's Resume)                              │
│ • Applies Reflection-Based Verification to Prevent Unsupported Additions                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 8] PDF RESUME COMPILER                                                                   │
│ • Compiles LaTeX Source -> Generates Tailored Single-Page PDF Resume                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [STAGE 9] BROWSER APPLICATION AGENT (Playwright Engine)                                         │
│ • Navigates to Target Portal -> Auto-Fills Standard Fields & Attaches Tailored PDF Resume       │
│ • Gracefully Hands Control Back when Manual Interaction is Required                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛑 [STAGE 10] HUMAN CHECKPOINT 2: FORM REVIEW                                                   │
│ • Candidate Reviews Pre-Filled Form in Browser prior to final submission                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎉 PIPELINE COMPLETE                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```text
career-os/
├── app/
│   ├── agents/              # Autonomous Agent Workflow Nodes
│   │   ├── parser.py        # Resume Parser Node (MD5 Hash Caching)
│   │   ├── planner.py       # Career Strategy Planner Node
│   │   ├── searcher.py      # Multi-Source Job Discovery Node
│   │   ├── ranker.py        # Deterministic ATS Ranking Engine Node
│   │   ├── latex_agent.py   # LaTeX Resume Architect Node
│   │   ├── compiler.py      # Single-Page PDF Resume Compiler Node
│   │   └── browser.py       # Playwright Browser Application Agent Node
│   ├── config/              # Centralized Environment Settings & Model Factory
│   │   ├── settings.py      # Environment variables & paths
│   │   └── model_factory.py # Model Factory (NVIDIA Nemotron / OpenAI / Ollama)
│   ├── graph/               # LangGraph State Machine & Orchestration
│   │   ├── state.py         # AgentState TypedDict schema
│   │   └── workflow.py      # LangGraph state machine compilation
│   ├── schemas/             # Pydantic data models (CandidateProfile, UnifiedJobListing)
│   ├── services/            # ATS Scanner API Client
│   ├── templates/           # Master LaTeX Templates (jake.tex)
│   └── tracker/             # SQLite DB Tracker & Deduplication Engine
├── tests/                   # Standalone Modular Test Suite
│   ├── test_full_resume_ats_api.py
│   ├── test_jakes_resume_latex.py
│   ├── test_browser_agent.py
│   ├── test_playwright_visual_demo.py
│   └── export_report.py
├── data/                    # 🔒 Gitignored (SQLite DB, uploads, compiled PDFs, logs)
├── main.py                  # Master Production Entrypoint CLI
├── LICENSE                  # MIT License
├── .env.example             # Environment configuration template
├── .gitignore               # Ignore rules
└── requirements.txt         # Project dependencies
```

---

## 🚀 Quickstart & Setup

### 1. Environment Setup
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/ARJUN-PUNDIR/career-os.git
cd career-os

python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
playwright install firefox
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and configure credentials:
```bash
cp .env.example .env
```

```env
NVIDIA_API_KEY=your_nvidia_nemotron_api_key
RAPIDAPI_KEY=your_rapidapi_key
SERPAPI_KEY=your_serpapi_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

## ☁️ AWS Cloud Deployment

CareerOS includes production Docker containerization and AWS Cloud deployment support:

- **`Dockerfile`**: Containerizes Python 3.10+, Playwright Firefox, dependencies, and Streamlit UI.
- **`aws_deploy_guide.md`**: Step-by-step instructions for deploying to **AWS App Runner** or **AWS ECS (Fargate)** with **AWS Secrets Manager (AES-256 Encryption)**.

### Run Web Dashboard Locally
```bash
streamlit run app/ui/dashboard.py
```

### Build & Run Docker Container
```bash
docker build -t career-os .
docker run -p 8501:8501 --env-file .env career-os
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

### 💡 Designed & Engineered by **Arjun Singh Pundir**

*Built with [LangGraph](https://www.langchain.com/langgraph), [NVIDIA Nemotron LLM](https://build.nvidia.com/), [Playwright](https://playwright.dev/), [RapidAPI](https://rapidapi.com/), and [LaTeX](https://www.latex-project.org/).*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github)

</div>
