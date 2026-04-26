from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "Skill Assessment & Learning Plan Agent API",
        "version": "1.0.0",
        "endpoints": {
            "assess": "/api/assess",
            "generate_plan": "/api/generate-plan",
            "health": "/health"
        }
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
