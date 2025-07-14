import json
import boto3
import os

s3 = boto3.client('s3')

UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']
PROCESSED_BUCKET = os.environ['PROCESSED_BUCKET']

def lambda_handler(event, context):
    print(json.dumps(event))

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    try:
        method = event['requestContext']['http']['method']
        
        if method == 'OPTIONS':
            return {'statusCode': 204, 'headers': headers}

      
        if method == 'POST':
            body = json.loads(event.get('body', '{}'))
            key = body.get('filename', 'upload.jpg')
            contentType = body.get('contentType', 'application/octet-stream')
            presigned_url = s3.generate_presigned_url('put_object',
                                                      Params={'Bucket': UPLOAD_BUCKET, 'Key': key, 'ContentType': contentType},
                                                      ExpiresIn=3600)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'upload_url': presigned_url})
            }
        
        elif method == 'GET':
            key = event.get('queryStringParameters', {}).get('key')
            if not key:
                raise ValueError("Missing 'key' parameter")
            presigned_url = s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': PROCESSED_BUCKET, 'Key': key},
                                                      ExpiresIn=3600)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'view_url': presigned_url})
            }
        
        else:
            raise ValueError(f"Unsupported method: {method}")

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        } 