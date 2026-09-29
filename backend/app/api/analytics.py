from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.models.activity import LearningActivity
from app.models.concept import Concept, LearnerConceptMastery
from app.models.quiz import QuestionResult, QuizAttempt

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
async def get_analytics(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Return comprehensive learner analytics for progress tracking."""
    # 1. Fetch concept masteries
    mastery_res = await db.execute(
        select(LearnerConceptMastery, Concept)
        .join(Concept, LearnerConceptMastery.concept_id == Concept.id)
        .where(LearnerConceptMastery.user_id == user_id)
        .order_by(Concept.id.asc())
    )
    concept_rows = list(mastery_res)

    mastery_values = [m.mastery_score for m, _ in concept_rows]
    overall_mastery = round(sum(mastery_values) / len(mastery_values), 1) if mastery_values else 0.0

    topics_mastered = sum(1 for m, _ in concept_rows if m.learning_status == "mastered")
    total_attempts_sum = sum(m.total_attempts for m, _ in concept_rows)

    # 2. Quiz attempts & accuracy
    attempts_res = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.completed_at.asc())
    )
    attempts = list(attempts_res.scalars().all())
    avg_accuracy = round(sum(a.score for a in attempts) / len(attempts), 1) if attempts else 0.0

    # 3. Topic mastery list
    topic_mastery = [
        {
            "name": concept.name,
            "mastery": round(m.mastery_score, 1),
            "accuracy": round(m.accuracy, 1),
            "status": m.learning_status,
            "attempts": m.total_attempts,
            "difficulty": concept.difficulty,
        }
        for m, concept in concept_rows
    ]

    # 4. Accuracy Trend
    if attempts:
        accuracy_trend = [
            {
                "attempt": f"Quiz {i + 1}",
                "score": round(a.score, 1),
                "date": a.completed_at.strftime("%b %d") if a.completed_at else f"Attempt {i+1}",
            }
            for i, a in enumerate(attempts[-8:])
        ]
    else:
        accuracy_trend = []

    # 5. Difficulty distribution
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
    for m, _ in concept_rows:
        dist = m.difficulty_distribution or {}
        for diff, count in dist.items():
            if diff in difficulty_counts:
                difficulty_counts[diff] += count

    # 6. Status distribution
    status_counts = {
        "needs_foundation": sum(1 for m, _ in concept_rows if m.learning_status == "needs_foundation"),
        "developing": sum(1 for m, _ in concept_rows if m.learning_status == "developing"),
        "proficient": sum(1 for m, _ in concept_rows if m.learning_status == "proficient"),
        "mastered": sum(1 for m, _ in concept_rows if m.learning_status == "mastered"),
    }

    # 7. Weekly Activity, counted from persisted quiz/practice events.
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=6)).date()
    activities_res = await db.execute(
        select(LearningActivity)
        .where(LearningActivity.user_id == user_id)
        .order_by(LearningActivity.created_at.asc())
    )
    activities = activities_res.scalars().all()
    week_counts = {}
    for activity in activities:
        if not activity.created_at:
            continue
        created = activity.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        day = created.astimezone(timezone.utc).date()
        if day >= week_start:
            bucket = week_counts.setdefault(day, {"sessions": 0, "questions": 0})
            bucket["sessions"] += 1
            bucket["questions"] += int((activity.activity_metadata or {}).get("questions_completed", (activity.activity_metadata or {}).get("total", 0)) or 0)

    weekly_activity = [
        {
            "day": (now.date() - timedelta(days=offset)).strftime("%a"),
            "date": (now.date() - timedelta(days=offset)).isoformat(),
            "hours": round(week_counts.get(now.date() - timedelta(days=offset), {}).get("questions", 0) * 1.5 / 60, 1),
            "sessions": week_counts.get(now.date() - timedelta(days=offset), {}).get("sessions", 0),
        }
        for offset in range(6, -1, -1)
    ]
    active_dates = sorted(day for day, counts in week_counts.items() if counts["sessions"])
    streak_days = 0
    cursor = now.date()
    active_set = set(active_dates)
    while cursor in active_set:
        streak_days += 1
        cursor -= timedelta(days=1)

    total_questions = await db.execute(
        select(func.count(QuestionResult.id))
        .join(QuizAttempt, QuestionResult.attempt_id == QuizAttempt.id)
        .where(QuizAttempt.user_id == user_id)
    )
    questions_answered = int(total_questions.scalar() or 0)

    return {
        "metrics": {
            "overall_mastery": overall_mastery,
            "overall_accuracy": avg_accuracy,
            "questions_answered": questions_answered,
            "topics_mastered": topics_mastered,
            "total_topics": len(concept_rows),
            "study_hours": round(sum(item["hours"] for item in weekly_activity), 1),
            "streak_days": streak_days,
        },
        "topic_mastery": topic_mastery,
        "accuracy_trend": accuracy_trend,
        "difficulty_distribution": difficulty_counts,
        "status_distribution": status_counts,
        "weekly_activity": weekly_activity,
    }
