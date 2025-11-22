# Parenting Curriculum App

A Duolingo-style parenting curriculum application with an AI-powered teaching assistant. This app helps parents learn about their child's growth through structured topics (Sleep, Nutrition, Play) and interactive chat lessons.

## Features

*   **Curriculum-based Learning**: Structured topics and lessons.
*   **AI Assistant**: Interactive chat interface powered by Google Gemini to teach lessons conversationally.
*   **Video Integration**: Embeds educational videos directly into the chat flow.
*   **Progress Tracking**: Tracks completed lessons.

## Tech Stack

*   **Backend**: Python (FastAPI), SQLite, Google Generative AI (Gemini).
*   **Frontend**: React Native (Expo).

## Prerequisites

*   Python 3.12+
*   Node.js & npm
*   Expo Go app (on your phone) or Android/iOS Simulator.

## Setup & Deployment

### 1. Backend (API)

The backend serves the curriculum data and handles AI chat requests.

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure AI (Optional)**:
    To use the real AI features, set your Google Gemini API key. If not set, the app will use a mock AI response.
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```

5.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

### 2. Frontend (Mobile App)

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  **Configuration**:
    If you are running on a physical device or Android Emulator, you may need to update the `API_URL` in the source files (`HomeScreen.js`, `TopicScreen.js`, `LessonScreen.js`).
    *   **iOS Simulator**: `http://localhost:8000` (Default)
    *   **Android Emulator**: `http://10.0.2.2:8000`
    *   **Physical Device**: Use your computer's local IP address (e.g., `http://192.168.1.x:8000`).

4.  Start the app:
    ```bash
    npx expo start
    ```
    *   Press `a` to run on Android Emulator.
    *   Press `i` to run on iOS Simulator.
    *   Scan the QR code with the Expo Go app to run on your physical device.

## Testing

### Backend Tests

We use `pytest` to test the API endpoints.

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Run tests:
    ```bash
    python -m pytest
    ```

## Usage Guide

1.  **Home Screen**: Browse the list of available parenting topics (e.g., Sleep Training, Nutrition).
2.  **Topic Screen**: View the lessons within a topic. Completed lessons are marked with a green circle.
3.  **Lesson Screen**:
    *   The AI will greet you and begin teaching the content.
    *   You can ask questions or just say "Next" to continue.
    *   If a lesson includes a video, it will appear in the chat.
    *   Click **"Mark Complete & Finish"** to save your progress and return to the topic list.
