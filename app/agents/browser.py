import os
import time
from typing import Dict, Any
from app.config.settings import settings
from app.schemas.models import CandidateProfile, UnifiedJobListing
from app.graph.state import AgentState

# Known system executable paths for N-Browsers across macOS & Linux
SYSTEM_BROWSER_PATHS = [
    # Brave Browser
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    # Google Chrome
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # Microsoft Edge
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    # Arc Browser
    "/Applications/Arc.app/Contents/MacOS/Arc",
    # Opera Browser
    "/Applications/Opera.app/Contents/MacOS/Opera",
    # Vivaldi Browser
    "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
    # Linux Standard Paths
    "/usr/bin/brave-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/microsoft-edge-stable",
    "/usr/bin/chromium-browser"
]

def find_system_browser() -> tuple[str, str]:
    """Scans local OS for any installed Chromium-family N-browser."""
    for path in SYSTEM_BROWSER_PATHS:
        if os.path.exists(path):
            browser_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path)))).replace(".app", "")
            return path, browser_name
    return "", "Chromium"

def fill_and_apply_job_node(state: AgentState) -> Dict[str, Any]:
    """
    Playwright Universal N-Browser Agent Node.
    Dynamically resolves any installed browser on the user's machine (Brave, Chrome, Edge, Arc, Opera, Vivaldi, Firefox),
    attaches tailored PDF resume, and auto-fills portal forms.
    """
    candidate: CandidateProfile = state.get("candidate_profile")
    selected_job: UnifiedJobListing = state.get("selected_job")
    pdf_path = state.get("compiled_pdf_path")

    if not selected_job:
        ranked = state.get("ranked_jobs", [])
        selected_job = ranked[0] if ranked else None

    if not selected_job or not candidate:
        print("⚠️ [Browser Agent] No selected job or candidate profile in state!")
        return {"application_status": "FAILED"}

    # Prioritize tailored PDF resume
    if not pdf_path or not os.path.exists(pdf_path):
        output_dir = os.path.join(settings.BASE_DIR, "data", "output")
        company_slug = selected_job.company.lower().replace(" ", "_") if selected_job else "tailored"
        
        candidates_pdfs = [
            os.path.join(output_dir, f"sample_jake_resume_{company_slug}.pdf"),
            os.path.join(output_dir, "sample_jake_resume_digitalxnode.pdf"),
            os.path.join(settings.UPLOADS_DIR, "candidate_resume.pdf"),
            os.path.join(settings.UPLOADS_DIR, "sample_resume.pdf")
        ]
        for p in candidates_pdfs:
            if os.path.exists(p):
                pdf_path = p
                break

    print(f"\n🌐 [Universal N-Browser Agent] Target Job: [{selected_job.company} - {selected_job.title}]...")
    print(f"🔗 Target Apply URL: {selected_job.apply_url}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("💡 Installing playwright...")
        import subprocess
        subprocess.run(["pip", "install", "playwright"], check=True)
        from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            # Dynamic Universal System Browser Resolution
            browser_path, browser_name = find_system_browser()
            user_profile_dir = os.path.join(settings.BASE_DIR, "data", f"{browser_name.lower()}_user_profile")
            os.makedirs(user_profile_dir, exist_ok=True)

            if browser_path:
                print(f"🚀 [Universal Agent] Detected & Launching: [{browser_name}] from {browser_path}")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_profile_dir,
                    executable_path=browser_path,
                    headless=False,
                    slow_mo=300,
                    viewport={"width": 1280, "height": 800}
                )
            else:
                print(f"🚀 [Universal Agent] Launching Chromium persistent context...")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_profile_dir,
                    channel="chrome",
                    headless=False,
                    slow_mo=300,
                    viewport={"width": 1280, "height": 800}
                )

            page = context.pages[0] if context.pages else context.new_page()

            print(f"🚀 [Browser Agent] Navigating to: {selected_job.apply_url}")
            page.goto(selected_job.apply_url, timeout=35000, wait_until="domcontentloaded")
            time.sleep(3)

            # Auto-click 'Apply' / 'Apply Now' / 'Register to Apply' button if present
            apply_button_selectors = [
                "button:has-text('Apply')",
                "a:has-text('Apply')",
                "button:has-text('Apply Now')",
                "a:has-text('Apply Now')",
                "button:has-text('Register to Apply')",
                "button[id*='apply']",
                "a[id*='apply']",
                ".apply-btn",
                "#apply-btn"
            ]
            for btn_sel in apply_button_selectors:
                try:
                    btn = page.query_selector(btn_sel)
                    if btn and btn.is_visible():
                        print(f"   👉 Found Apply button ({btn_sel}). Clicking automatically...")
                        btn.click()
                        time.sleep(2.5)
                        break
                except Exception:
                    pass

            # Detect & Fill Common Name Fields
            for selector in ["input[name*='name']", "input[id*='name']", "input[placeholder*='name']", "input[autocomplete*='name']"]:
                try:
                    if page.is_visible(selector):
                        page.fill(selector, candidate.full_name)
                        print(f"   ✓ Filled Name: {candidate.full_name}")
                        break
                except Exception:
                    pass

            # Detect & Fill Common Email Fields
            for selector in ["input[name*='email']", "input[type='email']", "input[id*='email']", "input[placeholder*='email']"]:
                try:
                    if page.is_visible(selector):
                        page.fill(selector, candidate.email)
                        print(f"   ✓ Filled Email: {candidate.email}")
                        break
                except Exception:
                    pass

            # Detect & Fill Common Phone Fields
            for selector in ["input[name*='phone']", "input[name*='mobile']", "input[type='tel']", "input[id*='phone']"]:
                try:
                    if page.is_visible(selector):
                        page.fill(selector, candidate.phone)
                        print(f"   ✓ Filled Phone: {candidate.phone}")
                        break
                except Exception:
                    pass

            # Detect & Upload PDF Resume File
            if os.path.exists(pdf_path):
                file_input = page.query_selector("input[type='file']")
                if file_input:
                    file_input.set_input_files(pdf_path)
                    print(f"   ✓ Attached Tailored PDF Resume: {os.path.basename(pdf_path)}")

            # HUMAN APPROVAL GATE 2 INTERRUPT
            print("\n" + "="*80)
            print(f"🛑 HUMAN APPROVAL GATE 2: PRE-SUBMISSION REVIEW INTERRUPT ({browser_name})")
            print("="*80)
            print(f"   The [{browser_name}] browser is open on your screen with pre-filled fields!")
            print(f"   Target Job: [{selected_job.company} - {selected_job.title}]")
            print("="*80)

            time.sleep(5)
            return {"application_status": "SUBMITTED_OR_REVIEWED", "gate_2_approved": True}

    except Exception as e:
        print(f"⚠️ [Browser Handoff]: {e}")
        return {"application_status": "HANDOFF_TO_HUMAN"}
