import sys
sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")

from models.user_intent import UserIntentModel
from models.chitchat import ChitChatModel
from models.meet_schedule import MeetSchedulerModel
from models.meet_reschedule import MeetRescheduleModel
from models.event import init_event_db, fetch_all_events
from models.email_send import send_confirmation_email
import json


init_event_db()

uim = UserIntentModel()
ccm = ChitChatModel()
msm = MeetSchedulerModel()
mrm = MeetRescheduleModel()

class ChatFlowModel:
    def __init__(self):
        pass

    def chat_flow(self, user_input,user_email= 'unmeshsupekar3@gmail.com'):
        try:
            print("Analysing User Input Intent")
            intent = uim.detect_intent(user_input = user_input)
            print("User Query Intent Detected:",intent)



            if intent == 'chitchat':
                print("CHitchat Mode")
                answer = ccm.chitchat(user_input=user_input)
                return {
                    "status_code":200,
                    "result":{
                        "intent":intent,
                        "answer":answer
                    }
                }
            
            elif intent == 'schedule':
                print("Scheduling your meeting")
                result = msm.extract_and_schedule(user_input=user_input)
                answer1 = json.dumps(result, indent=2)

                if result.get("status") == "available" and "event" in result:
                    event = result["event"]
                    meeting_date = event["start"].split("T")[0]
                    meeting_start_time = event["start"].split("T")[1]
                    meeting_end_time = event["end"].split("T")[1]
                    participants = event.get("participant", [])
                    purpose = event.get("description", "")
                    meeting_type = "Scheduled"
                    recipient_emails = [user_email] 

                    email_sent = send_confirmation_email(
                        recipient_emails,
                        meeting_type,
                        meeting_date,
                        meeting_start_time,
                        meeting_end_time,
                        participants,
                        purpose
                    )
                    print("Email sent:", email_sent)







                return {
                    "status_code":200,
                    "result":{
                        "intent":intent,
                        "answer":json.loads(answer1)
                    }
                }

            elif intent == "modify":
                print("Rescheduling your meeting")
                result = mrm.extract_and_reschedule(user_input)
                answer2 = json.dumps(result, indent=2)

            if result.get("status") == "rescheduled" and "event" in result:
                event = result["event"]
                meeting_date = event["start"].split("T")[0]
                meeting_start_time = event["start"].split("T")[1]
                meeting_end_time = event["end"].split("T")[1]
                participants = event.get("participant", [])
                purpose = event.get("description", "")
                meeting_type = "Rescheduled"
                recipient_emails = [user_email] 

                email_sent = send_confirmation_email(
                    recipient_emails,
                    meeting_type,
                    meeting_date,
                    meeting_start_time,
                    meeting_end_time,
                    participants,
                    purpose
                )
                print("Reschedule email sent:", email_sent)





                return {
                    "status_code":200,
                    "result":{
                        "intent":intent,
                        "answer":json.loads(answer2)
                    }
                }
            else:
                return {
                    "status_code":400,
                    "result": "Invalid intent type"}
        
        except Exception as e:
            print(e)
            return { "status_code":400,
                    "result": f"ERROR:{str(e)}"}


if __name__ == "__main__":
    from pprint import pprint
    cfm = ChatFlowModel()
    user_input = "Book a meeting with dr smith on tuesday 8 am for 30 mins"
    # query_reschedule = "Hey, can I reschedule my appointment to next Monday?"
    # query_schedule = "I want to book a new appointment for Tuesday"
    # query_chitchat = "How are you today?"
    # query_reschedule_detailed = "Can you move my appointment with Dr. Smith from June 10 at 2 PM to June 12 at 3:30 PM?"
    res = cfm.chat_flow(user_input=user_input)
    pprint(res)
    print(fetch_all_events())
