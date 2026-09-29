from typing import Dict, List, Any
from datetime import datetime, timedelta


class MasteryService:
    """
    Calculate and update learner concept mastery.

    Mastery Algorithm:
    - 30% recent performance (last 5 attempts)
    - 25% historical performance (all time)
    - 20% difficulty-adjusted performance
    - 15% consistency (consecutive correct vs incorrect)
    - 10% confidence/self-assessment

    Final score: 0-100
    """

    # Learning status thresholds (configurable)
    STATUS_THRESHOLDS = {
        "needs_foundation": 39,
        "developing": 59,
        "proficient": 79,
        "mastered": 100
    }

    @staticmethod
    def calculate_mastery(
        total_attempts: int,
        correct_attempts: int,
        recent_accuracy: float,
        difficulty_distribution: Dict[str, int],
        consecutive_correct: int,
        consecutive_incorrect: int,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calculate mastery score based on multiple factors.

        Returns dict with:
        - mastery_score: 0-100
        - learning_status: str
        - breakdown: Dict with component scores
        """

        if total_attempts == 0:
            return {
                "mastery_score": 0.0,
                "learning_status": "not_studied",
                "breakdown": {
                    "recent_performance": 0.0,
                    "historical_performance": 0.0,
                    "difficulty_adjusted": 0.0,
                    "consistency": 0.5,
                    "confidence": confidence
                }
            }

        # 1. Recent performance (30%)
        recent_score = recent_accuracy * 0.3

        # 2. Historical performance (25%)
        historical_accuracy = (correct_attempts / total_attempts) * 100
        historical_score = historical_accuracy * 0.25

        # 3. Difficulty-adjusted performance (20%)
        difficulty_score = MasteryService._calculate_difficulty_score(
            difficulty_distribution, correct_attempts, total_attempts
        ) * 0.2

        # 4. Consistency (15%)
        consistency_score = MasteryService._calculate_consistency_score(
            consecutive_correct, consecutive_incorrect
        ) * 0.15

        # 5. Confidence (10%)
        confidence_score = confidence * 10

        # Combine scores
        mastery_score = (
            recent_score +
            historical_score +
            difficulty_score +
            consistency_score +
            confidence_score
        )

        # Clamp to 0-100
        mastery_score = max(0.0, min(100.0, mastery_score))

        # Determine learning status
        learning_status = MasteryService._determine_status(mastery_score)

        return {
            "mastery_score": round(mastery_score, 1),
            "learning_status": learning_status,
            "breakdown": {
                "recent_performance": round(recent_score, 1),
                "historical_performance": round(historical_score, 1),
                "difficulty_adjusted": round(difficulty_score, 1),
                "consistency": round(consistency_score, 1),
                "confidence": round(confidence_score, 1)
            }
        }

    @staticmethod
    def _calculate_difficulty_score(
        difficulty_distribution: Dict[str, int],
        correct_attempts: int,
        total_attempts: int
    ) -> float:
        """Calculate difficulty-adjusted performance score."""
        if not difficulty_distribution or total_attempts == 0:
            return 0.0

        easy = difficulty_distribution.get("easy", 0)
        medium = difficulty_distribution.get("medium", 0)
        hard = difficulty_distribution.get("hard", 0)

        # Weight by difficulty
        # Easy: 1x, Medium: 1.5x, Hard: 2x
        weighted_total = easy + (medium * 1.5) + (hard * 2.0)
        total_weighted = easy + medium + hard

        if total_weighted == 0:
            return 0.0

        # Adjust overall accuracy by difficulty factor
        base_accuracy = (correct_attempts / total_attempts) * 100
        difficulty_factor = weighted_total / total_weighted if total_weighted > 0 else 1.0

        return base_accuracy * min(difficulty_factor, 1.2)  # Cap at 1.2x bonus

    @staticmethod
    def _calculate_consistency_score(
        consecutive_correct: int,
        consecutive_incorrect: int
    ) -> float:
        """Calculate consistency score based on streaks."""
        if consecutive_correct == 0 and consecutive_incorrect == 0:
            return 50.0  # Neutral

        # Reward consistency in correct answers
        if consecutive_correct > consecutive_incorrect:
            # 1-3 correct: 60-80
            # 4+ correct: 80-100
            score = min(100.0, 60.0 + (consecutive_correct * 5.0))
        else:
            # Penalize incorrect streaks
            # 1-2 incorrect: 40-30
            # 3+ incorrect: 30-10
            score = max(10.0, 40.0 - (consecutive_incorrect * 10.0))

        return score

    @staticmethod
    def _determine_status(mastery_score: float) -> str:
        """Determine learning status based on mastery score."""
        if mastery_score <= MasteryService.STATUS_THRESHOLDS["needs_foundation"]:
            return "needs_foundation"
        elif mastery_score <= MasteryService.STATUS_THRESHOLDS["developing"]:
            return "developing"
        elif mastery_score <= MasteryService.STATUS_THRESHOLDS["proficient"]:
            return "proficient"
        else:
            return "mastered"

    @staticmethod
    def update_mastery_after_attempt(
        current_mastery: Dict[str, Any],
        is_correct: bool,
        difficulty: str
    ) -> Dict[str, Any]:
        """
        Update mastery data after a single question attempt.

        Returns updated mastery data.
        """
        # Update counts
        current_mastery["total_attempts"] += 1
        if is_correct:
            current_mastery["correct_attempts"] += 1
            current_mastery["consecutive_correct"] += 1
            current_mastery["consecutive_incorrect"] = 0
        else:
            current_mastery["consecutive_incorrect"] += 1
            current_mastery["consecutive_correct"] = 0

        # Update difficulty distribution
        if "difficulty_distribution" not in current_mastery:
            current_mastery["difficulty_distribution"] = {}
        current_mastery["difficulty_distribution"][difficulty] = \
            current_mastery["difficulty_distribution"].get(difficulty, 0) + 1

        # Update accuracy
        current_mastery["accuracy"] = (
            current_mastery["correct_attempts"] / current_mastery["total_attempts"]
        ) * 100

        # Update recent accuracy (simplified exponential moving average)
        current_score = 100 if is_correct else 0
        if current_mastery["recent_accuracy"] == 0:
            current_mastery["recent_accuracy"] = current_score
        else:
            # 30% weight to new attempt, 70% to previous
            current_mastery["recent_accuracy"] = (
                (current_mastery["recent_accuracy"] * 0.7) + (current_score * 0.3)
            )

        # Recalculate mastery score
        mastery_result = MasteryService.calculate_mastery(
            current_mastery["total_attempts"],
            current_mastery["correct_attempts"],
            current_mastery["recent_accuracy"],
            current_mastery["difficulty_distribution"],
            current_mastery["consecutive_correct"],
            current_mastery["consecutive_incorrect"],
            current_mastery.get("confidence", 0.5)
        )

        # Update with new values
        current_mastery["mastery_score"] = mastery_result["mastery_score"]
        current_mastery["learning_status"] = mastery_result["learning_status"]

        return current_mastery

    @staticmethod
    def get_difficulty_for_mastery(mastery_score: float) -> str:
        """Suggest question difficulty based on mastery."""
        if mastery_score < 40:
            return "easy"
        elif mastery_score < 60:
            return "easy_or_medium"
        elif mastery_score < 80:
            return "medium"
        else:
            return "hard"
