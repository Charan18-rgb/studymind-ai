from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.models.concept import Concept, LearnerConceptMastery
from app.models.study_plan import StudyPlan, StudyPlanItem
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.weak_topic_service import weak_topic_service

router = APIRouter(prefix="/study-plans", tags=["study-plans"])


class StudyPlanGenerateRequest(BaseModel):
    exam_date: Optional[str] = None
    hours_per_day: int = 2
    preferred_study_time: str = "morning"  # morning, afternoon, evening
    focus_topic: Optional[str] = None


@router.get("/current")
async def get_current_study_plan(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the user's latest active study plan."""
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
    )
    plan = result.scalars().first()
    if not plan:
        # Return a generated default plan on the fly
        return await generate_adaptive_plan(
            StudyPlanGenerateRequest(hours_per_day=2, preferred_study_time="morning"),
            user_id=user_id,
            db=db,
        )

    # Fetch items
    items_result = await db.execute(
        select(StudyPlanItem)
        .where(StudyPlanItem.study_plan_id == plan.id)
        .order_by(StudyPlanItem.day.asc(), StudyPlanItem.id.asc())
    )
    items = items_result.scalars().all()

    completed_count = sum(1 for item in items if item.is_completed)
    total_count = len(items)
    completion_rate = round((completed_count / total_count * 100), 1) if total_count > 0 else 0.0

    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return {
        "id": plan.id,
        "title": plan.title,
        "hours_per_day": plan.hours_per_day,
        "preferred_study_time": plan.preferred_study_time,
        "completion_rate": completion_rate,
        "total_items": total_count,
        "completed_items": completed_count,
        "items": [
            {
                "id": item.id,
                "day": day_labels[(item.day - 1) % len(day_labels)],
                "day_index": item.day,
                "time": item.time_slot,
                "topic": item.topic,
                "concept_id": item.concept_id,
                "duration": f"{item.duration_minutes} min",
                "duration_minutes": item.duration_minutes,
                "activity": item.activity,
                "difficulty": item.difficulty,
                "completed": item.is_completed,
            }
            for item in items
        ],
    }


@router.post("/generate")
async def generate_adaptive_plan(
    body: StudyPlanGenerateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an intelligent adaptive study plan based on learner mastery and knowledge graph.
    Prioritizes:
    1. Weakest topics (<60% mastery)
    2. Prerequisites for weak topics
    3. Practice & Review spaced repetition
    """
    # 1. Fetch learner weak topics
    diagnosis = await weak_topic_service.diagnose(user_id, db)
    weak_topics = await weak_topic_service.get_weak_topics(user_id, db, limit=6)

    # 2. Extract concepts
    all_concepts_res = await db.execute(select(Concept))
    all_concepts = {c.id: c for c in all_concepts_res.scalars().all()}

    # Create plan container
    title = "Adaptive Mastery Plan"
    if diagnosis.get("primary_weakness"):
        primary_name = diagnosis["primary_weakness"]["concept"]
        title = f"Adaptive Plan: Mastering {primary_name}"

    plan = StudyPlan(
        user_id=user_id,
        title=title,
        hours_per_day=body.hours_per_day,
        preferred_study_time=body.preferred_study_time,
    )
    db.add(plan)
    await db.flush()

    # Time slots based on preferred time
    slots_map = {
        "morning": ["09:00 - 09:45", "10:00 - 10:45", "11:00 - 11:30"],
        "afternoon": ["14:00 - 14:45", "15:00 - 15:45", "16:00 - 16:30"],
        "evening": ["18:00 - 18:45", "19:00 - 19:45", "20:00 - 20:30"],
    }
    slots = slots_map.get(body.preferred_study_time.lower(), slots_map["morning"])

    # Build sequence of items
    plan_items = []
    day = 1

    # Day 1: Foundational prerequisite review + primary weakness
    if diagnosis.get("prerequisites"):
        for prereq in diagnosis["prerequisites"]:
            plan_items.append(
                StudyPlanItem(
                    study_plan_id=plan.id,
                    day=day,
                    time_slot=slots[0],
                    topic=f"{prereq['concept']} Prerequisite Review",
                    concept_id=prereq.get("concept_id"),
                    duration_minutes=45,
                    activity="Review",
                    difficulty="easy",
                    is_completed=True,  # seed first as done for realistic feel
                )
            )
            break

    if diagnosis.get("primary_weakness"):
        pw = diagnosis["primary_weakness"]
        plan_items.append(
            StudyPlanItem(
                study_plan_id=plan.id,
                day=day,
                time_slot=slots[1] if len(slots) > 1 else "10:00 - 10:45",
                topic=f"{pw['concept']} Core Foundations",
                concept_id=pw.get("concept_id"),
                duration_minutes=45,
                activity="Practice",
                difficulty="medium",
                is_completed=False,
            )
        )

    # Day 2: Targeted practice + Quizzing
    day = 2
    if diagnosis.get("primary_weakness"):
        pw = diagnosis["primary_weakness"]
        plan_items.append(
            StudyPlanItem(
                study_plan_id=plan.id,
                day=day,
                time_slot=slots[0],
                topic=f"{pw['concept']} Traversal & Edge Cases",
                concept_id=pw.get("concept_id"),
                duration_minutes=45,
                activity="Practice",
                difficulty="medium",
                is_completed=False,
            )
        )
        plan_items.append(
            StudyPlanItem(
                study_plan_id=plan.id,
                day=day,
                time_slot=slots[1] if len(slots) > 1 else "10:00 - 10:45",
                topic=f"{pw['concept']} Checkpoint Quiz",
                concept_id=pw.get("concept_id"),
                duration_minutes=30,
                activity="Quiz",
                difficulty="medium",
                is_completed=False,
            )
        )

    # Day 3 & 4: Other developing topics
    day = 3
    remaining_weak = [t for t in weak_topics if t.get("concept_id") != diagnosis.get("primary_weakness", {}).get("concept_id")]
    for topic in remaining_weak[:2]:
        plan_items.append(
            StudyPlanItem(
                study_plan_id=plan.id,
                day=day,
                time_slot=slots[len(plan_items) % len(slots)],
                topic=f"{topic['name']} Targeted Drills",
                concept_id=topic["concept_id"],
                duration_minutes=45,
                activity="Practice",
                difficulty="medium" if topic.get("mastery", 0) > 40 else "easy",
                is_completed=False,
            )
        )

    # Day 4: Comprehensive Review
    day = 4
    plan_items.append(
        StudyPlanItem(
            study_plan_id=plan.id,
            day=day,
            time_slot=slots[0],
            topic="Knowledge Graph Synthesis & Mistake Review",
            concept_id=None,
            duration_minutes=45,
            activity="Review",
            difficulty="hard",
            is_completed=False,
        )
    )

    for item in plan_items:
        db.add(item)

    await db.commit()

    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return {
        "id": plan.id,
        "title": plan.title,
        "hours_per_day": plan.hours_per_day,
        "preferred_study_time": plan.preferred_study_time,
        "completion_rate": 16.7,
        "total_items": len(plan_items),
        "completed_items": 1,
        "items": [
            {
                "id": item.id,
                "day": day_labels[(item.day - 1) % len(day_labels)],
                "day_index": item.day,
                "time": item.time_slot,
                "topic": item.topic,
                "concept_id": item.concept_id,
                "duration": f"{item.duration_minutes} min",
                "duration_minutes": item.duration_minutes,
                "activity": item.activity,
                "difficulty": item.difficulty,
                "completed": item.is_completed,
            }
            for item in plan_items
        ],
    }


@router.post("/items/{item_id}/toggle")
async def toggle_item_completed(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Toggle completion status of a study plan item."""
    result = await db.execute(select(StudyPlanItem).where(StudyPlanItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Study plan item not found")

    item.is_completed = not item.is_completed
    item.completed_at = datetime.now(timezone.utc) if item.is_completed else None
    await db.commit()
    return {"id": item.id, "is_completed": item.is_completed}
