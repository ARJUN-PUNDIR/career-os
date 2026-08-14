import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "CareerOS"
    VERSION: str = "1.0.0"
    
    # Model Provider Config (nvidia, openai, anthropic, ollama)
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "nvidia")
    
    # API Keys
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # Ollama Config
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Model Config
    DEFAULT_MODEL: str = "gpt-4o-mini"
    FAST_MODEL: str = "gpt-4o-mini"
    STRONG_MODEL: str = "gpt-4o"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOADS_DIR: str = os.path.join(BASE_DIR, "data", "uploads")
    COMPILED_PDFS_DIR: str = os.path.join(BASE_DIR, "data", "compiled_pdfs")
    DB_PATH: str = os.path.join(BASE_DIR, "data", "career_os.db")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.COMPILED_PDFS_DIR, exist_ok=True)
