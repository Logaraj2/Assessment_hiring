from fastapi import APIRouter, HTTPException

from app.schemas import AssessmentRequest, AssessmentResponse
from app.services.assessment import run_skill_assessment, run_quick_assessment

router = APIRouter(prefix="/api", tags=["assessment"])


@router.post("/assess", response_model=AssessmentResponse)
async def assess_skills(request: AssessmentRequest):
    """Conduct skill assessment through conversational interaction."""
    try:
        result = run_skill_assessment(
            request.job_description,
            request.resume,
            request.conversation_history
        )
        return AssessmentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-assessment")
async def quick_assessment(request: AssessmentRequest):
    """Quick end-to-end assessment without multi-turn conversation."""
    try:
        return run_quick_assessment(request.job_description, request.resume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
