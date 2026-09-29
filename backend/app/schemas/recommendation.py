from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecommendationBase(BaseModel):
    recommendation_type: str
    target_concept_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    action: str
    priority: int = 0
    reason: Optional[str] = None


class RecommendationCreate(RecommendationBase):
    user_id: int


class Recommendation(RecommendationBase):
    id: int
    user_id: int
    is_dismissed: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
