from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.utils.rate_limiter import limiter
from app.routers import auth, jobs, applications, analytics


app = FastAPI(
    title="IntelliHire API",
    description=(
        "## AI-Powered Job Board & Applicant Tracking System\n\n"
        "### Features\n"
        "- JWT Authentication with role-based access (Candidate / Employer)\n"
        "- Job posting, search and filtering\n"
        "- Resume upload with automatic ATS scoring\n"
        "- Application pipeline management\n"
        "- Async email notifications via Celery + Redis\n"
        "- Rate limiting on sensitive endpoints\n"
        "- Analytics dashboards for employers and candidates"
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["Authentication"])
app.include_router(jobs.router,         prefix="/api/v1/jobs",         tags=["Jobs"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Applications"])
app.include_router(analytics.router,    prefix="/api/v1/analytics",    tags=["Analytics"])


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "IntelliHire API",
        "status": "running",
        "docs": "/api/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}