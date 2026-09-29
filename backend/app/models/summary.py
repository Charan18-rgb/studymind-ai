from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    title = Column(String, nullable=False)
    overview = Column(Text)
    key_concepts = Column(JSON, default=list)
    important_definitions = Column(JSON, default=list)
    important_formulas = Column(JSON, default=list)
    exam_points = Column(JSON, default=list)
    common_mistakes = Column(JSON, default=list)
    quick_revision = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="summaries")
