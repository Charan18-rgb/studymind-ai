from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.concept import Concept, ConceptRelationship, LearnerConceptMastery
from app.models.document import Document


class KnowledgeGraphService:
    """Knowledge graph queries: concepts, relationships, prerequisites."""

    @staticmethod
    async def get_prerequisites(
        concept_id: int, db: AsyncSession, user_id: Optional[int] = None
    ) -> List[Concept]:
        """Prerequisites FOR concept_id: source --prerequisite--> target (concept_id)."""
        query = select(Concept).join(
            ConceptRelationship,
            Concept.id == ConceptRelationship.source_concept_id,
        ).where(
            ConceptRelationship.target_concept_id == concept_id,
            ConceptRelationship.relationship_type == "prerequisite",
        )
        if user_id is not None:
            query = query.join(Document, Concept.document_id == Document.id)
            query = query.where(Document.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_mastery_map(
        user_id: int, db: AsyncSession
    ) -> Dict[int, LearnerConceptMastery]:
        result = await db.execute(
            select(LearnerConceptMastery).where(LearnerConceptMastery.user_id == user_id)
        )
        return {m.concept_id: m for m in result.scalars().all()}

    @staticmethod
    async def get_graph_for_document(
        document_id: int, user_id: int, db: AsyncSession
    ) -> Dict[str, Any]:
        concepts_result = await db.execute(
            select(Concept).join(Document).where(Concept.document_id == document_id, Document.user_id == user_id)
        )
        concepts = list(concepts_result.scalars().all())
        concept_ids = [c.id for c in concepts]
        mastery_map = await KnowledgeGraphService.get_mastery_map(user_id, db)

        if concept_ids:
            rel_result = await db.execute(
                select(ConceptRelationship).where(
                    ConceptRelationship.source_concept_id.in_(concept_ids),
                    ConceptRelationship.target_concept_id.in_(concept_ids),
                )
            )
            relationships = list(rel_result.scalars().all())
        else:
            relationships = []

        nodes = []
        for concept in concepts:
            mastery = mastery_map.get(concept.id)
            if mastery:
                nodes.append(
                    {
                        "id": concept.id,
                        "name": concept.name,
                        "description": concept.description,
                        "difficulty": concept.difficulty,
                        "mastery": mastery.mastery_score,
                        "accuracy": mastery.accuracy,
                        "total_attempts": mastery.total_attempts,
                        "correct_attempts": mastery.correct_attempts,
                        "status": mastery.learning_status,
                    }
                )
            else:
                nodes.append(
                    {
                        "id": concept.id,
                        "name": concept.name,
                        "description": concept.description,
                        "difficulty": concept.difficulty,
                        "mastery": None,
                        "accuracy": None,
                        "total_attempts": 0,
                        "correct_attempts": 0,
                        "status": "not_studied",
                    }
                )

        edges = [
            {
                "source": rel.source_concept_id,
                "target": rel.target_concept_id,
                "relationship": rel.relationship_type,
                "confidence": rel.confidence,
            }
            for rel in relationships
        ]

        return {
            "document_id": document_id,
            "nodes": nodes,
            "edges": edges,
        }

    @staticmethod
    async def get_primary_demo_document_id(user_id: int, db: AsyncSession) -> Optional[int]:
        from app.models.document import Document

        result = await db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.id.asc())
        )
        doc = result.scalars().first()
        return doc.id if doc else None


knowledge_graph_service = KnowledgeGraphService()
