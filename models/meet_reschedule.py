from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime, timedelta
import sqlite3
import json
import re
from models.event import insert_event
from prompts.reschedule_prompt import RESCHEDULE_PROMPT
from models.meet_schedule import MeetSchedulerModel

llm = ChatOllama(model="gemma3:4b")

msm = MeetSchedulerModel()


class MeetRescheduleModel:
    def __init__(self):
        pass


    # def clean_llm_response(self,raw_response):
    #     try:
    #         raw_response = re.sub(r"```json|```", "", raw_response).strip()
    #         raw_response = raw_response.replace("True", "true").replace("False", "false")
    #         match = re.search(r'\{.*?\}', raw_response, re.DOTALL)
    #         if match:
    #             return json.loads(match.group(0))
    #         else:
    #             return None
    #     except Exception as e:
    #         print("Error parsing JSON:", e)
    #     return None

    # def is_slot_available(self,date, time, duration):
    #     conn = sqlite3.connect("calendar_events.db")
    #     cursor = conn.cursor()
    #     start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    #     end_dt = start_dt + timedelta(minutes=duration)

    #     cursor.execute("SELECT start, end FROM events WHERE DATE(start) = ?", (date,))
    #     slots = cursor.fetchall()
    #     conn.close()

    #     for slot in slots:
    #         existing_start = datetime.fromisoformat(slot[0])
    #         existing_end = datetime.fromisoformat(slot[1])
    #         if start_dt < existing_end and end_dt > existing_start:
    #             return False
    #     return True

    def suggest_alternate_slots(self,date, time, duration):
        base_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        suggestions = []
        deltas = [15, 30, 45, 60]

        for delta in deltas:
            new_time = base_dt + timedelta(minutes=delta)
            new_date = new_time.strftime("%Y-%m-%d")
            new_time_str = new_time.strftime("%H:%M")

            if msm.is_slot_available(new_date, new_time_str, duration):
                suggestions.append(new_time_str)
            if len(suggestions) >= 2:
                break
        return suggestions

    def extract_and_reschedule(self,user_input: str):
        prompt = RESCHEDULE_PROMPT.format(user_input=user_input)
        messages = [
            SystemMessage(content="Extract rescheduling details."),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        slots = msm.clean_llm_response(response.content)

        if not slots:
            return {"error": "Could not extract rescheduling details."}

        available = msm.is_slot_available(slots["new_date"], slots["new_time"], slots["duration_minutes"])
        
        if not available:
            alternatives = self.suggest_alternate_slots(slots["new_date"], slots["new_time"], slots["duration_minutes"])
            return {
                "status": "unavailable",
                "message": f"Slot not available at {slots['new_time']} on {slots['new_date']}.",
                "suggestions": alternatives,
                "slots": slots
            }

        # Remove old appointment
        conn = sqlite3.connect("calendar_events.db")
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM events 
            WHERE DATE(start) = ? AND TIME(start) = ? AND participants LIKE ?
        """, (slots["original_date"], f"{slots['original_time']}:00", f"%{slots['participant'][0]}%"))
        conn.commit()

        # Prepare and insert new event
        start_dt = datetime.strptime(f"{slots['new_date']} {slots['new_time']}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=slots["duration_minutes"])
        event = {
            "id": f"event-{slots['new_date'].replace('-', '')}{slots['new_time'].replace(':', '')}",
            "title": f"Rescheduled with {', '.join(slots['participant'])}",
            "description": slots.get("purpose", ""),
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "color": "#F39C12",  
            "participant": slots["participant"]
        }

        ev_stat = insert_event(event=event)
        if str(ev_stat).lower() == 'true':

            return {
                "status": "rescheduled",
                "message": f"Rescheduled to {slots['new_date']} at {slots['new_time']}.",
                "event": event
            }
        else:
            return {
                "status": "unavailable",
                "message": f"ERROR inserting into DB.Slot is available for {slots['new_date']} at {slots['new_time']}",
                # "slots": slots
                "event": {}
            }
        



if __name__ == "__main__":
    mrm = MeetRescheduleModel()
    user_input = "Can you move my appointment with Dr. Smith from June 10 at 2 PM to June 12 at 3:30 PM?"
    result = mrm.extract_and_reschedule(user_input)
    print(json.dumps(result, indent=2))