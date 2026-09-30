# Contributing

Thanks for helping improve StudyMind AI.

## Before opening a change

1. Open an issue for substantial changes so the scope can be discussed.
2. Keep changes focused and preserve user data, account isolation, and the existing adaptive-learning behavior unless a change explicitly targets those areas.
3. Never include API keys, `.env` files, user documents, local databases, or other private data.

Install the development and test dependencies with `pip install -r requirements-dev.txt` from `backend`.

## Local checks

Run the backend suite and frontend checks from PowerShell:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
cd ..\frontend
npx tsc --noEmit
npm run build
```

Describe the behavior changed, tests run, and any limitations in the pull request.
