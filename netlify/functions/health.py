import json

def handler(event, context):
    if event['httpMethod'] != 'GET':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    path = event.get('path', '/')
    if path.endswith('/health'):
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy'})
        }
    else:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "message": "Skill Assessment & Learning Plan Agent API",
                "version": "1.0.0",
                "endpoints": {
                    "assess": "/api/assess",
                    "generate_plan": "/api/generate-plan",
                    "health": "/health"
                }
            })
        }