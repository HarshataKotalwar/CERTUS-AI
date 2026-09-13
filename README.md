# CERTUS AI

## Document Intelligence Platform

Upload a PDF and ask questions grounded in that document.

### Tech Stack

- Python
- FastAPI
- Vanilla HTML/CSS/JavaScript frontend
- Gemini
- ChromaDB (local)

## Run locally

```bash
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/

The API (`/upload`, `/chat`, `/health`) and the frontend are served by the same FastAPI app.

Uploaded files and vector data are stored locally in `data/` and `chroma_db/`. On a typical free hosting service those directories are ephemeral, so documents may need to be re-uploaded after a restart or sleep.

## Status

🚧 Under Development
