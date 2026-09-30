import json
import logging
import time
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.ai.prompts import PromptTemplates
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Google Gemini integration. The API key and client remain backend-only."""

    def __init__(self):
        self.client = None
        self.available = bool(settings.gemini_api_key)
        self.model_name = "gemini-3.1-flash-lite"
        if self.available:
            try:
                self.client = genai.Client(api_key=settings.gemini_api_key)
            except Exception:
                self.available = False
                logger.exception("Gemini client initialization failed")
        else:
            logger.warning("GEMINI_API_KEY is not configured. AI-backed features are unavailable.")

    def _generate_content(self, prompt: str, json_response: bool = False) -> str:
        if not self.available or self.client is None:
            raise RuntimeError("AI service is not configured")
        config = types.GenerateContentConfig(
            response_mime_type="application/json" if json_response else "text/plain",
            temperature=0.2,
        )
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                text = response.text
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("Gemini returned an empty response")
                return text
            except Exception as exc:
                status = getattr(exc, "code", None) or getattr(exc, "status_code", None)
                if status in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(0.75 * (2 ** attempt))
                    continue
                # Provider exceptions may include request metadata. Never log their contents or the API key.
                logger.error("Gemini generation request failed (%s, status=%s)", type(exc).__name__, status)
                raise RuntimeError("Gemini generation request failed") from None

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(response.strip())
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Gemini returned malformed JSON")
            raise ValueError("Gemini returned malformed structured content") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Gemini structured response must be an object")
        return parsed

    def extract_concepts(self, document_text: str) -> List[Dict[str, Any]]:
        result = self._parse_json_response(self._generate_content(
            PromptTemplates.concept_extraction_prompt(document_text), json_response=True
        ))
        concepts = result.get("concepts")
        if not isinstance(concepts, list):
            raise ValueError("Gemini returned invalid concepts")
        return concepts

    def extract_relationships(self, concepts: List[str], document_text: str) -> List[Dict[str, Any]]:
        result = self._parse_json_response(self._generate_content(
            PromptTemplates.relationship_extraction_prompt(concepts, document_text), json_response=True
        ))
        relationships = result.get("relationships")
        if not isinstance(relationships, list):
            raise ValueError("Gemini returned invalid relationships")
        normalized = []
        for item in relationships:
            if isinstance(item, dict) and "type" in item and "relationship_type" not in item:
                item = {**item, "relationship_type": item["type"]}
            normalized.append(item)
        return normalized

    def generate_summary(self, document_text: str, concepts: List[str]) -> Dict[str, Any]:
        return self._parse_json_response(self._generate_content(
            PromptTemplates.summary_prompt(document_text, concepts), json_response=True
        ))

    def generate_quiz(self, concept: str, concept_description: str, difficulty: str = "medium", num_questions: int = 5, learner_mastery: float = 0.0) -> List[Dict[str, Any]]:
        prompt = PromptTemplates.quiz_generation_prompt(concept, concept_description, difficulty, num_questions, learner_mastery)
        questions = self._parse_json_response(self._generate_content(prompt, json_response=True)).get("questions")
        if not isinstance(questions, list):
            raise ValueError("Gemini returned invalid quiz questions")
        return questions

    def generate_explanation(self, concept: str, description: str, learner_mastery: float, explanation_style: str = "detailed") -> Dict[str, Any]:
        prompt = PromptTemplates.explanation_prompt(concept, description, learner_mastery, explanation_style)
        return self._parse_json_response(self._generate_content(prompt, json_response=True))

    def answer_question(self, question: str, relevant_chunks: List[str]) -> str:
        return self._generate_content(PromptTemplates.question_answer_prompt(question, relevant_chunks))

    def generate_recommendation(self, weak_topics: List[Dict[str, Any]], learner_mastery: Dict[str, float], recent_performance: Dict[str, Any]) -> Dict[str, Any]:
        prompt = PromptTemplates.recommendation_prompt(weak_topics, learner_mastery, recent_performance)
        return self._parse_json_response(self._generate_content(prompt, json_response=True))

    def generate_adaptive_quiz(self, target_concept: str, prerequisites: List[str], learner_mastery: float, recent_mistakes: List[str]) -> List[Dict[str, Any]]:
        prompt = PromptTemplates.adaptive_quiz_prompt(target_concept, prerequisites, learner_mastery, recent_mistakes)
        questions = self._parse_json_response(self._generate_content(prompt, json_response=True)).get("questions")
        if not isinstance(questions, list):
            raise ValueError("Gemini returned invalid adaptive questions")
        return questions


ai_service = AIService()
