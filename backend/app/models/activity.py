from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from app.database.session import Base


class LearningActivity(Base):
    __tablename__ = "learning_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # quiz_attempt, document_upload, concept_review, explanation_request
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    activity_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_type = Column(String, nullable=False)  # concept_review, adaptive_practice, study_plan
    target_concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    action = Column(String, nullable=False)  # practice, review, read, quiz
    priority = Column(Integer, default=0)  # Higher = more important
    reason = Column(Text)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
