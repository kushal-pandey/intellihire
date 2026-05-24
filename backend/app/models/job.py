from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    skills_required = Column(String(1000), nullable=False)   # comma-separated, e.g. "python,django,sql"
    location = Column(String(255), nullable=False)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    job_type = Column(String(20), default="full_time")       # full_time | part_time | contract | internship | remote
    status = Column(String(20), default="active")            # active | closed | draft
    employer_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employer = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")