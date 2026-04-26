from pydantic import BaseModel
from typing import Optional


class AssessmentRequest(BaseModel):
    job_description: str
    resume: str
    conversation_history: Optional[list] = None


class AssessmentResponse(BaseModel):
    message: str
    assessment_data: Optional[dict] = None
    is_complete: bool


class LearningPlanRequest(BaseModel):
    assessment_results: dict
    candidate_name: str


class LearningPlanResponse(BaseModel):
    learning_plan: dict
    recommendations: list
    timeline: str
