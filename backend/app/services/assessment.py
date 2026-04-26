import json

from app.ai_client import call_ai, extract_json_object, extract_json_array
from app.prompts import SKILL_ASSESSMENT_SYSTEM


def run_skill_assessment(job_description: str, resume: str, conversation_history: list | None) -> dict:
    """Conduct conversational skill assessment. Returns dict with message, assessment_data, is_complete."""
    # Extract skills from job description
    skills_text = call_ai(
        messages=[{
            "role": "user",
            "content": f"Extract required technical and soft skills from this job description. Return as JSON array.\n\nJob Description:\n{job_description}"
        }],
        max_tokens=1000
    )

    required_skills = extract_json_array(skills_text)
    if not required_skills:
        required_skills = ["Python", "Cloud", "API Design", "Testing", "Problem Solving"]

    # Build assessment context
    context = f"""
CANDIDATE RESUME:
{resume}

REQUIRED SKILLS:
{', '.join(str(s) for s in required_skills)}

Please assess the candidate's proficiency in these required skills based on their resume.
Ask targeted questions to verify their real proficiency level.
"""

    # Prepare messages
    messages = conversation_history or []
    if not messages:
        messages.append({
            "role": "user",
            "content": context + "\n\nStart the skill assessment by introducing yourself and explaining the process. Then ask about the first relevant skill."
        })

    # Call AI for assessment
    assistant_message = call_ai(
        messages=messages,
        system=SKILL_ASSESSMENT_SYSTEM,
        max_tokens=2000
    )

    # Check if assessment is complete
    is_complete = "assessment_complete" in assistant_message.lower() and "true" in assistant_message.lower()

    # Extract JSON if assessment is complete
    assessment_data = None
    if is_complete:
        assessment_data = extract_json_object(assistant_message)

    return {
        "message": assistant_message,
        "assessment_data": assessment_data,
        "is_complete": is_complete
    }


def run_quick_assessment(job_description: str, resume: str) -> dict:
    """Quick end-to-end assessment without multi-turn conversation."""
    prompt = f"""
Analyze this candidate's fit for the job based on their resume.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume}

Provide:
1. Required skills from JD
2. Candidate's proficiency in each (beginner/intermediate/advanced)
3. Key gaps
4. Adjacent skills they should learn
5. Personalized learning roadmap with resources and time estimates

Format as JSON.
"""

    assessment_text = call_ai(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000
    )

    result = extract_json_object(assessment_text)
    if result:
        return result
    return {"assessment": assessment_text}
