import os
import google.generativeai as genai
from models import Lesson, ChatMessage, ChatSession
from typing import List, AsyncGenerator

# Configure Gemini
# Note: In a real scenario, the API key should be in environment variables.
# I will look for it in os.environ.
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

async def generate_lesson_response(lesson: Lesson, history: List[ChatMessage]) -> ChatMessage:
    if not API_KEY:
        # Mock response if no key is present
        last_msg = history[-1].text if history else "Start"
        return ChatMessage(
            role="model",
            text=f"I am a mock AI assistant (No API Key found). You said: '{last_msg}'. I am teaching you about {lesson.title}. Content snippet: {lesson.content_text[:50]}...",
            video_url=lesson.video_url if "video" in last_msg.lower() else None
        )

    # Construct the prompt
    # We need to feed the history to the model.
    # Gemini supports history in its chat interface.

    model = genai.GenerativeModel('gemini-pro')

    # Convert internal history to Gemini format
    gemini_history = []
    # System instruction (simulated by the first user message or system instruction if supported)
    # Gemini Pro doesn't strictly have a "system" role in the history list in the same way as GPT,
    # but we can prepend context to the first message or use the system_instruction parameter if available in the lib version.
    # For this version, let's prepend context to the chat start.

    system_prompt = f"""
    You are a friendly, encouraging parenting expert and teacher.
    Your goal is to teach the user this specific lesson: "{lesson.title}".

    Here is the source material you must teach:
    "{lesson.content_text}"

    If there is a video available for this lesson, the URL is: {lesson.video_url or "None"}

    Rules:
    1. Do not dump all the text at once. Teach it in small, bite-sized conversational pieces.
    2. Ask the user questions to verify their understanding or ask about their specific situation (e.g., "How does your baby sleep currently?").
    3. Be empathetic and supportive.
    4. If the user asks to see the video, provide the video URL in your response text specifically or simply say "Here is the video".
    5. If you have finished teaching the content, congratulate the user.
    6. Stick primarily to the provided source material for factual information, but you can use your general parenting knowledge to be empathetic and helpful with context.
    """

    # If history is empty, this is the start of the session.
    # We will send the system prompt + a greeting trigger.

    chat = model.start_chat(history=[])

    # We need to replay the history to the chat object
    # Note: The history passed to this function includes the *latest* user message.
    # We need to separate prior history and the new message.

    # Simply sending the prompt with the context for each turn is a stateless approach,
    # but `start_chat` manages state.
    # Since the backend is REST (stateless), we must rebuild the state or use a "Stateless" prompt approach.
    # Let's use a stateless approach: construct the full prompt with history.

    messages_payload = []
    # Add system context to the very first logical message or as a preamble
    messages_payload.append({'role': 'user', 'parts': [system_prompt + "\n\n[System: The user has started the lesson.]"]})
    messages_payload.append({'role': 'model', 'parts': ["Understood. I am ready to teach."]})

    for msg in history[:-1]: # All except last one (which is the new one)
        role = 'user' if msg.role == 'user' else 'model'
        messages_payload.append({'role': role, 'parts': [msg.text]})

    last_user_msg = history[-1].text

    # Now generate response
    # We can't easily use `start_chat` with a pre-defined history list in the python client unless we manually build the Content objects.
    # It's often easier to just concatenate for a simple "one-shot" completion that acts like a chat,
    # OR assume the python client handles the list of dicts if we use `generate_content` on the model directly (it doesn't preserve state, but we provide history).

    # Actually, `model.generate_content(contents=...)` takes a list of contents.
    messages_payload.append({'role': 'user', 'parts': [last_user_msg]})

    try:
        response = model.generate_content(messages_payload)
        response_text = response.text

        # Check if we should attach the video (simple heuristic: if the model mentions "video" and one exists)
        video_response = None
        if lesson.video_url and ("video" in response_text.lower() or "watch" in response_text.lower()):
            video_response = lesson.video_url

        return ChatMessage(role="model", text=response_text, video_url=video_response)
    except Exception as e:
        return ChatMessage(role="model", text=f"Sorry, I had trouble connecting to the AI assistant. ({str(e)})")
