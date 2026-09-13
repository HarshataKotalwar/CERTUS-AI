from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is missing. Set it in the .env file."
    )

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001"
)
CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "chroma_db"
)
CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "certus_documents"
)
CHROMA_DISTANCE_SPACE = "cosine"
UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "data"
)
MAX_PDF_SIZE_BYTES = int(
    os.getenv(
        "MAX_PDF_SIZE_BYTES",
        str(10 * 1024 * 1024)
    )
)
N_RESULTS = int(
    os.getenv(
        "N_RESULTS",
        "3"
    )
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")
    if origin.strip()
]
