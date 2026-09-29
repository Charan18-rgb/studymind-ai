from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    quiz_type = Column(String, default="adaptive")  # adaptive, static, assessment
    difficulty = Column(String, default="mixed")  # easy, medium, hard, mixed
    question_count = Column(Integer, default=10)
    concepts = Column(JSON, default=list)  # List of concept IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="multiple_choice")  # multiple_choice, true_false, short_answer
    options = Column(JSON, default=list)  # For multiple choice
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text)
    difficulty = Column(String, default="medium")
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    results = relationship("QuestionResult", back_populates="question", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, default=0.0)  # 0-100
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    question_results = relationship("QuestionResult", back_populates="attempt", cascade="all, delete-orphan")


class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    user_answer = Column(String)
    is_correct = Column(Boolean, default=False)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="question_results")
    question = relationship("Question", back_populates="results")
