# StudyMind AI — Demo Recovery Commands

Run commands from PowerShell. Keep the backend and frontend in separate terminals.

## Start backend

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Start frontend

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/`.

## Health check

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Expected response:

```text
status
------
healthy
```

## Reset demo

Use the Dashboard's **Reset Demo State** button, or call the existing endpoint:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/demo/reset"
```

## Initialize demo

Use the Dashboard's **Reload Demo** button, or call the existing endpoint:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/demo/initialize"
```

## Expected baseline state

After reset and a Dashboard reload, expect overall mastery **70.4%**, Trees **42%**, Recursion **51%**, and a baseline recommendation to review Recursion. The graph contains a prerequisite edge **Recursion → Trees**. The seeded Data Structures document remains in the library. Reset restores demo learning state; it does not delete uploaded documents.
