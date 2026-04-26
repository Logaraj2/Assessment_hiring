from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, assessment, plan, upload


def create_app() -> FastAPI:
    app = FastAPI(
        title="Skill Assessment & Learning Plan Agent",
        description="AI-powered conversational skill assessment and personalized learning plan generation",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(assessment.router)
    app.include_router(plan.router)
    app.include_router(upload.router)

    return app
