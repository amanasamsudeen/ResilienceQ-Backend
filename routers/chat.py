from fastapi import APIRouter
from models.chat_schema import ChatRequest, ChatResponse
from services.rag import ChatModel

router = APIRouter(
  
    tags=["Chat"]
)

chat_model = ChatModel()  # initialize once

@router.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    result = chat_model.ask(request.question)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
