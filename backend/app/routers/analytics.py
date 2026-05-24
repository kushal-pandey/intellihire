from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.job import Job
from app.models.application import Application
from app.models.user import User
from app.utils.security import require_employer, get_current_user

router = APIRouter()


@router.get("/employer/dashboard")
def employer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    """
    Employer analytics dashboard.
    Returns job stats, application funnel, average ATS scores, and top-performing postings.
    """
    total_jobs = db.query(Job).filter(Job.employer_id == current_user.id).count()
    active_jobs = db.query(Job).filter(Job.employer_id == current_user.id, Job.status == "active").count()

    total_applications = (
        db.query(Application).join(Job).filter(Job.employer_id == current_user.id).count()
    )

    # Application funnel by status
    status_counts = (
        db.query(Application.status, func.count(Application.id).label("count"))
        .join(Job)
        .filter(Job.employer_id == current_user.id)
        .group_by(Application.status)
        .all()
    )

    avg_ats = (
        db.query(func.avg(Application.ats_score))
        .join(Job)
        .filter(Job.employer_id == current_user.id)
        .scalar()
    )

    # Top 5 jobs by number of applications
    top_jobs = (
        db.query(Job.title, func.count(Application.id).label("applications"))
        .join(Application)
        .filter(Job.employer_id == current_user.id)
        .group_by(Job.id, Job.title)
        .order_by(func.count(Application.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "application_funnel": {row.status: row.count for row in status_counts},
        "average_ats_score": round(float(avg_ats or 0), 1),
        "top_jobs_by_applications": [
            {"title": title, "applications": count} for title, count in top_jobs
        ],
    }


@router.get("/candidate/dashboard")
def candidate_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Candidate analytics — application history, status breakdown, and ATS score trends."""
    total_applications = db.query(Application).filter(
        Application.candidate_id == current_user.id
    ).count()

    status_counts = (
        db.query(Application.status, func.count(Application.id).label("count"))
        .filter(Application.candidate_id == current_user.id)
        .group_by(Application.status)
        .all()
    )

    avg_ats = (
        db.query(func.avg(Application.ats_score))
        .filter(Application.candidate_id == current_user.id)
        .scalar()
    )

    best = (
        db.query(Application)
        .filter(Application.candidate_id == current_user.id)
        .order_by(Application.ats_score.desc())
        .first()
    )

    return {
        "total_applications": total_applications,
        "application_breakdown": {row.status: row.count for row in status_counts},
        "average_ats_score": round(float(avg_ats or 0), 1),
        "best_ats_score": best.ats_score if best else 0,
    }