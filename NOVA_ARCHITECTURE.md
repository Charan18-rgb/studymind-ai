# StudyMind AI — Architecture Diagram Specification

## Presentation diagram

Use a single vertical flow. Keep each stage in a restrained outlined panel with one accent color; show the persisted learner state feeding diagnosis and the assessment result returning to the learner model.

```text
                         STUDY MATERIAL
                               ↓
                     ┌───────────────────┐
                     │   Knowledge Graph │
                     │ Concepts +        │
                     │ Prerequisites     │
                     └─────────┬─────────┘
                               ↓
                     ┌───────────────────┐
                     │   Learner Model   │
                     │ Concept Mastery   │
                     └─────────┬─────────┘
                               ↓
                     ┌───────────────────┐
                     │    Diagnosis      │
                     │ Weakness +        │
                     │ Prerequisites     │
                     └─────────┬─────────┘
                               ↓
                     ┌───────────────────┐
                     │ Adaptive Practice │
                     └─────────┬─────────┘
                               ↓
                     ┌───────────────────┐
                     │ Assessment +      │
                     │ Mastery Update    │
                     └─────────┬─────────┘
                               ↓
                     ┌───────────────────┐
                     │   Next Best       │
                     │     Action        │
                     └───────────────────┘
```

Add a feedback arrow from **Assessment + Mastery Update** back to **Learner Model**, then from the updated model into **Diagnosis**. Label the persistence store **SQLite** beside Learner Model and assessment history.

## Implementation notes for speaker/slide designer

- PDF text extraction is page-aware and uses PyMuPDF; chunks are stored for document questions.
- Gemini can extract concepts/relationships and generate content when configured. The deterministic demo graph and fallback questions support the presentation without implying every uploaded PDF is automatically understood correctly.
- Ask My Notes ranks text chunks by token overlap/relevance and returns source page references when available; it does not use embeddings or a vector database.
- FastAPI endpoints connect the React/TypeScript interface to asynchronous SQLAlchemy persistence over SQLite.
- Server-side answer scoring records assessment results, updates the prototype mastery heuristic, and returns the current next action.
