# IntelliHire — AI-Powered Job Board & Applicant Tracking System

> A production-grade full-stack application built with FastAPI, Django, PostgreSQL, Redis, and Docker.

**Live API →** https://intellihire-api-uxs1.onrender.com/api/docs  
**Admin Panel →** https://intellihire-admin.onrender.com

---

## What It Does

IntelliHire is a complete recruitment platform where employers post jobs and candidates apply with their resumes. The system automatically scores each resume against the job's requirements using an ATS (Applicant Tracking System) algorithm — the same approach used by companies like Greenhouse and Lever.

- Employers post jobs, view applicants ranked by ATS score, and move candidates through a hiring pipeline
- Candidates apply by uploading a PDF/DOCX resume and instantly receive a compatibility score
- Admins manage the entire platform through a Django admin dashboard

---

## Tech Stack

| Layer | Technology |
|---|---|
| Primary API | FastAPI 0.110 + Uvicorn |
| Admin Panel | Django 4.2 |
| Database | PostgreSQL 15 (Neon) |
| Cache + Message Broker | Redis 7 |
| Background Tasks | Celery 5 |
| ORM | SQLAlchemy 2.0 + Alembic |
| Authentication | JWT (access + refresh tokens) |
| Resume Parsing | PyPDF2 + python-docx |
| Rate Limiting | slowapi |
| Containerization | Docker + Docker Compose |
| Deployment | Render |

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│    FastAPI API      │     │   Django Admin      │     │   Celery Worker     │
│    Port: 8000       │     │   Port: 8001        │     │   (Background)      │
│                     │     │                     │     │                     │
│  /api/v1/auth       │     │  /admin/users       │     │  Email notifications│
│  /api/v1/jobs       │     │  /admin/jobs        │     │  Resume processing  │
│  /api/v1/apply      │     │  /admin/apps        │     │                     │
└──────────┬──────────┘     └──────────┬──────────┘     └──────────┬──────────┘
           │                           │                            │
           └───────────────────────────┼────────────────────────────┘
                                       │
              ┌────────────────────────┼───────────────────┐
              │                        │                   │
   ┌──────────▼──────────┐  ┌──────────▼──────────┐  ┌────▼────────────────┐
   │  PostgreSQL (Neon)  │  │       Redis         │  │   File Storage      │
   │  Primary Database   │  │  Cache + Queue      │  │   Resume Uploads    │
   └─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

---

## Key Features

**ATS Resume Scoring** — Automatically scores uploaded resumes (0–100) against job requirements using weighted keyword matching across skills, requirements, and resume structure. Employers see applicants ranked by score.

**Role-Based Access Control** — Candidates and employers have completely separate permissions enforced at the API level via JWT. Employers can only manage their own jobs and see their own applicants.

**Async Email Notifications** — Application confirmations and status updates are sent via Celery workers backed by Redis, keeping the API response time fast regardless of email delivery.

**Rate Limiting** — Login endpoint is rate-limited to 10 requests/minute per IP using slowapi to prevent brute force attacks.

**Analytics Dashboards** — Employers get an application funnel breakdown, average ATS scores, and top-performing job listings. Candidates get their application history and score trends.

**Django Admin** — Full platform management dashboard using Django's admin with unmanaged models pointing to the same PostgreSQL database that FastAPI manages.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/v1/auth/register | Public | Register candidate or employer |
| POST | /api/v1/auth/login | Public | Login, returns JWT tokens |
| GET | /api/v1/auth/me | Any | Get current user profile |
| GET | /api/v1/jobs/ | Public | List jobs with search & filters |
| POST | /api/v1/jobs/ | Employer | Create a job posting |
| GET | /api/v1/jobs/my-jobs | Employer | Get employer's own listings |
| PUT | /api/v1/jobs/{id} | Employer | Update own job posting |
| DELETE | /api/v1/jobs/{id} | Employer | Delete own job posting |
| POST | /api/v1/applications/apply/{job_id} | Candidate | Upload resume and apply |
| GET | /api/v1/applications/my-applications | Candidate | View own applications |
| GET | /api/v1/applications/job/{job_id} | Employer | View applicants ranked by ATS score |
| PATCH | /api/v1/applications/{id}/status | Employer | Move candidate through pipeline |
| GET | /api/v1/analytics/employer/dashboard | Employer | Hiring analytics |
| GET | /api/v1/analytics/candidate/dashboard | Candidate | Application analytics |

Full interactive documentation available at the live Swagger UI link above.

---

## Running Locally

**Prerequisites:** Docker Desktop, Python 3.11+

```bash
git clone https://github.com/kushal-pandey/intellihire.git
cd intellihire
cp .env.example .env   # Add your database credentials
docker compose up --build
```

| Service | URL |
|---|---|
| FastAPI Swagger Docs | http://localhost:8000/api/docs |
| Django Admin | http://localhost:8001/admin |

---

## Project Structure

```
intellihire/
├── backend/                  ← FastAPI service
│   ├── app/
│   │   ├── models/           ← SQLAlchemy models
│   │   ├── schemas/          ← Pydantic schemas
│   │   ├── routers/          ← API route handlers
│   │   ├── services/         ← ATS scoring logic
│   │   ├── tasks/            ← Celery async tasks
│   │   └── utils/            ← JWT, auth, rate limiting
│   └── alembic/              ← Database migrations
└── admin_panel/              ← Django admin service
    └── apps/core/            ← Unmanaged Django models
```

---

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@host/db?sslmode=require
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DJANGO_SECRET_KEY=your-django-secret-key
```