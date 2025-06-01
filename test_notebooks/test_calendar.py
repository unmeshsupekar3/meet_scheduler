import sys
sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")
import streamlit as st
from streamlit_calendar import calendar
import sqlite3
import json
from models.event import fetch_all_events

st.title("📅 Meeting Calendar")

event_list = fetch_all_events()

calendar_options = {
    "initialView": "timeGridWeek",
    "editable": False,
    "selectable": False,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
}

calendar(events=event_list, options=calendar_options)
