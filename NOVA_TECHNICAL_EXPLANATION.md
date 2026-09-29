# NOVA Technical Explanation

StudyMind AI is a continuous loop: document-derived concepts and prerequisite links inform diagnosis; the learner's persisted concept mastery informs practice; assessed answers update that mastery; the updated learner state informs the next recommendation.

## Knowledge model

PDF text is extracted page by page with PyMuPDF and stored as page-aware chunks. Concepts and relationships form a graph, including directed prerequisite links such as Recursion → Trees. Gemini can support AI generation when configured; the prototype also has deterministic demo/fallback behavior. Extraction and generated content can be wrong and should be reviewed.

## Learner model

SQLite stores concept-level learner mastery, accuracy, attempt counts, difficulty counts, recent accuracy, correct/incorrect streaks, and confidence. Assessment history is persisted as quiz attempts and individual `QuestionResult` records.

## Diagnosis

The system orders a learner's concepts by mastery and treats concepts below 70 as weak-topic candidates. It selects the lowest-mastery candidate and checks graph prerequisites; a prerequisite below 60 is considered weak by the diagnosis/recommendation path. This helps identify a foundational gap associated with a weak target.

## Adaptation

Adaptive practice targets the lowest-mastery weak concept. Its current mastery determines a suggested difficulty band and focus areas. The session includes prerequisite context; question generation uses Gemini when available and built-in demo questions otherwise.

## Feedback and mastery calculation

Quiz answers are compared with stored correct answers on the server. The backend saves per-question results, updates concept attempt state, recalculates mastery, and returns before/after values for the tracked concept.

The implemented mastery score combines:

- **30% recent performance:** recent accuracy. After each answer this is updated as a simple exponential moving average: 70% previous value and 30% the latest answer (100 or 0).
- **25% historical performance:** total correct answers divided by total attempts.
- **20% difficulty-adjusted performance:** overall accuracy scaled by the observed easy/medium/hard mix (weights 1×/1.5×/2×), with the difficulty factor capped at 1.2×.
- **15% consistency:** a score based on consecutive correct or incorrect answers; correct streaks raise it, incorrect streaks lower it.
- **10% confidence:** the stored confidence value scaled to a 0–100 component. In the demo seed this is initialized from the mastery band; it is not a live confidence question asked after every answer.

The components are added and clamped to 0–100. This is the prototype's heuristic score, not a validated measure of learning or a neural knowledge-tracing model. A fresh demo reset seeds baseline values directly; submitted quiz answers then recalculate mastery through the assessment pipeline.

## Recommendation

The recommendation service runs again against the updated learner state. It prioritizes a weak prerequisite for the primary weak concept when one is found; otherwise it selects foundational, remediation, or weak-topic practice depending on the diagnosis and recent activity. This is what allows the next action to change after practice.

## Supporting stack and retrieval

The API is FastAPI with SQLAlchemy async and SQLite/aiosqlite. The UI is React and TypeScript. Document Q&A ranks stored text chunks by token overlap/relevance and can return page references; it does not use a vector database or embedding search.
