# StudyMind AI — Judge Q&A

### What is innovative about StudyMind AI?

The product idea is the connection between a knowledge graph, a concept-level learner model, prerequisite-aware diagnosis, adaptive practice, and a next-best-action recommendation. Assessment changes the learner state, which can change the next action.

### How is this different from ChatGPT?

ChatGPT can explain a topic in response to a prompt. StudyMind AI's prototype maintains structured concept and learner state, uses prerequisite relationships to contextualize a weakness, and recalculates a recommended action after assessed practice. Gemini can support generation when configured, but the adaptive loop is driven by application data and rules.

### Why is a knowledge graph useful?

It represents concepts and their relationships explicitly. The demo's Recursion → Trees prerequisite edge lets the app consider an upstream skill when Trees is weak.

### Why does prerequisite reasoning matter?

A learner may struggle with a topic because a supporting concept is also weak. Considering prerequisite links can direct attention toward that supporting concept instead of treating every low score as isolated.

### How does the learner model update?

The backend grades submitted answers against stored answer keys, records question results, updates per-concept assessment state and mastery, then returns before/after values and a recalculated next action.

### How is mastery calculated?

The current prototype heuristic combines recent performance (30%), historical accuracy (25%), difficulty-adjusted performance (20%), answer-streak consistency (15%), and stored confidence (10%). The result is clamped to 0–100 and mapped to status bands. It is a heuristic, not validated knowledge tracing.

### How does adaptive practice work?

The backend selects a weak topic, retrieves its prerequisites and learner mastery, chooses question difficulty from the target mastery, and creates questions using Gemini when configured or demo questions as a fallback. Submitted answers are scored server-side.

### How do you measure improvement?

The demo reports a change in the application's mastery score before and after a practice assessment. One observed run showed Trees moving from 42.0% to 53.0% (+11.0 points). This is not a measured educational outcome, and results vary with submitted answers.

### Can it generalize beyond Data Structures?

The graph and learner-model concepts are not inherently tied to Data Structures. But the current seeded demo covers Data Structures, and broader subject coverage depends on good extraction, relationships, questions, and validation in each domain. Generalization has not been demonstrated.

### What happens when AI extraction is wrong?

Extraction and generated content can be incomplete or inaccurate. PDF text extraction and Gemini-backed concept/relationship extraction are not guaranteed to be correct. The prototype has demo/fallback behavior, but does not provide production-grade human review or quality assurance for every extracted item.

### What are the current limitations?

It is a hackathon prototype with a deterministic demo learner and heuristic mastery scoring. PDF processing extracts selectable text and does not provide OCR for scanned pages. Ask My Notes uses token-overlap/relevance ranking over chunks, not embeddings or a vector database. The app has not been validated for learning outcomes, time savings, or production-scale use.

### What would you build next?

Next, we would validate extraction and prerequisite quality with educators, add a review/correction workflow, and evaluate the learner model against real learning assessments in a controlled study. Those are future plans, not current capabilities.
