from fastapi.testclient import TestClient
from main import app
from database import init_db

client = TestClient(app)

# Initialize DB before tests
init_db()

def test_read_topics():
    response = client.get("/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["id"] == "topic_sleep"

def test_read_lessons():
    response = client.get("/topics/topic_sleep/lessons")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["topic_id"] == "topic_sleep"

def test_read_lesson_detail():
    response = client.get("/lessons/lesson_sleep_1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "lesson_sleep_1"
    assert "video_url" in data

def test_chat_endpoint_mock():
    # This tests the endpoint logic, even if API key is missing it should return the mock response
    response = client.post("/chat/message", json={
        "lesson_id": "lesson_sleep_1",
        "history": [{"role": "user", "text": "Hello"}]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "model"
    assert "text" in data
