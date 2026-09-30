from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_user_id
from app.models.user import User
from app.database.session import get_db
from app.models.activity import LearningActivity
from app.models.concept import Concept, LearnerConceptMastery
from app.models.quiz import QuizAttempt
from app.models.document import Document
from app.services.recommendation_service import recommendation_service
from app.services.weak_topic_service import weak_topic_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    mastery_result = await db.execute(
        select(LearnerConceptMastery, Concept)
        .join(Concept, LearnerConceptMastery.concept_id == Concept.id)
        .join(Document, Concept.document_id == Document.id)
        .where(LearnerConceptMastery.user_id == user_id)
        .where(Document.user_id == user_id)
    )
    rows = list(mastery_result)
    assessed_rows = [(m, concept) for m, concept in rows if (m.total_attempts or 0) > 0]
    mastery_values = [m.mastery_score for m, _ in assessed_rows]
    overall_mastery = round(sum(mastery_values) / len(mastery_values), 1) if mastery_values else 0.0

    attempt_result = await db.execute(
        select(func.avg(QuizAttempt.score)).where(QuizAttempt.user_id == user_id)
    )
    quiz_accuracy = round(float(attempt_result.scalar() or 0), 1)

    mastered_count = sum(1 for m, _ in assessed_rows if m.learning_status == "mastered")

    activity_result = await db.execute(
        select(LearningActivity)
        .where(LearningActivity.user_id == user_id)
        .order_by(LearningActivity.created_at.desc())
        .limit(8)
    )
    recent_activity = []
    for act in activity_result.scalars().all():
        meta = act.activity_metadata or {}
        label = meta.get("title") or meta.get("description") or act.activity_type.replace("_", " ").title()
        recent_activity.append(
            {
                "action": label,
                "activity_type": act.activity_type,
                "created_at": act.created_at.isoformat() if act.created_at else None,
                "metadata": meta,
            }
        )

    weak_topics = await weak_topic_service.get_weak_topics(user_id, db, limit=5)
    next_action = await recommendation_service.get_next_best_action(user_id, db)
    document_count = int(await db.scalar(select(func.count(Document.id)).where(Document.user_id == user_id)) or 0)
    concept_count = int(await db.scalar(select(func.count(Concept.id)).join(Document).where(Document.user_id == user_id)) or 0)

    activities = await db.execute(
        select(LearningActivity)
        .where(LearningActivity.user_id == user_id)
        .order_by(LearningActivity.created_at.asc())
    )
    study_hours = 0.0
    active_dates = set()
    for activity in activities.scalars().all():
        if activity.created_at:
            created = activity.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            active_dates.add(created.astimezone(timezone.utc).date())
            if activity.activity_type == "quiz_attempt":
                questions = int((activity.activity_metadata or {}).get("questions_completed", (activity.activity_metadata or {}).get("total", 0)) or 0)
                study_hours += questions * 1.5 / 60
    today = datetime.now(timezone.utc).date()
    streak_days = 0
    while today in active_dates:
        streak_days += 1
        today -= timedelta(days=1)

    return {
        "user": {"name": current_user.name, "email": current_user.email, "is_demo": current_user.is_demo},
        "stats": {
            "mastery": overall_mastery,
            "quiz_accuracy": quiz_accuracy,
            "streak_days": streak_days,
            "study_hours": round(study_hours, 1),
            "topics_mastered": mastered_count,
            "assessed_concepts": len(assessed_rows),
        },
        "weak_topics": weak_topics,
        "recent_activity": recent_activity,
        "next_best_action": next_action,
        "document_count": document_count,
        "concept_count": concept_count,
    }
