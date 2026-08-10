from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
app = FastAPI(
    title="CERTUS AI",
    description="Multi-Agent Document Intelligence Platform",
    version="1.0.0"
)
app.include_router(upload_router)
app.include_router(chat_router)
# Home

@app.get("/")
def home():
    return {
        "project": "CERTUS AI",
        "message": "Welcome to CERTUS AI 🚀",
        "status": "Backend Running"
    }

# Health
@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "service": "Backend"
    }

# About
@app.get("/about")
def about():
    return {
        "project": "CERTUS AI",
        "developer": "Harshata Kotalwar",
        "purpose": "AI-powered Document Intelligence Platform"
    }

# Version
@app.get("/version")
def version():
    return {
        "version": "1.0.0",
        "framework": "FastAPI",
        "language": "Python"
    }
