# NOVA Final Presenter Checklist

## Before the demo

- [ ] Backend running from `backend` on `127.0.0.1:8000`.
- [ ] Frontend running from `frontend` (normally `http://localhost:5173`).
- [ ] Open the app in the presentation browser on Dashboard.
- [ ] Click **Reset Demo State** and wait for the dashboard to settle.
- [ ] Confirm the seeded baseline: Trees 42%, Recursion 51%, Arrays 91%, Linked Lists 82%, Graphs 63% (also Stacks 88%, Queues 76%).
- [ ] Confirm the intended Data Structures PDF is present and `StudyMind_QA_Validation.pdf` is absent.
- [ ] Have the intended PDF ready only if using the optional Materials cutaway.
- [ ] Confirm browser zoom and window size on the presentation device.

## Demo sequence

- [ ] Dashboard: overall mastery, weak Trees topic, Next Best Action.
- [ ] Knowledge Map: select Trees; show Recursion → Trees and prerequisite direction.
- [ ] Trees detail: mastery, prerequisite context, explanation, **Practice Trees**.
- [ ] Adaptive Practice: explain why the questions are targeted; answer with a realistic mix.
- [ ] Complete the session and show the returned before/after mastery; confirm the displayed change matches the two values.
- [ ] Return to Dashboard: show updated Trees mastery, activity, and changed recommendation.
- [ ] Click **Reset Demo State** again and confirm the baseline and recommendation return.

## Backup commands (PowerShell)

From the repository root, start the backend:

```powershell
cd backend
.\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, start the frontend:

```powershell
cd frontend
npm run dev
```

If the UI reset is unavailable, restore the demo seed through the local API:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/demo/reset
```

To initialize demo data:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/demo/initialize
```

Reset restores mastery baseline values and the seeded document-upload activity row. It does not delete uploaded documents.

## Presenter guardrails

- Read actual result values from the UI; they depend on answers.
- Avoid refreshing the results screen during the live flow: the result view is held in page state, and refresh starts a fresh adaptive session instead of restoring that screen.
- Describe document retrieval as token-overlap/relevance ranking, not embeddings or vector search.
- Describe the result as a prototype mastery-score change, not a proven learning outcome.
- Browser/manual visual verification should be repeated on the actual presentation device if the browser, display, or screen size changes.
