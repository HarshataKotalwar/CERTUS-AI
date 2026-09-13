from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.config.settings import CORS_ORIGINS


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


app = FastAPI(
    title="CERTUS AI"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CERTUS AI"
    }

app.include_router(
    upload_router
)

app.include_router(
    chat_router
)


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend",
)
