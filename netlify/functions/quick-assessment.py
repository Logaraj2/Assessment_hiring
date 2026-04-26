import json
from app.services.assessment import run_quick_assessment
from app.schemas import AssessmentRequest

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        body = json.loads(event['body'])
        request = AssessmentRequest(**body)
        result = run_quick_assessment(request.job_description, request.resume)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }