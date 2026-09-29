# NOVA Pitch

## 30-second version

Students don't lack information. They lack learning direction. Most AI study tools wait for a student to ask a question; StudyMind AI builds a concept map from study material, tracks what the learner understands, and uses prerequisite gaps to choose a next step. Practice updates the learner model, and the recommendation changes with it. StudyMind AI asks: **What should this learner learn next?**

## 60-second version

Students have more explanations, notes, and quizzes than ever, but they still have to figure out what to study next. A generic AI tool can answer a question; it doesn't automatically keep a structured picture of a learner's concept-level strengths and gaps.

StudyMind AI turns study material into concepts and prerequisite relationships, then tracks mastery for each concept. If a student struggles with Trees and the graph shows that Recursion is a weak prerequisite, the system can direct practice toward that learning gap. Answers are assessed on the server, mastery is updated, and the next recommendation is recalculated.

That is our difference: not just generating content, but connecting what the learner studies to what the learner should do next. We built this as a hackathon prototype, and the results we show are application-level mastery changes, not yet measured educational outcomes.

## 2-minute version

Students don't lack information. They lack learning direction. A student can search for another explanation or take another quiz, but the harder question is: what should this particular learner work on now?

StudyMind AI starts with study material. It extracts PDF text and, when Gemini is configured, attempts to identify concepts and prerequisite links for a knowledge graph; the demo itself uses a deterministic seeded graph. Alongside that graph, it maintains a learner model with concept-level mastery and assessment history.

Those pieces work together. The system finds a weak concept, checks whether its prerequisites are also weak, and selects targeted practice. In our demo, the learner starts at 42% mastery in Trees and 51% in Recursion. The map shows Recursion as a prerequisite for Trees. So instead of a generic quiz, StudyMind AI gives focused practice around the learner's current gap.

When the learner submits answers, the backend scores them, records each question result, and recalculates mastery. One recorded demo example showed Trees moving from 42.0% to 53.0% (+11.0 points). That is an observed result from this prototype and that answer sequence, not a promise of learning gains. The recommendation then updates based on the new learner state.

This is the loop we built: material becomes a knowledge graph, the learner becomes a model, weaknesses become diagnoses, diagnoses become practice, and practice changes what the learner should do next.

StudyMind AI — Adaptive learning that understands the learner.
