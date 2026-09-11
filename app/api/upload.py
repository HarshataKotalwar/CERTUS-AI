from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import extract_pdf_text
from app.services.chunk_service import chunk_text
from app.services.embedding_service import create_embedding
from app.services.vector_service import add_chunks

import os
import uuid
from pathlib import Path


router = APIRouter()


# --------------------------------------------------
# UPLOAD FOLDER
# --------------------------------------------------

UPLOAD_FOLDER = "data"

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# --------------------------------------------------
# UPLOAD PDF
# --------------------------------------------------

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # CHECK FILE TYPE
    # --------------------------------------------------

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )


    # --------------------------------------------------
    # CREATE UNIQUE DOCUMENT ID
    # --------------------------------------------------

    document_id = str(
        uuid.uuid4()
    )


    # --------------------------------------------------
    # CREATE UNIQUE FILE NAME
    # --------------------------------------------------

    safe_filename = Path(file.filename or "").name

    unique_filename = (
        f"{document_id}_{safe_filename}"
    )


    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )


    # --------------------------------------------------
    # SAVE PDF
    # --------------------------------------------------

    bytes_written = 0

    try:
        with open(
            file_path,
            "wb"
        ) as buffer:

            while True:
                data = file.file.read(1024 * 1024)

                if not data:
                    break

                bytes_written += len(data)

                if bytes_written > MAX_PDF_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "PDF file is too large. "
                            "Maximum allowed size is 10 MB."
                        )
                    )

                buffer.write(data)

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise


    # --------------------------------------------------
    # EXTRACT PDF TEXT
    # --------------------------------------------------

    pdf_data = extract_pdf_text(
        file_path
    )

    text = pdf_data["text"]


    # --------------------------------------------------
    # CHECK TEXT
    # --------------------------------------------------

    if not text.strip():

        raise HTTPException(
            status_code=400,
            detail="No readable text found in the PDF."
        )


    # --------------------------------------------------
    # CREATE CHUNKS
    # --------------------------------------------------

    chunks = chunk_text(
        text
    )


    if not chunks:

        raise HTTPException(
            status_code=400,
            detail="Unable to create document chunks."
        )


    # --------------------------------------------------
    # NORMALIZE CHUNKS
    # --------------------------------------------------

    clean_chunks = []

    for chunk in chunks:

        if isinstance(chunk, dict):

            chunk_text_value = chunk.get(
                "text",
                ""
            )

        else:

            chunk_text_value = str(
                chunk
            )


        if chunk_text_value.strip():

            clean_chunks.append(
                chunk_text_value
            )


    if not clean_chunks:

        raise HTTPException(
            status_code=400,
            detail="Unable to extract valid document chunks."
        )


    # --------------------------------------------------
    # CREATE EMBEDDINGS
    # --------------------------------------------------

    embeddings = []

    for chunk in clean_chunks:

        embedding = create_embedding(
            chunk
        )

        embeddings.append(
            embedding
        )


    # --------------------------------------------------
    # CREATE METADATA
    # --------------------------------------------------

    metadatas = []

    for index in range(
        len(clean_chunks)
    ):

        metadatas.append({

            "document_id": document_id,

            "document": file.filename,

            "chunk": index + 1

        })


    # --------------------------------------------------
    # STORE IN CHROMADB
    # --------------------------------------------------

    add_chunks(
        clean_chunks,
        embeddings,
        metadatas
    )


    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {

        "document_id": document_id,

        "filename": file.filename,

        "pages": pdf_data["pages"],

        "characters": pdf_data["characters"],

        "chunks": len(clean_chunks),

        "message":
            "PDF uploaded, processed, embedded and indexed successfully!"

    }