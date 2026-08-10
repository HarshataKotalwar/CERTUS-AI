from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.document_service import get_document
from app.services.llm_service import ask_gemini

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(request: ChatRequest):

    # Validate question
    if request.question.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Get uploaded document
    context = get_document()

    # Make sure a PDF has been uploaded
    if not context:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF before asking questions."
        )

    # Ask Gemini using the document context
    answer = ask_gemini(
        request.question,
        context
    )

    return {
        "question": request.question,
        "answer": answer
    }