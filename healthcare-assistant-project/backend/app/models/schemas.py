# backend/app/models/schemas.py
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    user_id: str = Field(..., description="Unique identifier for the user")
    latitude: float | None = Field(None, description="User's latitude for location-based queries")
    longitude: float | None = Field(None, description="User's longitude for location-based queries")

class ChatResponse(BaseModel):
    response: str