from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import ai_service
from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.models.concept import Concept
from app.models.quiz import Question, Quiz
from app.services.quiz_service import quiz_service

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


class QuizGenerateRequest(BaseModel):
    concept_id: int
    num_questions: int = 5
    difficulty: str = "medium"


class QuizAnswer(BaseModel):
    question_id: int
    selected_answer: str
    time_spent_seconds: int = 0


class QuizSubmitRequest(BaseModel):
    answers: List[QuizAnswer]


@router.post("/generate")
async def generate_quiz(
    body: QuizGenerateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    concept_result = await db.execute(select(Concept).where(Concept.id == body.concept_id))
    concept = concept_result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    from app.services.mastery_persistence import get_or_create_mastery

    mastery = await get_or_create_mastery(user_id, concept.id, db)

    if ai_service.available:
        questions_data = ai_service.generate_quiz(
            concept.name,
            concept.description or "",
            body.difficulty,
            body.num_questions,
            mastery.mastery_score,
        )
    else:
        from app.services.adaptive_learning_service import AdaptiveLearningService

        questions_data = AdaptiveLearningService._demo_questions(concept, body.difficulty)[
            : body.num_questions
        ]

    quiz = Quiz(
        document_id=concept.document_id,
        user_id=user_id,
        title=f"Quiz: {concept.name}",
        quiz_type="static",
        difficulty=body.difficulty,
        question_count=len(questions_data),
        concepts=[concept.id],
    )
    db.add(quiz)
    await db.flush()

    client_questions = []
    for idx, q in enumerate(questions_data):
        question = Question(
            quiz_id=quiz.id,
            concept_id=concept.id,
            question_text=q["question_text"],
            options=q.get("options", []),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation"),
            difficulty=q.get("difficulty", body.difficulty),
            order=idx,
        )
        db.add(question)
        await db.flush()
        client_questions.append(
            {
                "id": question.id,
                "question_text": question.question_text,
                "options": question.options,
                "difficulty": question.difficulty,
                "concept_id": concept.id,
            }
        )

    return {"quiz_id": quiz.id, "concept": concept.name, "questions": client_questions}


@router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id).order_by(Question.order))
    questions = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": q.options,
            "difficulty": q.difficulty,
            "concept_id": q.concept_id,
        }
        for q in q_result.scalars().all()
    ]
    return {
        "id": quiz.id,
        "title": quiz.title,
        "quiz_type": quiz.quiz_type,
        "questions": questions,
    }


@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    body: QuizSubmitRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    track = quiz.concepts[0] if quiz.concepts else None
    answers = [a.model_dump() for a in body.answers]
    return await quiz_service.submit_quiz(user_id, quiz_id, answers, db, track_concept_id=track)


@router.get("/{quiz_id}/results")
async def get_quiz_results(
    quiz_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.models.quiz import QuizAttempt

    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.created_at.desc())
    )
    attempt = result.scalars().first()
    if not attempt:
        raise HTTPException(status_code=404, detail="No results for this quiz")
    return {
        "quiz_id": quiz_id,
        "attempt_id": attempt.id,
        "score": attempt.score,
        "correct_answers": attempt.correct_answers,
        "total_questions": attempt.total_questions,
        "completed_at": attempt.completed_at,
    }
