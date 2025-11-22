from fastapi import FastAPI, HTTPException, Depends
from typing import List
from pydantic import BaseModel

from models import Topic, Lesson, UserProgress, ChatMessage, ChatSession
from database import init_db, get_all_topics, get_lessons_by_topic, get_lesson, update_progress, get_user_progress
from ai_service import generate_lesson_response

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Parenting Curriculum API is running"}

@app.get("/topics", response_model=List[Topic])
def read_topics():
    return get_all_topics()

class LessonWithStatus(Lesson):
    completed: bool

@app.get("/topics/{topic_id}/lessons", response_model=List[LessonWithStatus])
def read_lessons(topic_id: str):
    lessons = get_lessons_by_topic(topic_id)
    # In a real app, we'd get the current user from auth.
    user_id = "user_1"
    progress = get_user_progress(user_id)
    completed_ids = {p.lesson_id for p in progress if p.completed}

    result = []
    for l in lessons:
        l_dict = l.dict()
        l_dict['completed'] = l.id in completed_ids
        result.append(LessonWithStatus(**l_dict))
    return result

@app.get("/lessons/{lesson_id}", response_model=Lesson)
def read_lesson(lesson_id: str):
    lesson = get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

class ProgressUpdate(BaseModel):
    user_id: str
    lesson_id: str
    completed: bool

@app.post("/progress")
def mark_progress(update: ProgressUpdate):
    update_progress(update.user_id, update.lesson_id, update.completed)
    return {"status": "success"}

class ChatRequest(BaseModel):
    lesson_id: str
    history: List[ChatMessage]

@app.post("/chat/message", response_model=ChatMessage)
async def chat_message(request: ChatRequest):
    lesson = get_lesson(request.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    response_msg = await generate_lesson_response(lesson, request.history)
    return response_msg
