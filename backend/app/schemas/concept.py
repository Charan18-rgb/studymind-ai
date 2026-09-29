from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ConceptBase(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: str = "medium"
    estimated_importance: float = 0.5


class ConceptCreate(ConceptBase):
    document_id: int
    source_chunks: List[int] = []


class Concept(ConceptBase):
    id: int
    document_id: int
    source_chunks: List[int]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConceptRelationshipBase(BaseModel):
    relationship_type: str
    confidence: float = 0.5


class ConceptRelationshipCreate(ConceptRelationshipBase):
    source_concept_id: int
    target_concept_id: int


class ConceptRelationship(ConceptRelationshipBase):
    id: int
    source_concept_id: int
    target_concept_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LearnerConceptMasteryBase(BaseModel):
    mastery_score: float = 0.0
    total_attempts: int = 0
    correct_attempts: int = 0
    accuracy: float = 0.0
    recent_accuracy: float = 0.0
    difficulty_distribution: Dict[str, int] = {}
    consecutive_correct: int = 0
    consecutive_incorrect: int = 0
    confidence: float = 0.5
    learning_status: str = "not_studied"


class LearnerConceptMasteryCreate(LearnerConceptMasteryBase):
    user_id: int
    concept_id: int


class LearnerConceptMastery(LearnerConceptMasteryBase):
    id: int
    user_id: int
    concept_id: int
    last_attempted: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConceptWithMastery(Concept):
    learner_mastery: Optional[LearnerConceptMastery] = None
    relationships: List[ConceptRelationship] = []
