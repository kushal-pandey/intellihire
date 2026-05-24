from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.utils.security import get_current_user, require_employer

router = APIRouter()

VALID_JOB_TYPES = {"full_time", "part_time", "contract", "internship", "remote"}
VALID_STATUSES = {"active", "closed", "draft"}


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """Create a new job listing. Employer only."""
    if job_data.job_type not in VALID_JOB_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid job_type. Choose from: {VALID_JOB_TYPES}")
    job = Job(**job_data.model_dump(), employer_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    search: Optional[str] = Query(None, description="Search by title, skills, or description"),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Public endpoint — list all active jobs with optional search and filters."""
    query = db.query(Job).filter(Job.status == "active")

    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%"),
                Job.skills_required.ilike(f"%{search}%"),
            )
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Job.job_type == job_type)

    return query.order_by(Job.created_at.desc()).offset((page - 1) * limit).limit(limit).all()


@router.get("/my-jobs", response_model=List[JobResponse])
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """Get all jobs posted by the authenticated employer."""
    return db.query(Job).filter(Job.employer_id == current_user.id).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID (public)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """Update a job listing. Only the employer who created it can update it."""
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    for field, value in job_data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """Delete a job listing. Only the employer who created it can delete it."""
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")
    db.delete(job)
    db.commit()