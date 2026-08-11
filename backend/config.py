import os
from dotenv import load_dotenv

load_dotenv()

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PAPERS_DIR = os.path.join(DATA_DIR, "papers")
VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstore")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")

# Ensure all structural data directories exist locally
os.makedirs(PAPERS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# LLM Configuration (Using Groq Free Tier)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("CRITICAL: GROQ_API_KEY is missing from environment setup.")

# Configuration models
LLM_MODEL = "openai/gpt-oss-120b"  # Free high-context model on Groq
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # Free local HuggingFace embedding (optional)