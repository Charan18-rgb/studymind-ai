from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import ai_service
from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.models.concept import Concept as ConceptModel
from app.models.concept import LearnerConceptMastery as MasteryModel
from app.models.document import Document
from app.schemas.concept import Concept, ConceptWithMastery, LearnerConceptMastery as LearnerMasterySchema
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.weak_topic_service import weak_topic_service

router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.get("/graph")
async def get_knowledge_graph(
    document_id: Optional[int] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if document_id:
        owned = await db.scalar(select(Document.id).where(Document.id == document_id, Document.user_id == user_id))
        if not owned:
            raise HTTPException(status_code=404, detail="Document not found")
    else:
        # Prefer a document that has an extracted graph. A valid upload can be
        # retained even when AI extraction is unavailable; it should not hide
        # an existing graph for that same learner.
        document_id = await db.scalar(
            select(Document.id)
            .join(ConceptModel, ConceptModel.document_id == Document.id)
            .where(Document.user_id == user_id)
            .group_by(Document.id)
            .order_by(Document.created_at.desc())
            .limit(1)
        )
        if not document_id:
            document_id = await db.scalar(
                select(Document.id)
                .where(Document.user_id == user_id)
                .order_by(Document.created_at.desc())
                .limit(1)
            )
    if not document_id:
        return {"document_id": None, "nodes": [], "edges": []}
    return await knowledge_graph_service.get_graph_for_document(document_id, user_id, db)


@router.get("/learner/mastery", response_model=List[LearnerMasterySchema])
async def get_learner_mastery(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MasteryModel).join(ConceptModel).join(Document).where(MasteryModel.user_id == user_id, Document.user_id == user_id))
    return result.scalars().all()


@router.get("/learner/weak-topics")
async def get_weak_topics(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await weak_topic_service.get_weak_topics(user_id, db)


@router.get("/learner/diagnosis")
async def get_weak_topic_diagnosis(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await weak_topic_service.diagnose(user_id, db)


@router.get("/document/{document_id}", response_model=List[Concept])
async def get_document_concepts(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ConceptModel).where(ConceptModel.document_id == document_id))
    owned = await db.scalar(select(Document.id).where(Document.id == document_id, Document.user_id == user_id))
    if not owned:
        raise HTTPException(status_code=404, detail="Document not found")
    return result.scalars().all()


@router.get("/{concept_id}/explanation")
async def get_adaptive_explanation(
    concept_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generate adaptive explanation tailored to the learner's current mastery level."""
    result = await db.execute(select(ConceptModel).join(Document).where(ConceptModel.id == concept_id, Document.user_id == user_id))
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    mastery = await db.scalar(select(MasteryModel).where(MasteryModel.user_id == user_id, MasteryModel.concept_id == concept_id))
    mastery_score = mastery.mastery_score if mastery else 0.0

    prerequisites = await knowledge_graph_service.get_prerequisites(concept_id, db)
    prereq_names = [p.name for p in prerequisites]

    if ai_service.available:
        try:
            ai_exp = ai_service.generate_explanation(
                concept=concept.name,
                description=concept.description or "",
                learner_mastery=mastery_score,
            )
            return {
                "concept_id": concept.id,
                "concept_name": concept.name,
                "learner_mastery": mastery_score,
                "learning_status": mastery.learning_status if mastery else "not_assessed",
                "prerequisites": prereq_names,
                **ai_exp,
            }
        except Exception:
            pass  # Fall back to template explanation

    # High quality tailored fallback explanation based on mastery level
    level_label = (
        "Foundational (Targeting Gaps)"
        if mastery_score < 40
        else "Developing (Core Skills)"
        if mastery_score < 70
        else "Advanced (Mastery)"
    )

    concept_explanations = {
        "Trees": {
            "simple_explanation": "A tree is a hierarchical data structure composed of nodes. The top node is the root, and each node can connect to child nodes. Binary trees restrict each node to at most two children (left and right).",
            "real_world_analogy": "Think of a company org chart: the CEO is the root at the top, managers are intermediate branch nodes, and team contributors are leaf nodes.",
            "example": "In a Binary Search Tree (BST), every node to the left has a smaller value, and every node to the right has a larger value. Searching is fast: O(log n).",
            "common_mistakes": [
                "Forgetting the base case when traversing recursively (causing stack overflow)",
                "Confusing depth (distance from root) with height (longest path to leaf)",
                "Assuming binary trees are automatically balanced",
            ],
            "quick_check": "In a binary tree, what is the maximum number of children any single node can have?",
            "why_this_matters": "Trees power filesystem directories, database indexes (B-Trees), and AI decision algorithms.",
        },
        "Recursion": {
            "simple_explanation": "Recursion is when a function calls itself to solve smaller subproblems until it reaches a simple, terminating base case.",
            "real_world_analogy": "Like Russian nesting dolls (Matryoshka) — you open each doll to find a smaller one inside until you reach the smallest solid doll (base case).",
            "example": "Tree traversal: traverse(root.left) then traverse(root.right). Each subtree is itself a tree!",
            "common_mistakes": [
                "Missing the base case, leading to infinite recursion",
                "Not reducing problem size in the recursive step",
                "Excessive memory overhead on call stack without memoization",
            ],
            "quick_check": "What happens if a recursive function never reaches its base case?",
            "why_this_matters": "Recursion is the foundational prerequisite for tree/graph traversals and divide-and-conquer algorithms.",
        },
    }

    base = concept_explanations.get(
        concept.name,
        {
            "simple_explanation": f"{concept.name} is a key concept: {concept.description}.",
            "real_world_analogy": f"Think of {concept.name} as an organized way to manage and process related data efficiently.",
            "example": f"Applying {concept.name} simplifies complex problem solving into structured steps.",
            "common_mistakes": [
                f"Skipping prerequisite concepts before studying {concept.name}",
                "Not practicing edge cases and boundary conditions",
            ],
            "quick_check": f"What is the primary advantage of using {concept.name}?",
            "why_this_matters": f"Mastering {concept.name} builds the foundation for advanced algorithms and system design.",
        },
    )

    return {
        "concept_id": concept.id,
        "concept_name": concept.name,
        "learner_mastery": mastery_score,
        "learning_status": mastery.learning_status if mastery else "not_assessed",
        "level_label": level_label,
        "prerequisites": prereq_names,
        **base,
    }


@router.get("/{concept_id}", response_model=ConceptWithMastery)
async def get_concept(
    concept_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ConceptModel).join(Document).where(ConceptModel.id == concept_id, Document.user_id == user_id))
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    mastery_result = await db.execute(
        select(MasteryModel).where(
            MasteryModel.concept_id == concept_id,
            MasteryModel.user_id == user_id,
        )
    )
    mastery = mastery_result.scalar_one_or_none()
    return ConceptWithMastery(**concept.__dict__, learner_mastery=mastery)
