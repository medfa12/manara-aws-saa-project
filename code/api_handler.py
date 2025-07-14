import json
import boto3
import os

s3 = boto3.client('s3')
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'manara-my-processed-bucket')

def lambda_handler(event, context):
    print(json.dumps(event)) # Log the entire event for debugging

    # Default headers for CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    try:
        # For HTTP APIs, the method is in event['requestContext']['http']['method']
        method = event['requestContext']['http']['method']

        # Handle preflight OPTIONS request for CORS
        if method == 'OPTIONS':
            return {
                'statusCode': 204,
                'headers': headers,
                'body': ''
            }

        if method == 'POST':
            key = event['queryStringParameters'].get('filename', 'upload.jpg')
            presigned_url = s3.generate_presigned_url('put_object',
                                                      Params={'Bucket': UPLOAD_BUCKET, 'Key': key},
                                                      ExpiresIn=3600)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'upload_url': presigned_url})
            }
        elif method == 'GET':
            key = event['queryStringParameters'].get('key')
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
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        } 