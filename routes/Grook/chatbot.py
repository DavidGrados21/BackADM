from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from .chatbot_service import generate_response

router = APIRouter( prefix="/chatbot", tags=["Chatbot"])

@router.post("/", response_model=ChatResponse)
def chat(data: ChatRequest):

    response = generate_response(data.message)

    return {
        "response": response
    }