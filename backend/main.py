from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import APP_NAME, APP_VERSION, UPLOAD_DIR, PROCESSED_DIR, VECTOR_DB_DIR
from .database import Base, engine
from . import models
from .routes import admin, chat, documents

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    description="Trusted Document-Grounded Knowledge Assistant",
    version=APP_VERSION,
)

for directory in (UPLOAD_DIR, PROCESSED_DIR, VECTOR_DB_DIR):
    Path(directory).mkdir(parents=True, exist_ok=True)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(admin.auth_router)
app.include_router(admin.router)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/chat", include_in_schema=False)
def chat_page():
    return FileResponse(FRONTEND_DIR / "chat.html")


@app.get("/admin", include_in_schema=False)
def admin_page():
    return FileResponse(FRONTEND_DIR / "admin.html")
