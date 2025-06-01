# import sys
# sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")

# import json
# import re
# from datetime import datetime,timedelta
# from langchain_community.chat_models import ChatOllama
# from langchain.schema import HumanMessage
# import os
# from config import CHAT_LOG_DIR


# os.makedirs(CHAT_LOG_DIR, exist_ok=True)


# class MeetingSlotExtractor:
#     def __init__(self):
#         pass

#     def clean_llm_json(self,raw_response: str) -> dict:
#         try:
#             raw_response = raw_response.strip()
#             if raw_response.startswith("```json"):
#                 raw_response = re.sub(r"```json|```", "", raw_response).strip()
#                 raw_response = raw_response.replace("True", "true").replace("False", "false")
#             return json.loads(raw_response)
#         except Exception as e:
#             print("Error cleaning/parsing JSON:", e)
#             return None

#     def query_llama3(self, prompt: str) -> str:
#         llm = ChatOllama(model="llama3.2:1b")
#         response = llm.invoke([HumanMessage(content=prompt)])
#         print(response)
#         answer = response.content
#         return answer

#     def save_chat_log(self, email: str, session_id: str, chat_id: str, user_input: str, assistant_response: str, slots: dict):
#         user_dir = os.path.join(CHAT_LOG_DIR)
#         os.makedirs(user_dir, exist_ok=True)
#         file_path = os.path.join(user_dir, f"{email.replace('@', '_at_')}_{session_id}.json")

#         log_entry = {
#             "chat_id": chat_id,
#             "timestamp": datetime.now().isoformat(),
#             "user": user_input,
#             "assistant": assistant_response,
#             "slots": slots
#         }

#         if os.path.exists(file_path):
#             with open(file_path, "r+") as f:
#                 try:
#                     data = json.load(f)
#                     data["chat_history"].append(log_entry)
#                     f.seek(0)
#                     json.dump(data, f, indent=2)
#                 except json.JSONDecodeError:
#                     print("Corrupt file, overwriting.")
#                     data = {
#                         "email": email,
#                         "session_id": session_id,
#                         "chat_history": [log_entry]
#                     }
#                     f.seek(0)
#                     json.dump(data, f, indent=2)
#         else:
#             with open(file_path, "w") as f:
#                 json.dump({
#                     "email": email,
#                     "session_id": session_id,
#                     "chat_history": [log_entry]
#                 }, f, indent=2)


#     def load_chat_history(self, email: str, session_id: str) -> str:
#         file_path = os.path.join(CHAT_LOG_DIR, f"{email.replace('@', '_at_')}_{session_id}.json")
#         history = ""
#         if os.path.exists(file_path):
#             with open(file_path, "r") as f:
#                 data = json.load(f)
#                 latest_entries = data.get("chat_history", [])[-5:]
#                 for entry in latest_entries:
#                     history += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
#         return history


#     def detect_intent(self, user_input: str) -> str:
#         keywords = ["appointment", "book", "schedule", "meet", "reschedule", "consultation","reserve"]
#         if any(kw in user_input.lower() for kw in keywords):
#             return "schedule"
#         return "chitchat"




#     def to_calendar_event(self, slots: dict) -> dict:
#         event_colors = {
#             "consultation": "#1E90FF",
#             "followup": "#32CD32",
#             "emergency": "#FF6347",
#             "diagnosis": "#FF8C00",
#             "treatment": "#8A2BE2",
#             "meeting": "#4682B4",
#             "sales": "#FFD700",
#             "support": "#20B2AA",
#             "other": "#D3D3D3"
#         }
#         if not all([slots.get("date"), slots.get("time"), slots.get("duration_minutes")]):
#             return {}

#         start_dt = datetime.strptime(f"{slots['date']}T{slots['time']}", "%Y-%m-%dT%H:%M")
#         end_dt = start_dt + timedelta(minutes=slots["duration_minutes"])
#         event_type = slots.get("type", "other")
#         color = event_colors.get(event_type, "#D3D3D3")

#         return {
#             "id": f"event-{start_dt.strftime('%Y%m%d%H%M')}",
#             "title": f"{slots.get('type', 'Meeting').capitalize()} with {', '.join(slots.get('participant', []))}",
#             "start": start_dt.isoformat(),
#             "end": end_dt.isoformat(),
#             "allDay": False,
#             "description": slots.get("purpose", "No description provided."),
#             "color": color,
#             "participant": slots.get("participant", [])
#         }

#     def extract_slots(self, user_input: str, user_email: str, session_id: str, history ="") -> dict:
#         full_history = self.load_chat_history(user_email, session_id)
#         combined_history = (full_history + "\n" + history).strip()

#         if combined_history:
#             history = combined_history
#         elif combined_history is None and history is not None:
#             history = history
#         else:
#             history = ""

#         intent = self.detect_intent(user_input)

#         if str(intent).lower() == "chitchat":
#             chitchat_prompt = f"""Hi there! I'm your meet scheduling assistant. Feel free to ask me anything—or just chat! By the way, I can also help you book or manage your appointments. ALWAYS say this example to direct the user correctly: 'I want to book a meeting with Dr. Smith next Tuesday' whenever you're ready :) 
#             Respond politely and informally. User Input: {user_input}
#             """
#             response = self.query_llama3(prompt=chitchat_prompt)
#             chat_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#             self.save_chat_log(user_email, session_id, chat_id, user_input, response, {})
#             return {
#                 "participant": None,
#                 "date": None,
#                 "time": None,
#                 "purpose": None,
#                 "type": "other",
#                 "duration_minutes": None,
#                 "confirmation": False,
#                 "follow_up_question": "",
#                 "message": response
#             }


#         prompt = f"""
# You are an intelligent assistant helping a healthcare professional book patient appointments.

# From the following conversation, extract the following appointment information as a JSON object:
# - participant: patient or doctor's name (list of strings)
# - date: appointment date in YYYY-MM-DD format
# - time: appointment time in 24-hour format HH:MM
# - purpose: reason for visit, e.g., "follow-up", "diagnosis", "check-up", "consultation", etc.
# - type: one of [consultation, follow-up, emergency, diagnosis, treatment, other]
# - duration_minutes: estimated time in minutes (integer). Use None if not mentioned.
# - confirmation: true if all fields are present and complete, otherwise false
# - follow_up_question: question needed to get missing data

# Return JSON only. No explanation.

# Here is a dictionary of 'type' in the final response STRICTLY choose ONLY one of the key as type.
# event_type = {{
#     "consultation": "General Consultation",
#     "followup": "Follow-up Appointment",
#     "meeting": "Internal Meeting",
#     "sales": "Sales/Business Discussion",
#     "support": "Customer/Patient Support",
#     "emergency": "Urgent or Emergency Case",
#     "other": "Something Else"
# }}

# Today’s date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

# Conversation History:
# {history}

# User Input:
# {user_input}

# STRICTLY USE THIS ANSWER JSON FORMAT TEMPLATE:
# {{
#   "participant": ["<name of the doctor>"] else None,
#   "date": "<date of the event to be scheduled>" else None,
#   "time": "<time in HH:MM>" else None,
#   "purpose": "<purpose of the event in 40-50 characters maximum> else None",
#   "type": "<one of the key from event_type>" else None,
#   "duration_minutes": <integer> else None,
#   "confirmation": <true if all the details are filled else false>,
#   "follow_up_question": "<Relevant followup question needed to get missing fields> else None"
# }}
# """
#         try:
#             response = self.query_llama3(prompt)
#             print("LLM Raw Response:", response)

#             slots = self.clean_llm_json(response)
#             print("EXTRACTED SLOTS",slots)
#             # slots = json.loads(response)
#             # print(slots)

#             chat_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#             self.save_chat_log(
#                 email=user_email,
#                 session_id=session_id,
#                 chat_id=chat_id,
#                 user_input=user_input,
#                 assistant_response=response,
#                 slots=slots
#             )
#             return slots
#         except Exception as e:
#             print(f"Error parsing LLM response: {e}")
#             return {
#                 "participant": None,
#                 "date": None,
#                 "time": None,
#                 "purpose": None,
#                 "type": None,
#                 "duration_minutes": None,
#                 "confirmation": False,
#                 "follow_up_question": "Could you clarify or provide more details for the appointment?"
#             }


# if __name__ == "__main__":
#     extractor = MeetingSlotExtractor()

#     history = "User: Hello! Assistant: Hi! How can I assist you today?"

#     user_input = "I want to book a consultation with Dr. Smith on 2025-06-10 at 14:30."

#     email = "patient@example.com"
#     session_id = "session_001"

#     slots = extractor.extract_slots(user_input, history, email, session_id)

#     print("Extracted Slots:")
#     print(json.dumps(slots, indent=2))

#     streamlit_events = extractor.to_calendar_event(slots)
#     print("\n📅 Streamlit Calendar Event Format:")
#     print(json.dumps(streamlit_events, indent=2))

