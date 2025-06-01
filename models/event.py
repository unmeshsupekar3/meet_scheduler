import sqlite3
from datetime import datetime

def init_event_db(db_path="calendar_events.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                color TEXT,
                participants TEXT
            )
        """)

        conn.commit()
        conn.close()
        return {
            'status_code': 200,
            'result': "DB Init successful"
        }
    except Exception as e:
        
        return {
            'status_code': 400,
            'result': f"ERROR[DB Init]: str(e)"
        }

def insert_event(event: dict, db_path="calendar_events.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO events (id, title, description, start, end, color, participants)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get("id"),
            event.get("title"),
            event.get("description"),
            event.get("start"),
            event.get("end"),
            event.get("color"),
            ", ".join(event.get("participant", []))
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False

def fetch_all_events(db_path="calendar_events.db") -> list:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, description, start, end, color, participants FROM events")
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "start": row[3],
            "end": row[4],
            "color": row[5],
            "participant": row[6].split(", ") if row[6] else []
        })
    return events

if __name__ == "__main__":
    init_event_db()
    test_event = {
        "id": "event-202506011000",
        "title": "Consultation with Dr. Smith",
        "description": "Annual health check-up",
        "start": "2025-06-01T10:00:00",
        "end": "2025-06-01T10:30:00",
        "color": "#2E86AB",
        "participant": ["Dr. Smith"]
    }
    insert_event(test_event)
    print("Events in DB:", fetch_all_events())
