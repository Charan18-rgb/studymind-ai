"""Idempotent demo seed and reset for NOVA presentation."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.demo_user import DEMO_USER_EMAIL, get_or_create_demo_user
from app.models.activity import LearningActivity
from app.models.concept import Concept, ConceptRelationship, LearnerConceptMastery
from app.models.document import Document, DocumentChunk
from app.models.quiz import Question, QuestionResult, Quiz, QuizAttempt

DEMO_DOCUMENT_TITLE = "Data Structures and Algorithms"
DEMO_FILENAME = "Data Structures.pdf"

CONCEPTS_DATA: List[Dict[str, Any]] = [
    {"name": "Arrays", "description": "Contiguous memory storage with O(1) access", "difficulty": "easy", "importance": 0.9, "mastery": 91.0, "status": "mastered"},
    {"name": "Linked Lists", "description": "Sequential node-based structure", "difficulty": "easy", "importance": 0.85, "mastery": 82.0, "status": "mastered"},
    {"name": "Stacks", "description": "LIFO data structure", "difficulty": "easy", "importance": 0.8, "mastery": 88.0, "status": "mastered"},
    {"name": "Queues", "description": "FIFO data structure", "difficulty": "easy", "importance": 0.8, "mastery": 76.0, "status": "proficient"},
    {"name": "Trees", "description": "Hierarchical node structure", "difficulty": "medium", "importance": 0.95, "mastery": 42.0, "status": "developing"},
    {"name": "Recursion", "description": "Self-referential function calls", "difficulty": "medium", "importance": 0.9, "mastery": 51.0, "status": "developing"},
    {"name": "Graphs", "description": "Vertex-edge networks", "difficulty": "hard", "importance": 0.85, "mastery": 63.0, "status": "proficient"},
]

RELATIONSHIPS: List[Tuple[str, str, str, float]] = [
    ("Arrays", "Linked Lists", "related", 0.8),
    ("Linked Lists", "Trees", "prerequisite", 0.9),
    ("Recursion", "Trees", "prerequisite", 0.95),
    ("Recursion", "Graphs", "prerequisite", 0.85),
    ("Trees", "Graphs", "related", 0.8),
    ("Stacks", "Queues", "related", 0.9),
]

CHUNK_TEXTS = [
    "Arrays are fundamental data structures that store elements in contiguous memory locations.",
    "Linked lists consist of nodes where each node contains data and a reference to the next node.",
    "Stacks follow the Last-In-First-Out (LIFO) principle.",
    "Queues follow the First-In-First-Out (FIFO) principle.",
    "Trees are hierarchical data structures with a root node and child nodes.",
    "Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem.",
    "Graphs consist of vertices connected by edges and support DFS and BFS traversals.",
]


async def _ensure_document(db: AsyncSession, user_id: int) -> Document:
    result = await db.execute(
        select(Document).where(
            Document.user_id == user_id,
            Document.title == DEMO_DOCUMENT_TITLE,
        )
    )
    doc = result.scalar_one_or_none()
    if doc:
        return doc

    doc = Document(
        user_id=user_id,
        title=DEMO_DOCUMENT_TITLE,
        filename=DEMO_FILENAME,
        file_path="data/demo.pdf",
        page_count=45,
        status="ready",
    )
    db.add(doc)
    await db.flush()

    for i, text in enumerate(CHUNK_TEXTS):
        db.add(
            DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=text,
                page_number=i + 1,
            )
        )
    await db.flush()
    return doc


async def _upsert_concepts(db: AsyncSession, document_id: int, user_id: int) -> Dict[str, Concept]:
    created: Dict[str, Concept] = {}
    for item in CONCEPTS_DATA:
        result = await db.execute(
            select(Concept).where(
                Concept.document_id == document_id,
                Concept.name == item["name"],
            )
        )
        concept = result.scalar_one_or_none()
        if not concept:
            concept = Concept(
                document_id=document_id,
                name=item["name"],
                description=item["description"],
                difficulty=item["difficulty"],
                estimated_importance=item["importance"],
                source_chunks=[item["name"]],
            )
            db.add(concept)
            await db.flush()

        created[item["name"]] = concept

        m_res = await db.execute(
            select(LearnerConceptMastery).where(
                LearnerConceptMastery.user_id == user_id,
                LearnerConceptMastery.concept_id == concept.id,
            )
        )
        mastery = m_res.scalar_one_or_none()
        if not mastery:
            mastery = LearnerConceptMastery(
                user_id=user_id,
                concept_id=concept.id,
            )
            db.add(mastery)

        _apply_initial_mastery(mastery, item)
    await db.flush()
    return created


def _apply_initial_mastery(mastery: LearnerConceptMastery, item: Dict[str, Any]) -> None:
    mastery.mastery_score = item["mastery"]
    mastery.total_attempts = 20
    mastery.correct_attempts = int(20 * item["mastery"] / 100)
    mastery.accuracy = item["mastery"]
    mastery.recent_accuracy = item["mastery"]
    mastery.difficulty_distribution = {"easy": 8, "medium": 8, "hard": 4}
    mastery.last_attempted = datetime.now() - timedelta(hours=2)
    mastery.consecutive_correct = 3 if item["mastery"] > 70 else 1
    mastery.consecutive_incorrect = 2 if item["mastery"] < 50 else 0
    mastery.confidence = 0.7 if item["mastery"] > 70 else 0.4
    mastery.learning_status = item["status"]


async def _ensure_relationships(db: AsyncSession, concepts: Dict[str, Concept]) -> None:
    for source_name, target_name, rel_type, confidence in RELATIONSHIPS:
        source = concepts.get(source_name)
        target = concepts.get(target_name)
        if not source or not target:
            continue
        existing = await db.execute(
            select(ConceptRelationship).where(
                ConceptRelationship.source_concept_id == source.id,
                ConceptRelationship.target_concept_id == target.id,
                ConceptRelationship.relationship_type == rel_type,
            )
        )
        if existing.scalar_one_or_none():
            continue
        db.add(
            ConceptRelationship(
                source_concept_id=source.id,
                target_concept_id=target.id,
                relationship_type=rel_type,
                confidence=confidence,
            )
        )
    await db.flush()


async def _seed_activity(db: AsyncSession, user_id: int, document_id: int) -> None:
    existing = await db.execute(
        select(LearningActivity).where(LearningActivity.user_id == user_id).limit(1)
    )
    if existing.scalar_one_or_none():
        return
    db.add(
        LearningActivity(
            user_id=user_id,
            document_id=document_id,
            activity_type="document_upload",
            activity_metadata={"title": DEMO_DOCUMENT_TITLE},
        )
    )


async def create_demo_data(db: AsyncSession) -> Dict[str, Any]:
    user = await get_or_create_demo_user(db)
    document = await _ensure_document(db, user.id)
    concepts = await _upsert_concepts(db, document.id, user.id)
    await _ensure_relationships(db, concepts)
    await _seed_activity(db, user.id, document.id)
    await db.commit()
    return {
        "message": "Demo data initialized successfully",
        "user_id": user.id,
        "email": DEMO_USER_EMAIL,
        "document_id": document.id,
        "concepts": len(concepts),
    }


async def reset_demo_data(db: AsyncSession) -> Dict[str, Any]:
    user = await get_or_create_demo_user(db)
    document = await _ensure_document(db, user.id)

    quiz_ids = (
        await db.execute(select(Quiz.id).where(Quiz.user_id == user.id))
    ).scalars().all()
    if quiz_ids:
        attempt_ids = (
            await db.execute(select(QuizAttempt.id).where(QuizAttempt.quiz_id.in_(quiz_ids)))
        ).scalars().all()
        if attempt_ids:
            await db.execute(delete(QuestionResult).where(QuestionResult.attempt_id.in_(attempt_ids)))
            await db.execute(delete(QuizAttempt).where(QuizAttempt.id.in_(attempt_ids)))
        await db.execute(delete(Question).where(Question.quiz_id.in_(quiz_ids)))
        await db.execute(delete(Quiz).where(Quiz.id.in_(quiz_ids)))

    await db.execute(delete(LearningActivity).where(LearningActivity.user_id == user.id))

    concepts = await _upsert_concepts(db, document.id, user.id)
    await _ensure_relationships(db, concepts)
    await _seed_activity(db, user.id, document.id)
    await db.commit()
    return {
        "message": "Demo data reset successfully",
        "user_id": user.id,
        "document_id": document.id,
    }
