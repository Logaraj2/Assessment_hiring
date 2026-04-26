import json

from app.ai_client import call_ai, extract_json_object
from app.prompts import LEARNING_PLAN_SYSTEM


def generate_plan(assessment_results: dict, candidate_name: str) -> dict:
    """Generate personalized learning plan. Returns dict with learning_plan, recommendations, timeline."""
    assessment_summary = json.dumps(assessment_results, indent=2)

    prompt = f"""Based on the following skill assessment results for {candidate_name},
create a detailed, personalized learning plan.

ASSESSMENT RESULTS:
{assessment_summary}

You MUST respond with ONLY a valid JSON object, no other text before or after. Use this exact structure:
{{
  "learning_path": [
    {{
      "phase": 1,
      "title": "phase title",
      "skills": ["skill1", "skill2"],
      "duration_weeks": 4,
      "resources": [
        {{
          "title": "resource title",
          "type": "course",
          "estimated_hours": 20
        }}
      ],
      "project": "real-world project description"
    }}
  ],
  "total_duration_weeks": 12,
  "success_metrics": ["metric1", "metric2"]
}}"""

    plan_text = call_ai(
        messages=[{"role": "user", "content": prompt}],
        system=LEARNING_PLAN_SYSTEM,
        max_tokens=3000
    )

    learning_plan = extract_json_object(plan_text)
    if not learning_plan:
        learning_plan = {"raw_plan": plan_text}

    recommendations = learning_plan.get("adjacent_skills_rationale", [])
    if isinstance(recommendations, str):
        recommendations = [recommendations]

    return {
        "learning_plan": learning_plan,
        "recommendations": recommendations,
        "timeline": f"{learning_plan.get('total_duration_weeks', 12)} weeks"
    }
