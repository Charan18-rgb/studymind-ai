# StudyMind AI

> **Adaptive learning that understands the learner.**

StudyMind AI is a multi-user learning application that turns each learner's own study material into a private knowledge graph, records assessment performance, and uses the learner model to choose what to study next.

## What it does

```text
Study material
      ↓
Knowledge graph
      ↓
Learner model
      ↓
Weakness diagnosis
      ↓
Adaptive practice
      ↓
Assessment
      ↓
Mastery update
      ↓
Next best action
```

Most AI study tools can explain a topic. The harder problem is knowing what this learner should learn next. StudyMind keeps learner state across sessions and uses assessed results, concept mastery, and available prerequisite relationships to select a next action.

## Product and optional demo

The normal application uses real accounts, private uploaded documents, real AI processing when configured, learner-specific assessments and mastery, and persistent data. A new account starts without seeded concepts or mastery.

Optional **Demo Mode** provides a deterministic seeded learner for local testing and presentation. It is not required for normal registration and should remain disabled in a public deployment.

## Features

- Email/password registration and login with hashed passwords and an HTTP-only session cookie.
- Private PDF uploads with signature and size validation, page-aware text extraction, and user-scoped documents and chunks.
- Gemini-backed concept and relationship extraction, question generation, and grounded answers when configured.
- Per-user knowledge graphs, assessments, server-side scoring, persisted question results, mastery, and recommendations.
- Adaptive practice driven by the current learner model, plus source-page citations in Ask My Notes.
- Honest empty and AI-unavailable states; the app does not replace missing AI output with fake concepts or mastery.

## Run locally

### Backend (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
# Edit backend/.env locally; never commit it.
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

In another terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open <http://127.0.0.1:5173>. The Vite development server proxies `/api` requests to `http://localhost:8000`. The API docs and health check are at <http://127.0.0.1:8000/docs> and <http://127.0.0.1:8000/health>.

Build the frontend for production with:

```powershell
cd frontend
npm run build
```

## Configuration

The backend loads environment settings from `backend/.env` during local development. Start Uvicorn from the `backend` directory. Keep secrets in local ignored files or the hosting provider's secret manager; never commit them or place them in frontend variables.

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Backend-only key for AI extraction and generation. Without it, uploads/chunks still work, while AI-dependent features report unavailable. |
| `DATABASE_URL` | SQLAlchemy database URL. Defaults to a local SQLite database. |
| `AUTH_SECRET` | Signs session cookies. Use a unique, high-entropy value outside local development. |
| `DEBUG` | Enables development cookie behavior. Set `false` over HTTPS; session cookies then use `Secure`. |
| `CORS_ORIGINS` | JSON list of allowed cross-origin browser origins. The bundled deployment serves UI and API from one origin and uses an empty list. |
| `DEMO_MODE` | Enables optional demo endpoints. Keep `false` for normal users and deployment. |
| `TEST_MODE` | Enables test-only demo identity behavior. Keep `false` outside tests. |
| `SESSION_HOURS` | Session-cookie lifetime. |
| `UPLOAD_MAX_BYTES` | Maximum PDF size in bytes; defaults to 10 MiB. |
| `UPLOAD_DIRECTORY` | Private directory for uploaded PDFs. |
| `BACKEND_HOST`, `BACKEND_PORT`, `FRONTEND_PORT` | Local server defaults. The container uses the hosting provider's `PORT`. |

## Deployment (Render Blueprint)

The repository includes a `Dockerfile` and `render.yaml` for a single-origin deployment: the FastAPI service serves the built React app and API together. The Blueprint requests a Render **Starter** web service and a 1 GB persistent disk mounted at `/var/data`; this paid disk is necessary because SQLite and uploaded PDFs are local files. Render's default service filesystem is ephemeral, so deploying without the configured disk would lose those files on restart or redeploy. See [Render's disk documentation](https://render.com/docs/disks).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Charan18-rgb/studymind-ai)

To deploy, connect this public GitHub repository in Render and create a Blueprint from `render.yaml`. Render generates `AUTH_SECRET` and prompts for `GEMINI_API_KEY`; enter the key in Render's secret/environment settings only. The Blueprint sets `DEBUG=false`, disables demo/test mode, stores SQLite and uploads on the disk, and uses same-origin requests so production CORS does not need a wildcard. The session cookie is Secure when `DEBUG=false`.

After Render provisions the service, use its assigned HTTPS hostname for the website, `/health`, and `/docs`. The URL is assigned by the hosting provider and is intentionally not hardcoded here. Verify registration, upload/AI processing, learning flow, persistence, and two-user isolation against that deployed service before treating it as live. This setup is a small MVP deployment, not enterprise-scale infrastructure; back up its persistent disk and review hosting costs and provider limits.

## Optional deterministic demo

For local testing or a presentation, set `DEMO_MODE=true` in `backend/.env` and use the demo controls in the application. The seeded learner is tooling for this optional path only. Normal account creation does not initialize or receive demo data.

## Validation

From the repository root in PowerShell:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
cd ..\frontend
npx tsc --noEmit
npm run build
```

## Technology and limitations

- Frontend: React, TypeScript, Vite, Tailwind CSS, Radix UI.
- Backend: FastAPI, SQLAlchemy async, SQLite/aiosqlite, and PyMuPDF.
- AI: Google Gemini through the backend-only `google-genai` SDK.
- PDF extraction supports selectable text; scanned-page OCR is not implemented.
- Note retrieval ranks page-aware chunks by token overlap, not embeddings or a vector database.
- AI-generated educational content can be imperfect. The mastery heuristic is not a validated measure of learning outcomes.
- SQLite plus a persistent disk is suitable for this MVP deployment, not a claim of production-scale concurrency or availability.

## NOVA materials

The repository includes the NOVA submission, architecture, pitches, demo, recovery, slide, judge Q&A, and presenter checklist documents. They describe the deterministic presentation scenario where relevant; seeded percentages in those materials are not values assigned to new accounts. Start with [NOVA_SUBMISSION.md](NOVA_SUBMISSION.md), [NOVA_ARCHITECTURE.md](NOVA_ARCHITECTURE.md), and [NOVA_FINAL_DEMO.md](NOVA_FINAL_DEMO.md).

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md). StudyMind AI is licensed under the [MIT License](LICENSE).
