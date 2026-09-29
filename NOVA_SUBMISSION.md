# StudyMind AI — NOVA Submission

## Project name

**StudyMind AI**

## Tagline

**Adaptive learning that understands the learner.**

## Problem

Students have access to huge amounts of educational content but often lack guidance about what they should study next. Finding another explanation is easy; identifying a learner's most useful next step is harder.

## Solution

StudyMind AI processes study PDFs into page-aware text chunks and, when AI is configured, can extract concepts and relationships. It represents concepts and prerequisites as a knowledge graph, stores concept-level learner mastery and assessment history, diagnoses weak topics in their prerequisite context, and generates targeted practice. The backend scores submitted answers, updates mastery, and recalculates the next learning action.

The demo also includes a seeded Data Structures learner, a knowledge map, quizzes, a study planner, and document question answering with source references.

## Innovation

StudyMind AI brings together:

**Knowledge Graph + Learner Model + Prerequisite Diagnosis + Adaptive Practice + Next Best Action**

The contribution is the connected loop: content relationships and learner state inform a practice session; scored performance updates the learner model; the new state can change what the system recommends next.

## Observed demo example

The recorded NOVA demo example starts with **Trees at 42.0%** and shows targeted adaptive practice, followed by **Trees at 53.0% (+11.0 points)** and a changed recommendation. These are observed values from a particular run, not guaranteed results. The current application calculates results from the submitted answers, so another run may produce different values.

## Technology

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Radix UI, Recharts
- **Backend:** Python, FastAPI, SQLAlchemy async, SQLite with aiosqlite
- **PDF processing:** PyMuPDF for page text extraction and chunking
- **AI integration:** Google Gemini (`google-generativeai`) when configured; fallback/demo paths are available

## Limitations

- This is a hackathon prototype with a deterministic demo learner, not a deployed or evaluated tutoring product.
- PDF processing extracts selectable page text. Scanned-image OCR is not implemented in this path; extraction can omit or misread content.
- Gemini-backed concept and relationship extraction and generated questions may be incomplete or incorrect. Availability depends on configuration and external service operation; the demo includes fallback behavior.
- Ask My Notes ranks stored chunks by token overlap/relevance and can return source page references. It does **not** use embeddings or a vector database; answers and retrieval can be incomplete.
- The demo graph and baseline are seeded. Reset restores the demo scenario; it does not remove uploaded documents.
- The mastery score is a prototype heuristic over recent performance, historical accuracy, difficulty, consistency, and stored confidence. It is not validated knowledge tracing.
- A change in the application's mastery score is not evidence of improved educational outcomes or reduced study time. No such outcomes have been measured.
- Some activity values are estimates or derived summaries; they should not be presented as measured study time.

## Core message

> StudyMind AI doesn't just explain the material. It connects a model of the material with a model of the learner, detects prerequisite weaknesses, adapts practice, measures mastery, and chooses a next learning action.
