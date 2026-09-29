from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import LearningActivity
from app.models.concept import Concept
from app.models.quiz import Question, QuestionResult, Quiz, QuizAttempt
from app.services.mastery_persistence import apply_question_result
from app.services.recommendation_service import recommendation_service


class QuizService:
    @staticmethod
    async def submit_quiz(
        user_id: int,
        quiz_id: int,
        answers: List[Dict[str, Any]],
        db: AsyncSession,
        track_concept_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quiz_result.scalar_one_or_none()
        if not quiz:
            raise ValueError("Quiz not found")

        q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
        questions = {q.id: q for q in q_result.scalars().all()}

        before_mastery: Optional[float] = None
        target_concept_name: Optional[str] = None
        if track_concept_id:
            from app.services.mastery_persistence import get_or_create_mastery

            m = await get_or_create_mastery(user_id, track_concept_id, db)
            before_mastery = m.mastery_score
            c_res = await db.execute(select(Concept).where(Concept.id == track_concept_id))
            c = c_res.scalar_one_or_none()
            target_concept_name = c.name if c else None

        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            total_questions=len(answers),
            correct_answers=0,
            score=0.0,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        await db.flush()

        correct_count = 0

        for ans in answers:
            qid = ans.get("question_id")
            selected = ans.get("selected_answer", "")
            question = questions.get(qid)
            if not question:
                continue

            is_correct = selected.strip() == question.correct_answer.strip()
            if is_correct:
                correct_count += 1

            db.add(
                QuestionResult(
                    attempt_id=attempt.id,
                    question_id=question.id,
                    concept_id=question.concept_id,
                    user_answer=selected,
                    is_correct=is_correct,
                    time_spent_seconds=ans.get("time_spent_seconds", 0),
                )
            )

            if question.concept_id:
                await apply_question_result(
                    user_id,
                    question.concept_id,
                    is_correct,
                    question.difficulty or "medium",
                    db,
                )

        attempt.correct_answers = correct_count
        attempt.total_questions = max(len(answers), 1)
        attempt.score = round((correct_count / attempt.total_questions) * 100, 1)

        db.add(
            LearningActivity(
                user_id=user_id,
                activity_type="quiz_attempt",
                document_id=quiz.document_id,
                activity_metadata={
                    "quiz_id": quiz_id,
                    "score": attempt.score,
                    "correct": correct_count,
                    "total": attempt.total_questions,
                    "questions_completed": attempt.total_questions,
                },
            )
        )

        after_mastery = before_mastery
        if track_concept_id:
            from app.services.mastery_persistence import get_or_create_mastery

            m_after = await get_or_create_mastery(user_id, track_concept_id, db)
            after_mastery = m_after.mastery_score

        next_action = await recommendation_service.get_next_best_action(user_id, db)

        improvement = None
        if before_mastery is not None and after_mastery is not None:
            improvement = round(after_mastery - before_mastery, 1)

        return {
            "quiz_id": quiz_id,
            "attempt_id": attempt.id,
            "score": attempt.score,
            "correct_answers": correct_count,
            "total_questions": attempt.total_questions,
            "concept": target_concept_name,
            "concept_id": track_concept_id,
            "before_mastery": before_mastery,
            "after_mastery": after_mastery,
            "improvement": improvement,
            "next_action": next_action,
        }


quiz_service = QuizService()
