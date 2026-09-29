import google.generativeai as genai
import json
from typing import Dict, List, Any, Optional
from app.core.config import settings
from app.ai.prompts import PromptTemplates


class AIService:
    """AI service for content generation and analysis."""

    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.available = True
        else:
            self.available = False
            print("Warning: GEMINI_API_KEY not configured. AI features will use demo mode.")

    def _generate_content(self, prompt: str) -> str:
        """Generate content using AI model."""
        if not self.available:
            raise ValueError("AI service not available. Check GEMINI_API_KEY.")

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"AI generation error: {e}")
            raise

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from AI."""
        try:
            # Clean response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response[:500]}")
            raise

    def extract_concepts(self, document_text: str) -> List[Dict[str, Any]]:
        """Extract concepts from document text."""
        prompt = PromptTemplates.concept_extraction_prompt(document_text)
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        return result.get("concepts", [])

    def extract_relationships(
        self,
        concepts: List[str],
        document_text: str
    ) -> List[Dict[str, Any]]:
        """Extract relationships between concepts."""
        prompt = PromptTemplates.relationship_extraction_prompt(concepts, document_text)
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        relationships = result.get("relationships", [])

        # Normalize field names for backward compatibility
        for rel in relationships:
            if "type" in rel and "relationship_type" not in rel:
                rel["relationship_type"] = rel["type"]

        return relationships

    def generate_summary(
        self,
        document_text: str,
        concepts: List[str]
    ) -> Dict[str, Any]:
        """Generate structured summary."""
        prompt = PromptTemplates.summary_prompt(document_text, concepts)
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        return result

    def generate_quiz(
        self,
        concept: str,
        concept_description: str,
        difficulty: str = "medium",
        num_questions: int = 5,
        learner_mastery: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions for a concept."""
        prompt = PromptTemplates.quiz_generation_prompt(
            concept, concept_description, difficulty, num_questions, learner_mastery
        )
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        return result.get("questions", [])

    def generate_explanation(
        self,
        concept: str,
        description: str,
        learner_mastery: float,
        explanation_style: str = "detailed"
    ) -> Dict[str, Any]:
        """Generate explanation adapted to learner level."""
        prompt = PromptTemplates.explanation_prompt(
            concept, description, learner_mastery, explanation_style
        )
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        return result

    def answer_question(
        self,
        question: str,
        relevant_chunks: List[str]
    ) -> str:
        """Answer question based on document chunks (RAG)."""
        prompt = PromptTemplates.question_answer_prompt(question, relevant_chunks)
        return self._generate_content(prompt)

    def generate_recommendation(
        self,
        weak_topics: List[Dict[str, Any]],
        learner_mastery: Dict[str, float],
        recent_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate next best action recommendation."""
        prompt = PromptTemplates.recommendation_prompt(
            weak_topics, learner_mastery, recent_performance
        )
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        return result

    def generate_adaptive_quiz(
        self,
        target_concept: str,
        prerequisites: List[str],
        learner_mastery: float,
        recent_mistakes: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate adaptive quiz questions."""
        prompt = PromptTemplates.adaptive_quiz_prompt(
            target_concept, prerequisites, learner_mastery, recent_mistakes
        )
        response = self._generate_content(prompt)
        result = self._parse_json_response(response)
        return result.get("questions", [])


# Singleton instance
ai_service = AIService()
