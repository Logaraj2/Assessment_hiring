import json

from app.ai_client import call_ai, extract_json_object
from app.prompts import LEARNING_PLAN_SYSTEM


def generate_plan(assessment_results: dict, candidate_name: str) -> dict:
    """Generate personalized learning plan. Returns dict with learning_plan, recommendations, timeline."""
    assessment_summary = json.dumps(assessment_results, indent=2)

    prompt = f"""
Based on the following skill assessment results for {candidate_name},
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

    plan_text = call_ai(
        messages=[{"role": "user", "content": prompt}],
        system=LEARNING_PLAN_SYSTEM,
        max_tokens=3000
    )

    learning_plan = extract_json_object(plan_text)
    if not learning_plan:
        learning_plan = {"raw_plan": plan_text}

    return {
        "learning_plan": learning_plan,
        "recommendations": learning_plan.get("adjacent_skills_rationale", []),
        "timeline": f"{learning_plan.get('total_duration_weeks', 12)} weeks"
    }
