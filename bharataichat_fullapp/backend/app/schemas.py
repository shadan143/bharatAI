from pydantic import BaseModel
from typing import Optional

class ConsentCreate(BaseModel):
    user_id: str
    purpose: str
    lang: Optional[str] = "hi"
    consent: bool
