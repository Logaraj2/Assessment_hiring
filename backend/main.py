"""
AI-Powered Skill Assessment & Personalized Learning Plan Agent
Backend API with Claude AI integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import anthropic
import json
import re

load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Skill Assessment & Learning Plan Agent",
    description="AI-powered conversational skill assessment and personalized learning plan generation",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Models
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

# System prompts
SKILL_ASSESSMENT_SYSTEM = """You are an expert technical interviewer and skill assessment specialist. Your role is to:

1. Extract required skills from the job description
2. Assess the candidate's proficiency in each skill based on their resume
3. Conduct a conversational, multi-turn interview to gauge real proficiency
4. Be encouraging but honest about gaps
5. Identify which skills the candidate can realistically acquire

For each skill, ask targeted questions to assess:
- Theoretical knowledge
- Practical experience
- Project examples
- Problem-solving approach
- Depth of expertise

Maintain a friendly, professional tone. Start by introducing yourself and the assessment process.
After assessing all skills, provide a JSON summary with:
{
  "skills_assessed": [
    {
      "skill": "skill_name",
      "proficiency_level": "beginner|intermediate|advanced|expert",
      "evidence": "specific evidence from resume/conversation",
      "confidence": 0.0-1.0,
      "gap_analysis": "areas where candidate needs improvement"
    }
  ],
  "adjacent_skills": ["skills that would complement their existing skills"],
  "recommended_focus_areas": ["priority areas for learning"],
  "assessment_complete": true
}"""

LEARNING_PLAN_SYSTEM = """You are an expert learning plan designer. Based on skill assessment results, create:

1. A personalized learning roadmap
2. Identify adjacent/complementary skills to build on existing expertise
3. Suggest curated resources (courses, books, projects)
4. Provide realistic time estimates
5. Create a progression path

Output a detailed learning plan as JSON with:
{
  "learning_path": [
    {
      "phase": 1,
      "title": "phase_title",
      "skills": ["skill1", "skill2"],
      "duration_weeks": number,
      "resources": [
        {
          "title": "resource_title",
          "type": "course|book|project|tutorial",
          "link": "url_if_applicable",
          "estimated_hours": number
        }
      ],
      "project": "real-world project to apply skills"
    }
  ],
  "total_duration_weeks": number,
  "success_metrics": ["measurable outcomes"],
  "adjacent_skills_rationale": "why these skills complement existing expertise"
}"""

@app.get("/")
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/assess", response_model=AssessmentResponse)
async def assess_skills(request: AssessmentRequest):
    """
    Conduct skill assessment through conversational interaction with Claude
    """
    try:
        # Extract skills from job description
        skill_extraction_response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract required technical and soft skills from this job description. Return as JSON array.\n\nJob Description:\n{request.job_description}"
                }
            ]
        )

        skills_text = skill_extraction_response.content[0].text
        # Parse JSON from response
        json_match = re.search(r'\[.*\]', skills_text, re.DOTALL)
        if json_match:
            required_skills = json.loads(json_match.group())
        else:
            required_skills = ["Python", "Cloud", "API Design", "Testing", "Problem Solving"]

        # Build assessment context
        context = f"""
CANDIDATE RESUME:
{request.resume}

REQUIRED SKILLS:
{', '.join(required_skills)}

Please assess the candidate's proficiency in these required skills based on their resume.
Ask targeted questions to verify their real proficiency level.
"""

        # Prepare messages
        messages = request.conversation_history or []
        if not messages:
            # First message - introduce assessment
            messages.append({
                "role": "user",
                "content": context + "\n\nStart the skill assessment by introducing yourself and explaining the process. Then ask about the first relevant skill."
            })

        # Call Claude for assessment
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            system=SKILL_ASSESSMENT_SYSTEM,
            messages=messages
        )

        assistant_message = response.content[0].text

        # Check if assessment is complete
        is_complete = "assessment_complete" in assistant_message.lower() and "true" in assistant_message.lower()

        # Extract JSON if assessment is complete
        assessment_data = None
        if is_complete:
            json_match = re.search(r'\{.*\}', assistant_message, re.DOTALL)
            if json_match:
                try:
                    assessment_data = json.loads(json_match.group())
                except:
                    assessment_data = None

        return AssessmentResponse(
            message=assistant_message,
            assessment_data=assessment_data,
            is_complete=is_complete
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-plan", response_model=LearningPlanResponse)
async def generate_learning_plan(request: LearningPlanRequest):
    """
    Generate personalized learning plan based on assessment results
    """
    try:
        # Format assessment results
        assessment_summary = json.dumps(request.assessment_results, indent=2)

        prompt = f"""
Based on the following skill assessment results for {request.candidate_name},
create a detailed, personalized learning plan:

ASSESSMENT RESULTS:
{assessment_summary}

Generate a comprehensive learning plan that:
1. Focuses on skills where they have gaps
2. Identifies adjacent/complementary skills to build on their strengths
3. Provides specific resources and time estimates
4. Creates a realistic progression path
5. Suggests real-world projects for application

Ensure the plan is motivating and achievable within 12 weeks.
"""

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            system=LEARNING_PLAN_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        plan_text = response.content[0].text

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
        learning_plan = {}
        if json_match:
            try:
                learning_plan = json.loads(json_match.group())
            except:
                learning_plan = {"raw_plan": plan_text}
        else:
            learning_plan = {"raw_plan": plan_text}

        return LearningPlanResponse(
            learning_plan=learning_plan,
            recommendations=learning_plan.get("adjacent_skills_rationale", []),
            timeline=f"{learning_plan.get('total_duration_weeks', 12)} weeks"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quick-assessment")
async def quick_assessment(request: AssessmentRequest):
    """
    Quick end-to-end assessment without multi-turn conversation
    """
    try:
        prompt = f"""
Analyze this candidate's fit for the job based on their resume.

JOB DESCRIPTION:
{request.job_description}

CANDIDATE RESUME:
{request.resume}

Provide:
1. Required skills from JD
2. Candidate's proficiency in each (beginner/intermediate/advanced)
3. Key gaps
4. Adjacent skills they should learn
5. Personalized learning roadmap with resources and time estimates

Format as JSON.
"""

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        assessment_text = response.content[0].text

        # Try to extract JSON
        json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                return {"assessment": assessment_text}
        else:
            return {"assessment": assessment_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
