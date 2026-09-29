"""
AI Prompt Templates for StudyMind AI
Centralized prompt management for consistent AI responses.
"""

from typing import List, Dict, Any


class PromptTemplates:
    """Collection of AI prompt templates."""

    @staticmethod
    def concept_extraction_prompt(document_text: str) -> str:
        """Extract concepts and topics from document text."""
        return f"""You are an educational content analyzer. Extract the key concepts and topics from the following study material.

Document text:
{document_text}

Return a JSON object with this exact structure:
{{
    "concepts": [
        {{
            "name": "Concept Name",
            "description": "Brief description of what this concept is",
            "difficulty": "easy|medium|hard",
            "importance": 0.5,
            "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
            "related_concepts": ["Related 1", "Related 2"]
        }}
    ]
}}

Guidelines:
- Extract 5-15 most important concepts
- Difficulty should reflect complexity relative to the document
- Importance is 0.0 to 1.0 based on centrality to the material
- Only include prerequisites that are clearly required before understanding this concept
- Related concepts should be those that are often studied together
- Return ONLY valid JSON, no other text"""

    @staticmethod
    def relationship_extraction_prompt(concepts: List[str], document_text: str) -> str:
        """Extract relationships between concepts."""
        concepts_list = "\n".join([f"- {c}" for c in concepts])
        return f"""You are an educational content analyzer. Identify relationships between these concepts from the study material.

Concepts:
{concepts_list}

Document text:
{document_text}

Return a JSON object with this exact structure:
{{
    "relationships": [
        {{
            "source": "Concept A",
            "target": "Concept B",
            "relationship_type": "prerequisite|related|depends_on",
            "confidence": 0.8
        }}
    ]
}}

Relationship types:
- prerequisite: Concept A must be understood before Concept B
- related: Concepts are often studied together or connected
- depends_on: Concept B depends on Concept A being applied

Confidence is 0.0 to 1.0 based on how clearly the relationship is stated.
Return ONLY valid JSON, no other text."""

    @staticmethod
    def summary_prompt(document_text: str, concepts: List[str]) -> str:
        """Generate structured summary of document."""
        concepts_str = ", ".join(concepts)
        return f"""You are an educational content summarizer. Create a structured summary of this study material.

Key concepts covered: {concepts_str}

Document text:
{document_text}

Return a JSON object with this exact structure:
{{
    "overview": "2-3 sentence overview of the entire document",
    "key_concepts": [
        {{"name": "Concept", "description": "Brief explanation"}}
    ],
    "important_definitions": [
        {{"term": "Term", "definition": "Definition"}}
    ],
    "important_formulas": [
        {{"formula": "Formula", "description": "What it means"}}
    ],
    "exam_points": [
        "Point 1",
        "Point 2"
    ],
    "common_mistakes": [
        "Mistake 1",
        "Mistake 2"
    ],
    "quick_revision": "Concise revision summary in 3-5 bullet points"
}}

Return ONLY valid JSON, no other text."""

    @staticmethod
    def quiz_generation_prompt(
        concept: str,
        concept_description: str,
        difficulty: str,
        num_questions: int,
        learner_mastery: float = 0.0
    ) -> str:
        """Generate quiz questions for a specific concept."""
        mastery_context = ""
        if learner_mastery < 40:
            mastery_context = "The learner is struggling with this concept. Focus on foundational understanding."
        elif learner_mastery < 70:
            mastery_context = "The learner has moderate understanding. Include both basic and intermediate questions."
        else:
            mastery_context = "The learner has good understanding. Include challenging application questions."

        return f"""You are an educational quiz generator. Create questions for this concept.

Concept: {concept}
Description: {concept_description}
Difficulty: {difficulty}
Number of questions: {num_questions}
Learner context: {mastery_context}

Return a JSON object with this exact structure:
{{
    "questions": [
        {{
            "question_text": "Clear question text",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Why this is correct",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}

Guidelines:
- Questions should test understanding, not just memorization
- Ensure one clear correct answer
- Explanations should be concise and helpful
- Adjust complexity based on requested difficulty
- Return ONLY valid JSON, no other text"""

    @staticmethod
    def explanation_prompt(
        concept: str,
        description: str,
        learner_mastery: float,
        explanation_style: str = "detailed"
    ) -> str:
        """Generate explanation adapted to learner level."""
        level = "beginner" if learner_mastery < 40 else "intermediate" if learner_mastery < 70 else "advanced"

        return f"""You are an educational explainer. Explain this concept to a learner.

Concept: {concept}
Description: {description}
Learner mastery level: {level} ({learner_mastery}%)
Explanation style: {explanation_style}

Return a JSON object with this exact structure:
{{
    "simple_explanation": "Clear, accessible explanation",
    "real_world_analogy": "Real-world comparison if applicable",
    "example": "Concrete example",
    "common_mistakes": ["Mistake 1", "Mistake 2"],
    "quick_check": "One question to test understanding"
}}

Guidelines:
- Adapt complexity to learner's mastery level
- Use analogies for complex topics
- Include practical examples
- Highlight common pitfalls
- Return ONLY valid JSON, no other text"""

    @staticmethod
    def question_answer_prompt(question: str, relevant_chunks: List[str]) -> str:
        """Answer question based on document chunks (RAG)."""
        chunks_text = "\n\n".join([f"Chunk {i+1}: {chunk}" for i, chunk in enumerate(relevant_chunks)])

        return f"""You are a helpful study assistant. Answer the student's question based ONLY on the provided document chunks.

Question: {question}

Relevant document chunks:
{chunks_text}

If the answer is not clearly available in the chunks, say: "I couldn't find this information in your uploaded material."

Provide a concise, accurate answer with the source chunk reference.
Return the answer as plain text."""

    @staticmethod
    def recommendation_prompt(
        weak_topics: List[Dict[str, Any]],
        learner_mastery: Dict[str, float],
        recent_performance: Dict[str, Any]
    ) -> str:
        """Generate next best action recommendation."""
        weak_topics_str = "\n".join([
            f"- {t['name']}: {t['mastery']}% (recent: {t['recent_accuracy']}%)"
            for t in weak_topics
        ])

        return f"""You are an adaptive learning recommendation engine. Suggest the single most useful next learning action.

Weak topics:
{weak_topics_str}

Recent performance:
{recent_performance}

Return a JSON object with this exact structure:
{{
    "target_concept": "Concept name to focus on",
    "action": "practice|review|read|quiz",
    "title": "Clear action title",
    "description": "Why this is the next best action",
    "duration_minutes": 15,
    "reason": "Brief explanation of reasoning"
}}

Guidelines:
- Focus on foundational weaknesses first
- Consider prerequisite relationships
- Balance between review and new practice
- Prioritize topics with recent poor performance
- Return ONLY valid JSON, no other text"""

    @staticmethod
    def adaptive_quiz_prompt(
        target_concept: str,
        prerequisites: List[str],
        learner_mastery: float,
        recent_mistakes: List[str]
    ) -> str:
        """Generate adaptive quiz questions based on learner state."""
        prerequisites_str = ", ".join(prerequisites) if prerequisites else "None"
        mistakes_str = "\n".join([f"- {m}" for m in recent_mistakes]) if recent_mistakes else "None"

        return f"""You are an adaptive quiz generator. Create targeted questions based on learner performance.

Target concept: {target_concept}
Prerequisites: {prerequisites_str}
Learner mastery: {learner_mastery}%
Recent mistakes:
{mistakes_str}

Return a JSON object with this exact structure:
{{
    "questions": [
        {{
            "question_text": "Targeted question",
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Explanation",
            "difficulty": "easy|medium|hard",
            "focus_area": "What this question addresses"
        }}
    ]
}}

Guidelines:
- Include prerequisite questions if mastery is low
- Focus on mistake patterns
- Start easier, progress to harder
- Address specific weak areas
- Return ONLY valid JSON, no other text"""
