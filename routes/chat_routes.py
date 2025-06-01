from fastapi import APIRouter, HTTPException
from models.chat import MeetingSlotExtractor
from schemas.chat_schemas import SlotRequest
import json


router = APIRouter()
extractor = MeetingSlotExtractor()




@router.post("/extract_mslots", summary="Extract meeting slot from chat")
async def extract_meeting_slot(request: SlotRequest):
    try:
        slots = extractor.extract_slots(
            user_input=request.user_input,
            history=request.history or "",
            user_email=request.email,
            session_id=request.session_id
        )

        return {"status": "success", "slots": slots}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Slot extraction failed: {str(e)}")