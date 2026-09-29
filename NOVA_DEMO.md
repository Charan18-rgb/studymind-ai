# NOVA Live Demo Script

**Target: about 3 minutes.** Start with the UI on Dashboard. Use **Reset Demo State** before the take. The baseline is backend-seeded; use the before/after values the app returns because the result changes with the submitted answers.

## 0:00–0:25 — Opening and Dashboard

**Say:** “Most AI study tools can explain a topic. The harder problem is knowing what this learner should learn next.”

Show overall mastery, the weak-topic list, and Next Best Action. Point out Trees at 42% and Recursion at 51%.

**Say:** “StudyMind AI maintains a model of the learner, not just the content.”

## 0:25–0:55 — Knowledge Map

Open Knowledge Map. If Trees is not selected, click the Trees node. Point to the dashed, downward prerequisite arrow from Recursion to Trees; the map legend says arrows run from prerequisite to dependent concept. Show the Trees details and practice button.

**Say:** “It understands that Recursion is a prerequisite for Trees, and the learner is weak in both.”

## 0:55–1:30 — Adaptive Practice

Choose **Practice Trees**. Point out the session context, the current Trees mastery, prerequisites considered, focus area, and targeted question. Answer the five questions with a realistic mix—some correct and some incorrect—using each question's content rather than blindly selecting the same position.

**Say:** “So instead of a generic quiz, it creates targeted practice around that weakness.”

## 1:30–2:00 — Results

Complete the session. Pause on the backend-returned session score and before/after mastery. Check that `after − before = improvement`; do not narrate a planned value. A verified run with three correct and two incorrect answers returned Trees 42.0% → 53.0% (+11.0 points); a different answer sequence can produce a different result.

**Say:** “After the assessment, the learner model changes.”

## 2:00–2:30 — Recommendation changes

Return to Dashboard. Show Trees' updated mastery and the recalculated Next Best Action. In the verified run above, the action changed from “Review Recursion” to “Practice Recursion.”

**Say:** “And because the learner state changed, the next recommendation changes too.”

## 2:30–3:00 — Close

**Say:** “Most AI tutors answer what you ask. StudyMind AI figures out what you should learn next. StudyMind AI — Adaptive learning that understands the learner.”

### Optional Materials cutaway

For a strict three-minute take, skip Materials. If the upload and PDF are already prepared, replace up to 15 seconds of the results or recommendation hold with one grounded question and its source page. The primary story remains the adaptive loop.

### Presenter notes

- If the start state looks different, click **Reset Demo State** and wait for the dashboard values to reload.
- Use the values and recommendation visible in the current run. The +11.0 point result above is a verified example, not a guaranteed outcome.
- The demo may use Gemini-generated questions when configured; the exact question text and answer choices can vary.
- Avoid refreshing the results screen mid-demo; it is page state and a refresh starts a fresh adaptive session.
