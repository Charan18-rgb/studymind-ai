from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.services.adaptive_learning_service import adaptive_learning_service
from app.services.quiz_service import quiz_service

router = APIRouter(prefix="/adaptive", tags=["adaptive"])


class AdaptiveAnswer(BaseModel):
    question_id: int
    selected_answer: str
    time_spent_seconds: int = 0


class AdaptiveSubmitRequest(BaseModel):
    answers: List[AdaptiveAnswer]


@router.post("/session")
async def create_adaptive_session(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    document_id: int | None = None,
):
    return await adaptive_learning_service.create_session(
        user_id=user_id,
        db=db,
        document_id=document_id,
    )


@router.post("/session/{session_id}/submit")
async def submit_adaptive_session(
    session_id: int,
    body: AdaptiveSubmitRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.quiz import Quiz

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == session_id, Quiz.user_id == user_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Session not found")

    track_concept_id = quiz.concepts[0] if quiz.concepts else None
    answers: List[Dict[str, Any]] = [a.model_dump() for a in body.answers]

    try:
        result = await quiz_service.submit_quiz(
            user_id=user_id,
            quiz_id=session_id,
            answers=answers,
            db=db,
            track_concept_id=track_concept_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return {
        "before_mastery": result["before_mastery"],
        "after_mastery": result["after_mastery"],
        "improvement": result["improvement"],
        "concept": result["concept"],
        "questions_completed": result["total_questions"],
        "score": result["score"],
        "next_action": result["next_action"],
        "summary": (
            f"Your performance improved after targeted practice on {result['concept']}."
            if result.get("improvement") and result["improvement"] > 0
            else "Session complete. Review explanations and continue with the next recommendation."
        ),
    }
