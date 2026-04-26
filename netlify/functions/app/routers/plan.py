from fastapi import APIRouter, HTTPException

from app.schemas import LearningPlanRequest, LearningPlanResponse
from app.services.plan import generate_plan

router = APIRouter(prefix="/api", tags=["learning-plan"])


@router.post("/generate-plan", response_model=LearningPlanResponse)
async def generate_learning_plan(request: LearningPlanRequest):
    """Generate personalized learning plan based on assessment results."""
    try:
        result = generate_plan(request.assessment_results, request.candidate_name)
        return LearningPlanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
