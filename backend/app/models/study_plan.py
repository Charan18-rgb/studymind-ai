from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    exam_date = Column(DateTime(timezone=True))
    hours_per_day = Column(Integer, default=2)
    preferred_study_time = Column(String, default="morning")
    subjects = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    items = relationship("StudyPlanItem", back_populates="study_plan", cascade="all, delete-orphan")


class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    day = Column(Integer, nullable=False)
    time_slot = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    duration_minutes = Column(Integer, default=30)
    activity = Column(String, default="practice")  # review, practice, quiz, read
    difficulty = Column(String, default="medium")
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    study_plan = relationship("StudyPlan", back_populates="items")
