import json, boto3, os

s3 = boto3.client('s3')
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']

def lambda_handler(event, context):
    try:
        # Generate presigned URL (valid for 1 hour)
        key = event['queryStringParameters'].get('filename', 'upload.jpg')
        presigned_url = s3.generate_presigned_url('put_object',
                                                  Params={'Bucket': UPLOAD_BUCKET, 'Key': key},
                                                  ExpiresIn=3600)
        return {
            'statusCode': 200,
            'body': json.dumps({'upload_url': presigned_url})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 