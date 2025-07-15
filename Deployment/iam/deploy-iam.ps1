param(
  [string]$AccountId = ((aws sts get-caller-identity --query Account --output text))
)

# Deploy ImageProcessor Lambda Role
Write-Output "Creating ImageProcessor Lambda Role..."
aws iam create-role `
  --role-name image-processor-lambda-role `
  --assume-role-policy-document file://Deployment/iam/image-processor-lambda-role.json `
  --description "Allows Lambda functions to access s3 buckets"

# Attach AWS managed policy for basic execution
aws iam attach-role-policy `
  --role-name image-processor-lambda-role `
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Add inline policies for ImageProcessor
aws iam put-role-policy `
  --role-name image-processor-lambda-role `
  --policy-name DynamoDBWritePolicy `
  --policy-document file://Deployment/iam/Image-processor\ lambda\ function/permissions/dynamodb-write-policy.json

aws iam put-role-policy `
  --role-name image-processor-lambda-role `
  --policy-name lambda-s3-access `
  --policy-document file://Deployment/iam/Image-processor\ lambda\ function/permissions/lambda-s3-access.json

# Deploy API Handler Lambda Role
Write-Output "Creating API Handler Lambda Role..."
aws iam create-role `
  --role-name APi-lambda-upload-s3 `
  --assume-role-policy-document file://Deployment/iam/api-lambda-upload-s3-role.json `
  --description "Allows Lambda api function to put s3 objects in the upload bucket"

# Attach AWS managed policy for basic execution
aws iam attach-role-policy `
  --role-name APi-lambda-upload-s3 `
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Add inline policy for API Handler
aws iam put-role-policy `
  --role-name APi-lambda-upload-s3 `
  --policy-name ApihandlerUploadToS3 `
  --policy-document file://Deployment/iam/Api-handler-lambda-function/permissions/api-handler-s3-policy.json

Write-Output "IAM roles and policies deployed successfully!"
Write-Output "ImageProcessor Role ARN: arn:aws:iam::$AccountId:role/image-processor-lambda-role"
Write-Output "API Handler Role ARN: arn:aws:iam::$AccountId:role/APi-lambda-upload-s3" 