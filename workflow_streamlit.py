import sys
sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")

import streamlit as st
from datetime import datetime
from streamlit_calendar import calendar
from models.event import fetch_all_events
from models.user_chat import ChatFlowModel 
import json
import uuid
import random

def show_calendar_and_event_details1():
    calendar_keys = [
    "calendar_key_1", "calendar_key_2", "calendar_key_3", "calendar_key_4", "calendar_key_5",
    "calendar_key_6", "calendar_key_7", "calendar_key_8", "calendar_key_9", "calendar_key_10",
    "calendar_key_11", "calendar_key_12", "calendar_key_13", "calendar_key_14", "calendar_key_15",
    "calendar_key_16", "calendar_key_17", "calendar_key_18", "calendar_key_19", "calendar_key_20"
]
     
    random_calendar_key = random.choice(calendar_keys)
    events = fetch_all_events()

    calendar_options = {
        "initialView": "timeGridWeek",
        "editable": False,
        "selectable": False,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
    }
    calendar(events=events, options=calendar_options)

    # Show event selector for details
    event_titles = [event['title'] for event in events]
    selected_title = st.selectbox("Select an event to view details", event_titles)

    selected_event = next((e for e in events if e['title'] == selected_title), None)
    if selected_event:
        st.markdown("### Event Details")
        st.markdown(f"**Title:** {selected_event['title']}")
        st.markdown(f"**Description:** {selected_event.get('description', 'N/A')}")
        st.markdown(f"**Start:** {selected_event['start']}")
        st.markdown(f"**End:** {selected_event['end']}")
        st.markdown(f"**Participants:** {', '.join(selected_event.get('participant', []))}")

def show_calendar_and_event_details2():
    calendar_keys = [
    "calendar_key_1", "calendar_key_2", "calendar_key_3", "calendar_key_4", "calendar_key_5",
    "calendar_key_6", "calendar_key_7", "calendar_key_8", "calendar_key_9", "calendar_key_10",
    "calendar_key_11", "calendar_key_12", "calendar_key_13", "calendar_key_14", "calendar_key_15",
    "calendar_key_16", "calendar_key_17", "calendar_key_18", "calendar_key_19", "calendar_key_20"
]
     
    random_calendar_key = random.choice(calendar_keys)
    events = fetch_all_events()

    calendar_options = {
        "initialView": "timeGridWeek",
        "editable": False,
        "selectable": False,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
    }
    calendar(events=events, options=calendar_options, key=str(uuid.uuid4()))

    # Show event selector for details
    event_titles = [event['title'] for event in events]
    selected_title = st.selectbox("Select an event to view details", event_titles,key=str(uuid.uuid4()))

    selected_event = next((e for e in events if e['title'] == selected_title), None)
    if selected_event:
        st.markdown("### Event Details")
        st.markdown(f"**Title:** {selected_event['title']}")
        st.markdown(f"**Description:** {selected_event.get('description', 'N/A')}")
        st.markdown(f"**Start:** {selected_event['start']}")
        st.markdown(f"**End:** {selected_event['end']}")
        st.markdown(f"**Participants:** {', '.join(selected_event.get('participant', []))}")




st.set_page_config(layout="wide")

cfm = ChatFlowModel()

# # Layout with two columns: left (calendar), right (chat)
left_col, right_col = st.columns([3, 1])

with left_col:
    with st.expander("📅 Your Meeting Calendar", expanded=True):
            show_calendar_and_event_details1()
#         st.write("Here are your upcoming scheduled meetings:")
#         events = fetch_all_events()
#         calendar_options = {
#             "initialView": "timeGridWeek",
#             "editable": False,
#             "selectable": False,
#             "headerToolbar": {
#                 "left": "prev,next today",
#                 "center": "title",
#                 "right": "dayGridMonth,timeGridWeek,timeGridDay",
#             },
#         }
#         calendar(events=events, options=calendar_options)

with right_col:
    st.title("🤖 Meeting Scheduler Chat")


    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown("Welcome! 👋 Enter your email and tell me what you'd like to do — book, reschedule, or just chat. I'll take care of the rest!")

    with st.form(key="chat_form", clear_on_submit=True):
        user_email = st.text_input(
            "Your Email 📨",
            value="",
            placeholder="Enter your email for confirmations",
            help="We'll send your meeting confirmation here."
        )
        user_input1 = st.text_area(
            "Your message 💬",
            placeholder="E.g., 'Book a meeting with Dr. Smith next Tuesday at 10am for 30 minutes'",
            height=100
        )
        
        now_iso = datetime.now().isoformat()
        current_date = now_iso.split("T")[0]      
        current_time = now_iso.split("T")[1][:5] 
        user_input = user_input1 + f"Today's date is: {current_date}, Current time: {current_time}"
        submit = st.form_submit_button("Send")

    if submit:
        if not user_email.strip():
            st.warning("Please enter your email so I can send you a confirmation.")
        elif not user_input.strip():
            st.warning("Please type a message so I can assist you.")
        else:
            with st.spinner("Processing your request..."):
                st.write("🔍 Analyzing your message and detecting intent...")
                response = cfm.chat_flow(user_input=user_input, user_email=user_email)
                st.write(response)
                st.write("✅ Intent detected and handled.")

            st.session_state.chat_history.append(("You", user_input))

            if response["status_code"] == 200:
                result = response.get("result", {})
                intent = result.get("intent", "unknown")
                answer = result.get("answer", "")
                if isinstance(answer, dict) or isinstance(answer, list):
                    bot_answer = json.dumps(answer, indent=2)
                else:
                    bot_answer = str(answer)

                # Add some user-friendly follow up messages based on intent
                if intent == "schedule":
                    bot_answer += "\n\n✅ Your meeting has been scheduled. You will receive an email confirmation shortly."
                elif intent == "modify":
                    bot_answer += "\n\n✅ Your meeting has been rescheduled. Confirmation email sent."
                elif intent == "chitchat":
                    bot_answer += "\n\n🤖 Happy to chat anytime! Need help scheduling something?"

            else:
                bot_answer = response.get("result", "😞 Sorry, something went wrong. Please try again.")

            st.session_state.chat_history.append(("Bot", bot_answer))
            with left_col:
                with st.expander("📅 Your Meeting Calendar", expanded=True):
                    show_calendar_and_event_details1()

    # Display chat history with styled chat bubbles
    for speaker, message in st.session_state.chat_history:
        if speaker == "You":
            st.markdown(
                f'<div style="text-align: right; background-color:#DCF8C6; padding:10px; margin:8px 0; border-radius:12px; max-width:75%; margin-left:auto; font-size: 16px;">{message}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="text-align: left; background-color:#ECECEC; padding:10px; margin:8px 0; border-radius:12px; max-width:75%; margin-right:auto; font-size: 16px;">{message}</div>',
                unsafe_allow_html=True
            )
