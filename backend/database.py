import sqlite3
from typing import List, Optional
from datetime import datetime
from models import Topic, Lesson, UserProgress

# For this MVP, we will use a simple SQLite helper.
# In a production app, we would use SQLAlchemy or SQLModel.

import os
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parenting.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        icon TEXT,
        "order" INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id TEXT PRIMARY KEY,
        topic_id TEXT,
        title TEXT,
        content_text TEXT,
        video_url TEXT,
        "order" INTEGER,
        FOREIGN KEY(topic_id) REFERENCES topics(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_progress (
        user_id TEXT,
        lesson_id TEXT,
        completed BOOLEAN,
        completed_at TIMESTAMP,
        PRIMARY KEY (user_id, lesson_id)
    )
    ''')

    conn.commit()

    # Check if data exists, if not seed it
    cursor.execute("SELECT count(*) FROM topics")
    if cursor.fetchone()[0] == 0:
        seed_data(cursor)
        conn.commit()

    conn.close()

def seed_data(cursor):
    topics = [
        ("topic_sleep", "Sleep Training", "Help your baby sleep better", "bed", 1),
        ("topic_nutrition", "Nutrition", "Feeding and solids", "restaurant", 2),
        ("topic_play", "Play & Development", "Activities for growth", "toys", 3),
    ]
    cursor.executemany("INSERT INTO topics VALUES (?, ?, ?, ?, ?)", topics)

    lessons = [
        ("lesson_sleep_1", "topic_sleep", "Newborn Sleep Cycles",
         "Newborns typically sleep 16-18 hours a day but in short bursts. Understanding their sleep cycles is key. They have active sleep (REM) and quiet sleep.",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", 1),
        ("lesson_sleep_2", "topic_sleep", "Day/Night Confusion",
         "Many babies mix up day and night. Keep days bright and noisy, and nights dark and quiet to help reset their internal clock.",
         None, 2),
        ("lesson_nutrition_1", "topic_nutrition", "Breastfeeding Basics",
         "Latch is crucial. Ensure the baby's mouth covers the areola, not just the nipple. Feed on demand.",
         None, 1),
    ]
    cursor.executemany("INSERT INTO lessons VALUES (?, ?, ?, ?, ?, ?)", lessons)
    print("Database seeded.")

# Data Access Functions

def get_all_topics() -> List[Topic]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics ORDER BY \"order\"")
    rows = cursor.fetchall()
    conn.close()
    return [Topic(**dict(row)) for row in rows]

def get_lessons_by_topic(topic_id: str) -> List[Lesson]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lessons WHERE topic_id = ? ORDER BY \"order\"", (topic_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Lesson(**dict(row)) for row in rows]

def get_lesson(lesson_id: str) -> Optional[Lesson]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Lesson(**dict(row))
    return None

def update_progress(user_id: str, lesson_id: str, completed: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now() if completed else None
    cursor.execute("""
        INSERT INTO user_progress (user_id, lesson_id, completed, completed_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, lesson_id) DO UPDATE SET
        completed = excluded.completed,
        completed_at = excluded.completed_at
    """, (user_id, lesson_id, completed, now))
    conn.commit()
    conn.close()

def get_user_progress(user_id: str) -> List[UserProgress]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [UserProgress(user_id=row['user_id'], lesson_id=row['lesson_id'], completed=bool(row['completed']), completed_at=row['completed_at']) for row in rows]
