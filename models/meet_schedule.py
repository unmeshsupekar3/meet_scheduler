import sys
sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")
from models.event import init_event_db,fetch_all_events, insert_event
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime, timedelta
import sqlite3
import json
import re
from prompts.schedule_prompt import SCHEDULE_PROMPT

init_event_db()
fetch_all_events()


llm = ChatOllama(model="gemma3:4b") 


class MeetSchedulerModel:
    def __init__(self):
        pass


    def clean_llm_response(self,raw_response):
        try:
            print("cleaning LLM response")
            raw_response = re.sub(r"```json|```", "", raw_response).strip()
            raw_response = raw_response.replace("True", "true").replace("False", "false")
            # print(raw_response)
            match = re.search(r'\{.*?\}', raw_response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                return None
        except Exception as e:
            print("JSON parse error:", e)
            return None
        # return None

    def is_slot_available(self, date, time, duration):
        print("Checking available timeslots")
        conn = sqlite3.connect("calendar_events.db")
        cursor = conn.cursor()

        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=duration)

        cursor.execute("""
            SELECT start, end FROM events
            WHERE DATE(start) = ?
        """, (date,))
        slots = cursor.fetchall()
        conn.close()

        for slot in slots:
            # existing_start = datetime.strptime(f"{date} {slot[0]}", "%Y-%m-%d %H:%M:%S")
            # existing_end = datetime.strptime(f"{date} {slot[1]}", "%Y-%m-%d %H:%M:%S")
            existing_start = datetime.fromisoformat(slot[0]) 
            existing_end = datetime.fromisoformat(slot[1]) 
            if (start_dt < existing_end and end_dt > existing_start):
                return False
        return True

    def suggest_alternate_slots(self,date, time, duration):
        base_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        suggestions = []
        deltas = [15, 30, 45, 60]

        for delta in deltas:
            new_time = base_dt + timedelta(minutes=delta)
            new_date = new_time.strftime("%Y-%m-%d")
            new_time_str = new_time.strftime("%H:%M")

            if self.is_slot_available(new_date, new_time_str, duration):
                suggestions.append(new_time_str)
                
            if len(suggestions) >= 2:
                break
        return suggestions



    def extract_and_schedule(self,user_input: str):
        prompt = SCHEDULE_PROMPT.format(user_input=user_input)
        messages = [
            SystemMessage(content="Extract meeting details for scheduling."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)
        slots = self.clean_llm_response(response.content)
        if not slots:
            return {"error": "Could not extract meeting details."}

        available = self.is_slot_available(slots["date"], slots["time"], slots["duration_minutes"])

        if available:
            start_dt = datetime.strptime(f"{slots['date']} {slots['time']}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=slots["duration_minutes"])

            event_id = f"event-{slots['date'].replace('-', '')}{slots['time'].replace(':', '')}"

            event_type = slots.get('type', 'Meeting').capitalize()
            participants = slots.get('participant', [])
            event_title = f"{event_type} with {', '.join(participants)}"

            event_description = slots.get("purpose", "")

            event_start = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
            event_end = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

            event_color = "#2E86AB"

            event = {
                "id": event_id,
                "title": event_title,
                "description": event_description,
                "start": event_start,
                "end": event_end,
                "color": event_color,
                "participant": participants
            }

            ev_stat = insert_event(event=event)

            if str(ev_stat).lower() == 'true':

                return {
                    "status": "available",
                    "message": f"Slot is available for {slots['date']} at {slots['time']} and booked",
                    # "slots": slots
                    "event": event
                }
            else:
                return {
                    "status": "unavailable",
                    "message": f"ERROR inserting into DB.Slot is available for {slots['date']} at {slots['time']}",
                    # "slots": slots
                    "event": {}
                }
        else:
            alternatives = self.suggest_alternate_slots(slots["date"], slots["time"], slots["duration_minutes"])
            return {
                "status": "unavailable",
                "message": f"Slot not available at {slots['time']} on {slots['date']}.",
                "suggestions": alternatives,
                "original_slots": slots
            }
    


if __name__ == "__main__":
    msm = MeetSchedulerModel()
    user_query = "I need to schedule a consultation with Dr. Smith on June 10th at 2 PM for 30 minutes."
    result = msm.extract_and_schedule(user_query)
    print(json.dumps(result, indent=2))
