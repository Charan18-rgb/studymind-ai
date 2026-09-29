from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import LearningActivity
from app.models.concept import Concept, LearnerConceptMastery
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.weak_topic_service import (
    PREREQ_WEAK_THRESHOLD,
    weak_topic_service,
)


class RecommendationService:
    """Next best action from learner model + knowledge graph."""

    @staticmethod
    async def get_next_best_action(user_id: int, db: AsyncSession) -> Dict[str, Any]:
        mastery_result = await db.execute(
            select(LearnerConceptMastery, Concept)
            .join(Concept, LearnerConceptMastery.concept_id == Concept.id)
            .where(LearnerConceptMastery.user_id == user_id)
        )
        rows = list(mastery_result)
        if not rows:
            return RecommendationService._start_action()

        learner_mastery = [
            {
                "concept_id": concept.id,
                "name": concept.name,
                "mastery": mastery.mastery_score,
                "learning_status": mastery.learning_status,
            }
            for mastery, concept in rows
        ]

        diagnosis = await weak_topic_service.diagnose(user_id, db)
        primary = diagnosis.get("primary_weakness")
        if not primary:
            return RecommendationService._advanced_action(learner_mastery)

        prereqs = diagnosis.get("prerequisites") or []
        weak_prereq = next(
            (p for p in prereqs if p.get("mastery", 100) < PREREQ_WEAK_THRESHOLD),
            None,
        )

        if weak_prereq:
            return {
                "type": "prerequisite_review",
                "target_concept": weak_prereq["concept"],
                "target_concept_id": weak_prereq["concept_id"],
                "related_concept": primary["concept"],
                "related_concept_id": primary["concept_id"],
                "action": "adaptive_practice",
                "title": f"Review {weak_prereq['concept']}",
                "description": (
                    f"Review {weak_prereq['concept']} (mastery: {weak_prereq['mastery']:.0f}%), "
                    f"then practice {primary['concept']} tree traversal with targeted questions."
                ),
                "duration_minutes": 15,
                "recommended_duration": 15,
                "reason": (
                    f"{weak_prereq['concept']} is a prerequisite for {primary['concept']} "
                    f"and current mastery is low."
                ),
                "priority": 9,
            }

        if primary["mastery"] < 40:
            return {
                "type": "foundational_practice",
                "target_concept": primary["concept"],
                "target_concept_id": primary["concept_id"],
                "related_concept": None,
                "action": "adaptive_practice",
                "title": f"Master {primary['concept']} Fundamentals",
                "description": (
                    f"Your {primary['concept']} mastery is {primary['mastery']:.0f}%. "
                    f"Start an adaptive session with foundational questions."
                ),
                "duration_minutes": 20,
                "recommended_duration": 20,
                "reason": "Foundational weakness detected",
                "priority": 8,
            }

        recent = await RecommendationService._recent_activity(user_id, db)
        recent_poor = next(
            (
                a
                for a in recent
                if a.get("accuracy") is not None and isinstance(a.get("accuracy"), (int, float)) and a["accuracy"] < 50
            ),
            None,
        )
        if recent_poor:
            return {
                "type": "remediation",
                "target_concept": recent_poor.get("concept_name"),
                "action": "adaptive_practice",
                "title": f"Practice {recent_poor.get('concept_name')}",
                "description": recent_poor.get("description", "Targeted practice recommended."),
                "duration_minutes": 15,
                "recommended_duration": 15,
                "reason": "Recent poor performance",
                "priority": 7,
            }

        return {
            "type": "weak_topic_practice",
            "target_concept": primary["concept"],
            "target_concept_id": primary["concept_id"],
            "action": "adaptive_practice",
            "title": f"Practice {primary['concept']}",
            "description": (
                f"This is your weakest area (mastery: {primary['mastery']:.0f}%). "
                f"Targeted practice will have the most impact."
            ),
            "duration_minutes": 20,
            "recommended_duration": 20,
            "reason": "Weakest topic identified",
            "priority": 6,
        }

    @staticmethod
    async def _recent_activity(user_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(LearningActivity)
            .where(LearningActivity.user_id == user_id)
            .order_by(LearningActivity.created_at.desc())
            .limit(10)
        )
        activities = []
        for act in result.scalars().all():
            meta = act.activity_metadata or {}
            activities.append(
                {
                    "activity_type": act.activity_type,
                    "accuracy": meta.get("accuracy"),
                    "concept_name": meta.get("concept_name"),
                    "description": meta.get("description"),
                }
            )
        return activities

    @staticmethod
    def _start_action() -> Dict[str, Any]:
        return {
            "type": "onboarding",
            "target_concept": None,
            "action": "upload",
            "title": "Upload Your First Document",
            "description": "Start by uploading study material to build your knowledge map.",
            "duration_minutes": 5,
            "reason": "No learning data available yet. Initialize demo or upload a PDF.",
            "priority": 10,
        }

    @staticmethod
    def _advanced_action(learner_mastery: List[Dict[str, Any]]) -> Dict[str, Any]:
        strong = sorted(learner_mastery, key=lambda x: x["mastery"], reverse=True)
        if strong:
            name = strong[0]["name"]
            return {
                "type": "advanced",
                "target_concept": name,
                "action": "quiz",
                "title": f"Advanced {name} Challenge",
                "description": "You've strengthened weak areas. Try advanced questions.",
                "duration_minutes": 25,
                "reason": "Ready for advanced practice",
                "priority": 4,
            }
        return RecommendationService._start_action()


recommendation_service = RecommendationService()
