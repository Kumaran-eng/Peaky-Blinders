import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

UPLOAD_DIR = "data/uploads"
PROCESSED_DIR = "data/processed"
VECTOR_DB_DIR = "vector_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 5

SIMILARITY_THRESHOLD = 0.45