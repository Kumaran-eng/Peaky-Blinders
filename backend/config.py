import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "DocTrust AI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").strip().lower() == "true"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

# The admin password is deliberately server-only: never expose it in JavaScript.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_COOKIE_SECURE = os.getenv("ADMIN_COOKIE_SECURE", "false").strip().lower() == "true"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./doctrust.db")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def project_path(value: str) -> str:
    """Resolve relative application paths from the project root."""
    path = Path(value)
    return str(path if path.is_absolute() else PROJECT_ROOT / path)


UPLOAD_DIR = project_path(os.getenv("UPLOAD_DIR", "data/uploads"))
PROCESSED_DIR = project_path(os.getenv("PROCESSED_DIR", "data/processed"))
VECTOR_DB_DIR = project_path(os.getenv("VECTOR_DB_DIR", "vector_db"))
