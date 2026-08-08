from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extract_pdf_text
import os
import shutil

router = APIRouter()

UPLOAD_FOLDER = "data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pdf_data = extract_pdf_text(file_path)

    return {
    "filename": file.filename,
    "pages": pdf_data["pages"],
    "characters": pdf_data["characters"],
    "message": "PDF uploaded and processed successfully!"
}