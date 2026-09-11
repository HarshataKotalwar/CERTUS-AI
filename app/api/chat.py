from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.embedding_service import create_embedding
from app.services.vector_service import search_chunks
from app.services.llm_service import ask_gemini

import logging


logger = logging.getLogger(__name__)

router = APIRouter()


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):

    question: str

    document_id: str


# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------

@router.post("/chat")
async def chat(request: ChatRequest):

    # --------------------------------------------------
    # 1. VALIDATE QUESTION
    # --------------------------------------------------

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    # --------------------------------------------------
    # 2. VALIDATE DOCUMENT ID
    # --------------------------------------------------

    if not request.document_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Document ID is required."
        )


    # --------------------------------------------------
    # 3. CREATE QUESTION EMBEDDING
    # --------------------------------------------------

    try:

        question_embedding = create_embedding(
            request.question
        )

    except Exception:
        logger.exception(
            "Failed to generate the question embedding."
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate the question embedding."
        )


    # --------------------------------------------------
    # 4. SEARCH ONLY THE CURRENT DOCUMENT
    # --------------------------------------------------

    try:

        results = search_chunks(
            question_embedding,
            request.document_id
        )

    except Exception:
        logger.exception(
            "Failed to search the document."
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to search the document."
        )


    # --------------------------------------------------
    # 5. EXTRACT CHROMADB RESULTS
    # --------------------------------------------------

    documents = results.get(
        "documents",
        [[]]
    )

    metadatas = results.get(
        "metadatas",
        [[]]
    )

    distances = results.get(
        "distances",
        [[]]
    )


    # ChromaDB returns nested lists

    documents = (
        documents[0]
        if documents and documents[0]
        else []
    )

    metadatas = (
        metadatas[0]
        if metadatas and metadatas[0]
        else []
    )

    distances = (
        distances[0]
        if distances and distances[0]
        else []
    )


    # --------------------------------------------------
    # 6. CHECK WHETHER ANY DOCUMENT WAS FOUND
    # --------------------------------------------------

    if not documents:

        raise HTTPException(
            status_code=404,
            detail=(
                "I couldn't find relevant information "
                "in the uploaded document."
            )
        )


    # --------------------------------------------------
    # 7. RELEVANCE CHECK
    # --------------------------------------------------

    if distances:

        best_distance = distances[0]

        # ChromaDB distance increases as similarity decreases.
        # Reject clearly unrelated results.

        if best_distance > 1.2:

            raise HTTPException(
                status_code=404,
                detail=(
                    "I couldn't find relevant information "
                    "in the uploaded document."
                )
            )


    # --------------------------------------------------
    # 8. BUILD RETRIEVED CONTEXT
    # --------------------------------------------------

    context = "\n\n".join(
        documents
    )


    # --------------------------------------------------
    # 9. ASK GEMINI USING ONLY RETRIEVED CONTEXT
    # --------------------------------------------------

    try:

        answer = ask_gemini(
            request.question,
            context
        )

    except Exception:
        logger.exception(
            "Failed to generate the answer."
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate the answer."
        )


    # --------------------------------------------------
    # 10. BUILD SOURCES
    # --------------------------------------------------

    sources = []

    for metadata in metadatas:

        sources.append({

            "document":
                metadata.get(
                    "document"
                ),

            "chunk":
                metadata.get(
                    "chunk"
                )

        })


    # --------------------------------------------------
    # 11. RETURN RESPONSE
    # --------------------------------------------------

    return {

        "question":
            request.question,

        "answer":
            answer,

        "sources":
            sources

    }