from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    difficulty = Column(String, default="medium")  # easy, medium, hard
    estimated_importance = Column(Float, default=0.5)  # 0-1
    source_chunks = Column(JSON, default=list)  # List of chunk IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="concepts")
    relationships = relationship(
        "ConceptRelationship",
        foreign_keys="ConceptRelationship.source_concept_id",
        back_populates="source_concept"
    )
    reverse_relationships = relationship(
        "ConceptRelationship",
        foreign_keys="ConceptRelationship.target_concept_id",
        back_populates="target_concept"
    )
    learner_mastery = relationship("LearnerConceptMastery", back_populates="concept", uselist=False)


class ConceptRelationship(Base):
    __tablename__ = "concept_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    target_concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    relationship_type = Column(String, nullable=False)  # prerequisite, related, depends_on
    confidence = Column(Float, default=0.5)  # 0-1, AI confidence
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_concept = relationship("Concept", foreign_keys=[source_concept_id], back_populates="relationships")
    target_concept = relationship("Concept", foreign_keys=[target_concept_id], back_populates="reverse_relationships")


class LearnerConceptMastery(Base):
    __tablename__ = "learner_concept_mastery"
    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_learner_concept_mastery_user_concept"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    mastery_score = Column(Float, default=0.0)  # 0-100
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)  # 0-100
    recent_accuracy = Column(Float, default=0.0)  # 0-100, weighted recent performance
    difficulty_distribution = Column(JSON, default=dict)  # {easy: x, medium: y, hard: z}
    last_attempted = Column(DateTime(timezone=True))
    consecutive_correct = Column(Integer, default=0)
    consecutive_incorrect = Column(Integer, default=0)
    confidence = Column(Float, default=0.5)  # 0-1, learner self-assessment
    learning_status = Column(String, default="not_studied")  # not_studied, needs_foundation, developing, proficient, mastered
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    concept = relationship("Concept", back_populates="learner_mastery")
