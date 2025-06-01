from fastapi import APIRouter, HTTPException
from models.user_chat import ChatFlowModel
from schemas.chat_schemas import SlotRequest
import json
from datetime import datetime


router = APIRouter()
extractor = ChatFlowModel()
from datetime import datetime

# Get current datetime in ISO format
  # e.g. "2025-06-02T15:30:45.123456"

# Extract date and time
  # '15:30' (HH:MM)



@router.post("/extract_mslots")
async def extract_meeting_slot(request: SlotRequest):
    try:
        now_iso = datetime.now().isoformat()
        current_date = now_iso.split("T")[0]      
        current_time = now_iso.split("T")[1][:5] 
        user_input1 = request.user_input
        user_input = user_input1 + f"Today's date is: {current_date}, Current time: {current_time}"

        slots = extractor.chat_flow(
            user_input= user_input,
            # history=request.history or "",
            user_email=request.email
            # session_id=request.session_id
        )

        return {"status": "success",
                 "slots": slots}
    except Exception as e:
        print(e)
        return {"status": "error",
                 "slots": None,
                 "message":f"Slot extraction failed: {str(e)}"}