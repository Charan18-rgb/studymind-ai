from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import ai_service
from app.models.concept import Concept, LearnerConceptMastery
from app.models.document import Document
from app.core.config import settings
from app.models.quiz import Question, Quiz
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.mastery_service import MasteryService
from app.services.weak_topic_service import weak_topic_service


class AdaptiveLearningService:
    @staticmethod
    async def create_session(
        user_id: int,
        db: AsyncSession,
        document_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        weak_topics = await weak_topic_service.get_weak_topics(user_id, db, limit=5)
        if not weak_topics:
            return {"message": "No assessed concepts yet. Upload study material and complete an assessment to begin adaptive learning.", "session": None}

        target = weak_topics[0]
        concept_result = await db.execute(
            select(Concept).join(Document).where(Concept.id == target["concept_id"], Document.user_id == user_id)
        )
        concept = concept_result.scalar_one_or_none()
        if not concept:
            return {"message": "Concept not found", "session": None}

        if not document_id:
            document_id = concept.document_id

        prerequisites = await knowledge_graph_service.get_prerequisites(concept.id, db, user_id=user_id)
        mastery_map = await knowledge_graph_service.get_mastery_map(user_id, db)

        difficulty = MasteryService.get_difficulty_for_mastery(target["mastery"])

        if ai_service.available:
            try:
                questions_data = ai_service.generate_adaptive_quiz(
                    target_concept=concept.name,
                    prerequisites=[p.name for p in prerequisites],
                    learner_mastery=target["mastery"],
                    recent_mistakes=[],
                )
            except Exception:
                questions_data = []
        else:
            from app.models.user import User
            learner = await db.get(User, user_id)
            questions_data = AdaptiveLearningService._demo_questions(concept, difficulty) if settings.demo_mode and learner and learner.is_demo else []
        questions_data = AdaptiveLearningService._validated_questions(questions_data)
        if not questions_data:
            return {"message": "Adaptive questions are temporarily unavailable. Try again later.", "session": None}

        quiz = Quiz(
            document_id=document_id,
            user_id=user_id,
            title=f"Adaptive: {concept.name}",
            quiz_type="adaptive_session",
            difficulty=difficulty,
            question_count=len(questions_data),
            concepts=[concept.id],
        )
        db.add(quiz)
        await db.flush()

        stored_questions = []
        for idx, q in enumerate(questions_data):
            concept_id = q.get("concept_id", concept.id)
            question = Question(
                quiz_id=quiz.id,
                concept_id=concept_id,
                question_text=q["question_text"],
                question_type=q.get("question_type", "multiple_choice"),
                options=q.get("options", []),
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation", ""),
                difficulty=q.get("difficulty", difficulty),
                order=idx,
            )
            db.add(question)
            await db.flush()
            stored_questions.append(
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "options": question.options,
                    "difficulty": question.difficulty,
                    "focus_area": q.get("focus_area"),
                }
            )

        prereq_payload = []
        for p in prerequisites:
            m = mastery_map.get(p.id)
            prereq_payload.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "mastery": m.mastery_score if m else None,
                }
            )

        return {
            "session": {
                "session_id": quiz.id,
                "target_concept": {
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description,
                    "current_mastery": target["mastery"],
                },
                "prerequisites": prereq_payload,
                "difficulty": difficulty,
                "questions": stored_questions,
                "focus_areas": AdaptiveLearningService._focus_areas(target["mastery"]),
            }
        }

    @staticmethod
    def _focus_areas(mastery: float) -> List[str]:
        if mastery < 40:
            return ["Foundational understanding", "Tree traversal basics"]
        if mastery < 60:
            return ["Core concepts application", "Recursion in trees"]
        return ["Advanced problem-solving"]

    @staticmethod
    def _validated_questions(items: Any) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []
        valid = []
        for item in items:
            if not isinstance(item, dict):
                continue
            prompt, options, answer = item.get("question_text"), item.get("options"), item.get("correct_answer")
            if (isinstance(prompt, str) and prompt.strip()
                    and isinstance(options, list) and len(options) >= 2
                    and all(isinstance(option, str) and option.strip() for option in options)
                    and isinstance(answer, str) and answer in options):
                valid.append(item)
        return valid

    @staticmethod
    def _demo_questions(concept: Concept, difficulty: str) -> List[Dict[str, Any]]:
        base = concept.name
        items = [
            (
                f"What is the primary purpose of {base} in computer science?",
                ["Store hierarchical data", "Sort numbers only", "Replace arrays entirely", "Compile code"],
                "Store hierarchical data",
                f"{base} models hierarchical relationships, which is essential for search and organization.",
            ),
            (
                f"Which traversal visits the root node first in a binary tree?",
                ["Pre-order", "In-order", "Post-order", "Level-order only"],
                "Pre-order",
                "Pre-order traversal processes the root before its subtrees.",
            ),
            (
                f"Why is recursion commonly used with {base}?",
                ["Subproblems mirror subtrees", "Recursion is always faster", "It avoids memory", "It removes base cases"],
                "Subproblems mirror subtrees",
                "Recursive calls naturally match left/right subtree structure.",
            ),
            (
                f"What is a common mistake when learning {base} traversal?",
                ["Forgetting base cases in recursion", "Using too many arrays", "Avoiding pointers", "Using BFS only"],
                "Forgetting base cases in recursion",
                "Missing base cases causes infinite recursion during traversal.",
            ),
            (
                f"Which skill most directly supports mastering {base}?",
                ["Recursion fundamentals", "HTML styling", "File compression", "Network ports"],
                "Recursion fundamentals",
                "Recursion underpins many tree traversal algorithms.",
            ),
        ]
        questions = []
        for i, (text, options, correct, explanation) in enumerate(items):
            questions.append(
                {
                    "question_text": text,
                    "question_type": "multiple_choice",
                    "options": options,
                    "correct_answer": correct,
                    "explanation": explanation,
                    "difficulty": difficulty if difficulty in ("easy", "medium", "hard") else "medium",
                    "focus_area": "Tree traversal",
                    "concept_id": concept.id,
                }
            )
        return questions


adaptive_learning_service = AdaptiveLearningService()
