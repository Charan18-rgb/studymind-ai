# StudyMind AI

> **Adaptive learning that understands the learner.**

StudyMind AI is a hackathon prototype that connects study material, concept prerequisites, and a learner's concept-level mastery to identify a useful next learning action. Its central question is: **What should this learner learn next?**

## The adaptive loop

```text
Study material → extracted text → extracted (or seeded demo) concepts and relationships
              → persisted learner mastery → weakness diagnosis
              → targeted practice → server-side scoring and saved results
              → recalculated mastery → updated next action
```

The components interact: practice results update the learner model, and the next recommendation is computed from the updated mastery and prerequisite state.

## What it does

- Extracts PDF text by page with PyMuPDF and stores page-aware text chunks.
- When Gemini is configured, attempts to extract concepts and prerequisite/related relationships into a concept graph; the demo uses a deterministic seeded graph.
- Persists mastery and assessment history for each concept in SQLite.
- Diagnoses low-mastery concepts and checks their prerequisites.
- Creates adaptive practice for the selected weakness, with AI generation when configured and demo questions as a fallback.
- Grades submitted answers on the server, stores question results, updates mastery, and returns before/after values and a recalculated recommendation.
- Answers document questions using token-overlap/relevance ranking over extracted chunks, with source page references when available. Retrieval does not use embeddings or a vector database.

## Technology

- Backend: Python, FastAPI, SQLAlchemy async, SQLite/aiosqlite, PyMuPDF
- AI integration: Google Gemini when configured; fallback/demo behavior is available
- Frontend: React, TypeScript, Vite, Tailwind CSS, Radix UI

## Run locally

### Backend (PowerShell)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If the virtual environment is already set up, start the backend from the `backend` directory with only the final command above.

### Frontend

In a second PowerShell terminal, from the repository root:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173`. The API docs are at `http://127.0.0.1:8000/docs`; the backend health check is `http://127.0.0.1:8000/health`.

### Configuration

Copy the example environment file into the backend directory, then add a Gemini key there only if you want Gemini-backed generation:

```powershell
Copy-Item .env.example backend/.env
```

Without a key, the app uses its fallback/demo behavior. The example SQLite URL matches the backend's default local database path. Keep `backend/.env` private; do not commit API keys.

## NOVA demo mode

The app uses a deterministic demo learner and includes a reset endpoint/button to restore the seeded scenario. Reset starts with Trees at 42% and Recursion at 51%, connected by a prerequisite relationship. Run targeted practice, submit answers, and show the backend-returned mastery result and changed recommendation. One recorded NOVA demo example showed Trees changing from 42.0% to 53.0% (+11.0 points); this is an observed run, not a guaranteed result or evidence of general learning gains. Results vary with the submitted answers. Reset before each take so the starting state is consistent.

See [NOVA_SUBMISSION.md](NOVA_SUBMISSION.md), [NOVA_FINAL_DEMO.md](NOVA_FINAL_DEMO.md), [NOVA_30_SECOND_PITCH.md](NOVA_30_SECOND_PITCH.md), [NOVA_2_MINUTE_PITCH.md](NOVA_2_MINUTE_PITCH.md), [NOVA_JUDGE_QA.md](NOVA_JUDGE_QA.md), [NOVA_SLIDES.md](NOVA_SLIDES.md), [NOVA_ARCHITECTURE.md](NOVA_ARCHITECTURE.md), [NOVA_PRESENTER_CHECKLIST.md](NOVA_PRESENTER_CHECKLIST.md), and [NOVA_DEMO_RECOVERY.md](NOVA_DEMO_RECOVERY.md) for the final submission package.

## Verification and limitations

The project has a backend pytest suite and a frontend TypeScript/build workflow. From the repository root in PowerShell, run:

```powershell
cd backend
.\venv\Scripts\python -m pytest -v
cd ..\frontend
npx tsc --noEmit
npm run build
```

The current prototype uses a deterministic demo learner rather than a full account system. PDF processing extracts selectable text; scanned-page OCR is not implemented. Gemini-backed concept/relationship extraction and generated content can be imperfect, and the seeded demo graph is not evidence that arbitrary documents will be modeled correctly. Ask My Notes ranks chunks by token overlap/relevance and can return source pages; it does not use embeddings or a vector database. The mastery heuristic has not been validated against educational outcomes. No learning gains or study-time reductions have been measured.
