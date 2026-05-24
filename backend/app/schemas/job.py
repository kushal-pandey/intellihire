from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str
    skills_required: str            # comma-separated: "python,django,postgresql"
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: str = "full_time"


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    skills_required: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    status: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    skills_required: str
    location: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    job_type: str
    status: str
    employer_id: int
    created_at: datetime

    model_config = {"from_attributes": True}