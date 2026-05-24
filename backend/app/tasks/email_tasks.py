from app.celery_app import celery_app


@celery_app.task(name="send_application_confirmation")
def send_application_confirmation(candidate_email: str, job_title: str, ats_score: float):
    """
    Sends a confirmation email to the candidate after applying.
    In production: integrate SendGrid / Amazon SES here.
    """
    if ats_score >= 70:
        tip = "Great news — your profile is a strong match for this role!"
    elif ats_score >= 45:
        tip = "Tip: Add more keywords from the job description to boost your ATS score."
    else:
        tip = "Tip: Tailor your resume with skills listed in the job requirements."

    message = (
        f"Subject: Application Received — {job_title}\n\n"
        f"Hi,\n\n"
        f"We received your application for '{job_title}'.\n"
        f"Your ATS Compatibility Score: {ats_score}/100\n\n"
        f"{tip}\n\n"
        f"Best,\nIntelliHire Team"
    )
    # Replace the print with an actual email call in production
    print(f"[EMAIL → {candidate_email}]\n{message}\n{'─'*50}")
    return {"status": "sent", "to": candidate_email}


@celery_app.task(name="send_status_update")
def send_status_update(candidate_email: str, job_title: str, new_status: str):
    """Notifies candidate when employer changes their application status."""
    status_messages = {
        "screening": "Your application is being reviewed by the hiring team.",
        "interview": "Congratulations! You have been shortlisted for an interview.",
        "offered": "Exciting news — you have received a job offer!",
        "rejected": "Thank you for applying. We have decided to move forward with other candidates.",
    }
    body = status_messages.get(new_status, f"Your application status has been updated to: {new_status}.")
    message = (
        f"Subject: Application Update — {job_title}\n\n"
        f"Hi,\n\n{body}\n\nBest,\nIntelliHire Team"
    )
    print(f"[EMAIL → {candidate_email}]\n{message}\n{'─'*50}")
    return {"status": "sent", "to": candidate_email}