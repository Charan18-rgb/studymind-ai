from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class QuestionBase(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    options: List[str] = []
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"


class QuestionCreate(QuestionBase):
    concept_id: Optional[int] = None


class Question(QuestionBase):
    id: int
    quiz_id: int
    concept_id: Optional[int] = None
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str
    quiz_type: str = "adaptive"
    difficulty: str = "mixed"
    question_count: int = 10
    concepts: List[int] = []


class QuizCreate(QuizBase):
    document_id: int
    user_id: int


class Quiz(QuizBase):
    id: int
    document_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuizAttemptBase(BaseModel):
    pass


class QuizAttemptCreate(QuizAttemptBase):
    quiz_id: int
    user_id: int


class QuizAttempt(QuizAttemptBase):
    id: int
    quiz_id: int
    user_id: int
    score: float
    total_questions: int
    correct_answers: int
    time_spent_seconds: int
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionResultBase(BaseModel):
    user_answer: str
    is_correct: bool
    time_spent_seconds: int = 0


class QuestionResultCreate(QuestionResultBase):
    attempt_id: int
    question_id: int
    concept_id: Optional[int] = None


class QuestionResult(QuestionResultBase):
    id: int
    attempt_id: int
    question_id: int
    concept_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
