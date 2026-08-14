import os
from fpdf import FPDF
from app.config.settings import settings
from app.agents.parser import parse_resume_node
from app.graph.state import AgentState

def create_sample_pdf(output_path: str):
    """Generates a clean sample engineering resume PDF for testing."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Arjun Singh Pundir", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Email: arjun@example.com | Phone: +91 9876543210 | Location: Remote, India", ln=True)
    pdf.cell(0, 6, "LinkedIn: linkedin.com/in/arjunsingh | GitHub: github.com/ARJUN-PUNDIR", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "SUMMARY", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Passionate AI & Full-Stack Engineer specializing in Stateful Multi-Agent Systems, RAG pipelines, FastAPI, and LangGraph. Built enterprise-grade research and search agents with re-ranked FAISS retrieval.")
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "TECHNICAL SKILLS", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Languages & Frameworks: Python, FastAPI, LangGraph, LangChain, PyTorch, React, Next.js, SQL\nAI & Databases: FAISS, FlashRank, RAG, Ollama, OpenAI API, SQLite, PostgreSQL")
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "PROJECTS", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "Nexus AI Research Platform | LangGraph, FAISS, FlashRank, FastAPI", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "- Engineered modular multi-agent research platform featuring 2-stage hybrid RAG (FAISS + FlashRank) with <15ms re-ranking latency.\n- Developed 4-Way Intent Router and self-correcting reflection audit loop achieving 31 passed pytest assertions.")
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "EDUCATION", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "B.Tech in Computer Science & Engineering | CGPA: 8.5 | Graduating 2026", ln=True)
    
    pdf.output(output_path)
    print(f"✅ Sample Resume PDF created at: {output_path}")

if __name__ == "__main__":
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    pdf_file = os.path.join(settings.UPLOADS_DIR, "arjun_resume.pdf")
    create_sample_pdf(pdf_file)
