from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.concept import Concept, LearnerConceptMastery
from app.services.knowledge_graph_service import knowledge_graph_service

WEAK_MASTERY_THRESHOLD = 70.0
PREREQ_WEAK_THRESHOLD = 60.0


class WeakTopicService:
    @staticmethod
    async def get_weak_topics(user_id: int, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(LearnerConceptMastery, Concept)
            .join(Concept, LearnerConceptMastery.concept_id == Concept.id)
            .where(LearnerConceptMastery.user_id == user_id)
            .order_by(LearnerConceptMastery.mastery_score.asc())
        )
        weak = []
        for mastery, concept in result:
            if mastery.mastery_score < WEAK_MASTERY_THRESHOLD:
                weak.append(
                    {
                        "concept_id": concept.id,
                        "name": concept.name,
                        "mastery": mastery.mastery_score,
                        "accuracy": mastery.accuracy,
                        "learning_status": mastery.learning_status,
                        "recent_accuracy": mastery.recent_accuracy,
                    }
                )
        return weak[:limit]

    @staticmethod
    async def diagnose(user_id: int, db: AsyncSession) -> Dict[str, Any]:
        weak_topics = await WeakTopicService.get_weak_topics(user_id, db, limit=5)
        if not weak_topics:
            return {
                "primary_weakness": None,
                "prerequisites": [],
            }

        primary = weak_topics[0]
        prereq_concepts = await knowledge_graph_service.get_prerequisites(
            primary["concept_id"], db
        )
        mastery_map = await knowledge_graph_service.get_mastery_map(user_id, db)

        prerequisites = []
        for prereq in prereq_concepts:
            m = mastery_map.get(prereq.id)
            prerequisites.append(
                {
                    "concept_id": prereq.id,
                    "concept": prereq.name,
                    "mastery": m.mastery_score if m else 0.0,
                    "accuracy": m.accuracy if m else 0.0,
                }
            )

        return {
            "primary_weakness": {
                "concept_id": primary["concept_id"],
                "concept": primary["name"],
                "mastery": primary["mastery"],
                "accuracy": primary["accuracy"],
            },
            "prerequisites": prerequisites,
        }


weak_topic_service = WeakTopicService()
