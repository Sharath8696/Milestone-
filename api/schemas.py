from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    response: str
    error: bool = False
