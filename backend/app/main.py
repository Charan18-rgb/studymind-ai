from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import adaptive, analytics, auth, concepts, dashboard, demo, documents, quizzes, recommendations, study_plans
from app.core.config import settings
from app.database.session import init_db

app = FastAPI(
    title="StudyMind AI",
    description="Adaptive AI learning platform with knowledge graph and learner modeling",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(documents.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(concepts.router, prefix=API_PREFIX)
app.include_router(adaptive.router, prefix=API_PREFIX)
app.include_router(recommendations.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(quizzes.router, prefix=API_PREFIX)
app.include_router(demo.router, prefix=API_PREFIX)
app.include_router(study_plans.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)


@app.on_event("startup")
async def startup_event():
    if not settings.debug and settings.auth_secret == "change-this-development-secret-before-deploying":
        raise RuntimeError("AUTH_SECRET must be configured before starting in production mode")
    await init_db()


@app.get("/")
async def root():
    frontend_index = Path(__file__).parent / "static" / "index.html"
    if frontend_index.is_file():
        return FileResponse(frontend_index)
    return {
        "message": "StudyMind AI API",
        "version": "2.0.0",
        "status": "running",
        "api_prefix": API_PREFIX,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


frontend_static = Path(__file__).parent / "static"
if frontend_static.is_dir():
    app.mount("/", StaticFiles(directory=frontend_static, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
