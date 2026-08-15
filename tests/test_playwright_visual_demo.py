import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.settings import settings
from playwright.sync_api import sync_playwright

def run_visual_playwright_demo():
    print("\n" + "="*85)
    print("🚀 VISUAL WIKIPEDIA DEMO (DEDICATED PERSISTENT CHROME PROFILE)")
    print("="*85)

    with sync_playwright() as p:
        user_profile_dir = os.path.join(settings.BASE_DIR, "data", "chrome_user_profile")
        os.makedirs(user_profile_dir, exist_ok=True)

        print(f"🚀 Opening Google Chrome (Persistent Profile: file://{user_profile_dir})...")

        context = p.chromium.launch_persistent_context(
            user_data_dir=user_profile_dir,
            channel="chrome",  # Uses your real Mac Google Chrome browser!
            headless=False,
            slow_mo=300,
            viewport={"width": 1280, "height": 800}
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("\n🌐 Step 1: Navigating to Wikipedia (https://www.wikipedia.org)...")
        page.goto("https://www.wikipedia.org", wait_until="domcontentloaded")
        time.sleep(2)

        print("⌨️ Step 2: Typing 'Arjun Singh Pundir AI Engineer' into search box live...")
        search_input = page.query_selector("input#searchInput")
        if search_input:
            search_input.fill("Arjun Singh Pundir AI Engineer")
            time.sleep(1.5)
            
            print("🔘 Step 3: Clicking Search button live...")
            search_btn = page.query_selector("button[type='submit']")
            if search_btn:
                search_btn.click()
                time.sleep(3)

        print("\n" + "="*85)
        print("🎉 DEMO COMPLETE!")
        print("   Inside this Chrome browser, press ⌘ + H to see your saved history!")
        print("="*85 + "\n")
        
        input("👉 Press ENTER in terminal to close...")
        context.close()

if __name__ == "__main__":
    run_visual_playwright_demo()
