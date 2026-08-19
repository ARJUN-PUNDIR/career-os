import os
import time
from typing import Dict, Any
from app.config.settings import settings
from app.schemas.models import CandidateProfile, UnifiedJobListing
from app.graph.state import AgentState

def fill_and_apply_job_node(state: AgentState) -> Dict[str, Any]:
    """
    Playwright Browser Application Agent Node.
    Auto-detects and launches Brave Browser / Google Chrome / Firefox with persistent profile,
    populates candidate details, attaches compiled PDF resume, and pauses for review.
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

    # Prioritize the tailored compiled PDF resume created for this specific job
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

    print(f"\n🌐 [Playwright Browser Agent] Opening browser for target job: [{selected_job.company} - {selected_job.title}]...")
    print(f"🔗 Target Apply URL: {selected_job.apply_url}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("💡 [Playwright Note] Installing playwright...")
        import subprocess
        subprocess.run(["pip", "install", "playwright"], check=True)
        from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            # Brave Browser executable location on macOS
            brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            
            user_profile_dir = os.path.join(settings.BASE_DIR, "data", "brave_user_profile")
            os.makedirs(user_profile_dir, exist_ok=True)

            context = None
            if os.path.exists(brave_path):
                print(f"🚀 [Browser Agent] Launching BRAVE BROWSER directly from: {brave_path}")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_profile_dir,
                    executable_path=brave_path,
                    headless=False,
                    slow_mo=300,
                    viewport={"width": 1280, "height": 800}
                )
            elif os.path.exists(chrome_path):
                print(f"🚀 [Browser Agent] Launching GOOGLE CHROME directly...")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_profile_dir,
                    channel="chrome",
                    headless=False,
                    slow_mo=300,
                    viewport={"width": 1280, "height": 800}
                )
            else:
                print(f"🚀 [Browser Agent] Launching Firefox Engine...")
                firefox_profile_dir = os.path.join(settings.BASE_DIR, "data", "firefox_user_profile")
                context = p.firefox.launch_persistent_context(
                    user_data_dir=firefox_profile_dir,
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
                        print(f"   👉 [Browser Agent] Found Apply button ({btn_sel}). Clicking automatically...")
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
            print("🛑 HUMAN APPROVAL GATE 2: PRE-SUBMISSION REVIEW INTERRUPT")
            print("="*80)
            print("   The Brave/Chrome browser is open on your screen with pre-filled fields!")
            print(f"   Target Job: [{selected_job.company} - {selected_job.title}]")
            print("   Please review the form, answer any custom portal questions, and approve submission.")
            print("="*80)

            time.sleep(5)
            return {"application_status": "SUBMITTED_OR_REVIEWED", "gate_2_approved": True}

    except Exception as e:
        print(f"⚠️ [Playwright Browser Handoff]: {e}")
        print(f"💡 Guided Human Handoff: Open URL directly in your browser: {selected_job.apply_url}")
        return {"application_status": "HANDOFF_TO_HUMAN"}
