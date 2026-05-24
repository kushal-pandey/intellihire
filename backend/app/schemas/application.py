from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    cover_letter: Optional[str]
    ats_score: Optional[float]
    status: str
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationStatusUpdate(BaseModel):
    status: str                     # screening | interview | offered | rejected
    notes: Optional[str] = None