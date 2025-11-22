from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Topic(BaseModel):
    id: str
    title: str
    description: str
    icon: str  # Placeholder for an icon name or URL
    order: int

class Lesson(BaseModel):
    id: str
    topic_id: str
    title: str
    content_text: str
    video_url: Optional[str] = None
    order: int

class UserProgress(BaseModel):
    user_id: str = "user_1" # Hardcoded for MVP
    lesson_id: str
    completed: bool
    completed_at: Optional[datetime] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    text: str
    video_url: Optional[str] = None

class ChatSession(BaseModel):
    lesson_id: str
    history: List[ChatMessage]
