param(
  [string]$LayerArn,  
  [string]$ProcessedBucket,
  [string]$TableName = "ImageMetadata",  # Optional DynamoDB table
  [string]$RoleName = "image-processor-lambda-role"
)

$zip="function.zip"
Compress-Archive -Path code\handler.py -DestinationPath $zip -Force  # Updated path to handler.py

$functionArn = (aws lambda get-function --function-name ImageProcessor `
   --query 'Configuration.FunctionArn' --output text 2>$null)

$envVars = "Variables={DEST_BUCKET=$ProcessedBucket"
if ($TableName) { $envVars += ",TABLE_NAME=$TableName" }
$envVars += "}"

if (!$functionArn) {
  aws lambda create-function `
    --function-name ImageProcessor `
    --runtime python3.12 `
    --role arn:aws:iam::$((aws sts get-caller-identity --query Account --output text)):role/$RoleName `
    --handler handler.lambda_handler `
    --zip-file "fileb://$zip" `
    --layers $LayerArn `
    --environment $envVars  # Updated env with optional TABLE_NAME
} else {
  aws lambda update-function-code `
    --function-name ImageProcessor `
    --zip-file "fileb://$zip"
  aws lambda update-function-configuration `
    --function-name ImageProcessor `
    --environment $envVars
}

# Note: This script deploys the ImageProcessor Lambda. For API Gateway setup, use deploy-api.ps1