import json
from app.services.plan import generate_plan
from app.schemas import LearningPlanRequest, LearningPlanResponse

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        body = json.loads(event['body'])
        request = LearningPlanRequest(**body)
        result = generate_plan(request.assessment_results, request.candidate_name)
        response = LearningPlanResponse(**result)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response.dict())
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }