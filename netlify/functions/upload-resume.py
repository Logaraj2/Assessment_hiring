import json
import base64
from app.services.file_parser import parse_resume

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        # Assuming the file is sent as base64 in body
        body = json.loads(event['body'])
        file_data = base64.b64decode(body['file'])
        filename = body['filename']
        text = parse_resume(file_data, filename)
        if not text.strip():
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Could not extract text from the file.'})
            }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'text': text})
        }
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to parse file: {str(e)}'})
        }