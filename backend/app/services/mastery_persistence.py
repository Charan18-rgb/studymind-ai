from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.concept import LearnerConceptMastery
from app.services.mastery_service import MasteryService


async def get_or_create_mastery(
    user_id: int, concept_id: int, db: AsyncSession
) -> LearnerConceptMastery:
    result = await db.execute(
        select(LearnerConceptMastery).where(
            LearnerConceptMastery.user_id == user_id,
            LearnerConceptMastery.concept_id == concept_id,
        )
    )
    mastery = result.scalar_one_or_none()
    if mastery:
        return mastery

    mastery = LearnerConceptMastery(
        user_id=user_id,
        concept_id=concept_id,
        mastery_score=0.0,
        total_attempts=0,
        correct_attempts=0,
        accuracy=0.0,
        recent_accuracy=0.0,
        difficulty_distribution={},
        learning_status="not_studied",
    )
    db.add(mastery)
    await db.flush()
    return mastery


def mastery_to_update_dict(mastery: LearnerConceptMastery) -> Dict[str, Any]:
    return {
        "total_attempts": mastery.total_attempts,
        "correct_attempts": mastery.correct_attempts,
        "recent_accuracy": mastery.recent_accuracy,
        "difficulty_distribution": dict(mastery.difficulty_distribution or {}),
        "consecutive_correct": mastery.consecutive_correct,
        "consecutive_incorrect": mastery.consecutive_incorrect,
        "confidence": mastery.confidence,
        "accuracy": mastery.accuracy,
        "mastery_score": mastery.mastery_score,
        "learning_status": mastery.learning_status,
    }


async def apply_question_result(
    user_id: int,
    concept_id: int,
    is_correct: bool,
    difficulty: str,
    db: AsyncSession,
) -> LearnerConceptMastery:
    mastery = await get_or_create_mastery(user_id, concept_id, db)
    updated = MasteryService.update_mastery_after_attempt(
        mastery_to_update_dict(mastery),
        is_correct,
        difficulty,
    )

    mastery.total_attempts = updated["total_attempts"]
    mastery.correct_attempts = updated["correct_attempts"]
    mastery.recent_accuracy = updated["recent_accuracy"]
    mastery.difficulty_distribution = updated["difficulty_distribution"]
    mastery.consecutive_correct = updated["consecutive_correct"]
    mastery.consecutive_incorrect = updated["consecutive_incorrect"]
    mastery.accuracy = updated["accuracy"]
    mastery.mastery_score = updated["mastery_score"]
    mastery.learning_status = updated["learning_status"]
    mastery.last_attempted = datetime.now(timezone.utc)
    await db.flush()
    return mastery
