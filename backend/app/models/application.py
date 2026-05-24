from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_id = Column(Integer, ForeignKey("users.id"))
    resume_path = Column(String(500), nullable=False)
    cover_letter = Column(Text, nullable=True)
    ats_score = Column(Float, nullable=True)                 # 0–100 score
    status = Column(String(20), default="applied")           # applied | screening | interview | offered | rejected | withdrawn
    notes = Column(Text, nullable=True)                      # employer internal notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", back_populates="applications")