from fastapi import FastAPI

from .database import Base, engine
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DocTrust AI",
    description="Trusted Document-Grounded Knowledge Assistant",
    version="1.0.0"
)


@app.get("/")
def root():

    return {
        "message": "DocTrust AI is running"
    }