import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
from datetime import datetime
from app.config.settings import settings

def export_db_jobs_to_markdown():
    """Reads all saved jobs from SQLite DB and exports a clean Markdown report."""
    if not os.path.exists(settings.DB_PATH):
        print(f"❌ Error: SQLite DB not found at '{settings.DB_PATH}'")
        return

    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY discovered_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not rows:
        print("⚠️ No jobs found in SQLite DB!")
        return

    report_path = os.path.join(settings.BASE_DIR, "data", "job_feed_report.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# 🚀 CAREEROS MASTER JOB FEED REPORT
**Generated On**: {timestamp}  
**Total Live Jobs Discovered & Deduplicated**: **{len(rows)}**

---

## 📋 Discovered Job Feed ({len(rows)} Live Postings)

"""
    for idx, job in enumerate(rows, 1):
        md += f"""### [{idx}] {job['company']} - {job['title']}
* **Source Platform**: `{job['source_platform']}`
* **Location**: {job['location']}
* **Salary / Stipend**: {job['salary_range']}
* **Apply Link**: [Click Here to Apply]({job['apply_url']})
* **Job Description Snippet**:
  > {str(job['raw_jd'])[:300].replace('\n', ' ')}...

---
"""

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    print("\n" + "="*70)
    print(f"🎉 SUCCESS! EXPORTED ALL {len(rows)} JOBS TO MARKDOWN REPORT")
    print("="*70)
    print(f"📄 Open File: file://{report_path}")
    print("="*70 + "\n")

if __name__ == "__main__":
    export_db_jobs_to_markdown()
