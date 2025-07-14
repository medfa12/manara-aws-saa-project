import json, boto3, os

s3 = boto3.client('s3')
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'manara-my-processed-bucket')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    try:
        method = event['requestContext']['http']['method']

        if method == 'OPTIONS':
            return {
                'statusCode': 204,
                'headers': headers,
                'body': ''
            }

        if method == 'POST':
            key = event['queryStringParameters'].get('filename', 'upload.jpg')
            contentType = event['queryStringParameters'].get('contentType', 'application/octet-stream')
            presigned_url = s3.generate_presigned_url('put_object',
                                                      Params={'Bucket': UPLOAD_BUCKET, 'Key': key, 'ContentType': contentType},
                                                      ExpiresIn=3600)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'upload_url': presigned_url})
            }

        if method == 'GET':
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

        raise ValueError(f"Unsupported method: {method}")

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        } 