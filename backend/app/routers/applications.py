import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.application import ApplicationResponse, ApplicationStatusUpdate
from app.utils.security import get_current_user, require_employer, require_candidate
from app.services.resume_parser import parse_resume_and_score
from app.tasks.email_tasks import send_application_confirmation, send_status_update

router = APIRouter()

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

VALID_STATUSES = {"screening", "interview", "offered", "rejected", "withdrawn"}


@router.post("/apply/{job_id}", response_model=ApplicationResponse, status_code=201)
async def apply_for_job(
    job_id: int,
    resume: UploadFile = File(..., description="PDF or DOCX resume file"),
    cover_letter: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    """
    Submit a job application with resume upload.
    - Validates file type (PDF/DOCX only)
    - Calculates ATS compatibility score automatically
    - Triggers async email confirmation via Celery
    """
    # Check job is open
    job = db.query(Job).filter(Job.id == job_id, Job.status == "active").first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or no longer accepting applications")

    # Prevent duplicate applications
    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.candidate_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    # Validate file type
    filename = resume.filename or ""
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resume files are accepted")

    # Save file with a unique name to avoid collisions
    ext = filename.rsplit(".", 1)[-1]
    saved_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    with open(file_path, "wb") as f:
        content = await resume.read()
        f.write(content)

    # Score the resume against the job
    ats_score = parse_resume_and_score(file_path, job.skills_required, job.requirements)

    application = Application(
        job_id=job_id,
        candidate_id=current_user.id,
        resume_path=file_path,
        cover_letter=cover_letter,
        ats_score=ats_score,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    send_application_confirmation(current_user.email, job.title, ats_score)

    return application


@router.get("/my-applications", response_model=List[ApplicationResponse])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    """Get all applications submitted by the authenticated candidate."""
    return (
        db.query(Application)
        .filter(Application.candidate_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )


@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """
    Get all applications for a job posting, sorted by ATS score descending.
    Only the employer who owns the job can access this.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    return (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .order_by(Application.ats_score.desc())   # Best matches first
        .all()
    )


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    update_data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """Update the status of an application. Triggers async email notification to candidate."""
    if update_data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {VALID_STATUSES}")

    application = (
        db.query(Application)
        .join(Job)
        .filter(Application.id == application_id, Job.employer_id == current_user.id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found or access denied")

    application.status = update_data.status
    if update_data.notes:
        application.notes = update_data.notes

    db.commit()
    db.refresh(application)

    # Notify candidate asynchronously
    candidate = db.query(User).filter(User.id == application.candidate_id).first()
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if candidate and job:
        send_status_update(candidate.email, job.title, update_data.status)

    return application