import pytest
from app.services.mastery_service import MasteryService
from app.services.recommendation_service import RecommendationService


def test_mastery_calculation_non_zero_after_attempts():
    result = MasteryService.calculate_mastery(
        total_attempts=10,
        correct_attempts=7,
        recent_accuracy=70.0,
        difficulty_distribution={"easy": 4, "medium": 4, "hard": 2},
        consecutive_correct=2,
        consecutive_incorrect=0,
        confidence=0.6,
    )
    assert 0 < result["mastery_score"] <= 100
    assert result["learning_status"] in {
        "needs_foundation",
        "developing",
        "proficient",
        "mastered",
        "not_studied",
    }


def test_mastery_update_increases_on_correct():
    base = {
        "total_attempts": 20,
        "correct_attempts": 8,
        "recent_accuracy": 42.0,
        "difficulty_distribution": {"easy": 5, "medium": 10, "hard": 5},
        "consecutive_correct": 0,
        "consecutive_incorrect": 2,
        "confidence": 0.4,
        "accuracy": 40.0,
        "mastery_score": 42.0,
        "learning_status": "needs_foundation",
    }
    updated = MasteryService.update_mastery_after_attempt(base, True, "medium")
    assert updated["mastery_score"] >= 42.0
    assert updated["total_attempts"] == 21
    assert updated["correct_attempts"] == 9


def test_recommendation_start_action_when_empty():
    action = RecommendationService._start_action()
    assert action["action"] == "upload"
