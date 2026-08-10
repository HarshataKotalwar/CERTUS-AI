from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import ask_gemini

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(request: ChatRequest):

    if request.question.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    answer = ask_gemini(request.question)

    return {
        "question": request.question,
        "answer": answer
    }