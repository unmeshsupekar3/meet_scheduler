from pydantic import BaseModel
from typing import Optional, List, Dict


class SlotRequest(BaseModel):
    user_input: str
    history: Optional[str] = ""
    email: str
    session_id: str