param(
  [string]$UploadBucket = "manara-my-upload-bucket",
  [string]$ProcessedBucket = "manara-my-processed-bucket",
  [string]$RoleName = "api-lambda-upload-s3",  # Adjust role if different
  [string]$Region = "us-east-1",
  [string]$AccountId = ((aws sts get-caller-identity --query Account --output text)),
  [string]$ApiName = "ImageUploadAPI",
  [string]$StageName = "prod"
)

# Step 1: Package and deploy Lambda
$zip="api_function.zip"
Compress-Archive -Path code\api_handler.py -DestinationPath $zip -Force

$functionArn = (aws lambda get-function --function-name UploadAPIHandler --query 'Configuration.FunctionArn' --output text 2>$null)

$envVars = "Variables={UPLOAD_BUCKET=$UploadBucket,PROCESSED_BUCKET=$ProcessedBucket}"

if (!$functionArn) {
  aws lambda create-function `
    --function-name UploadAPIHandler `
    --runtime python3.12 `
    --role arn:aws:iam::$AccountId:role/$RoleName `
    --handler api_handler.lambda_handler `
    --zip-file "fileb://$zip" `
    --environment $envVars
} else {
  aws lambda update-function-code `
    --function-name UploadAPIHandler `
    --zip-file "fileb://$zip"
  aws lambda update-function-configuration `
    --function-name UploadAPIHandler `
    --environment $envVars
}

# Step 2: Add Lambda permission for API Gateway
aws lambda add-permission `
  --function-name UploadAPIHandler `
  --statement-id apigateway-invoke `
  --action "lambda:InvokeFunction" `
  --principal apigateway.amazonaws.com `
  --source-arn "arn:aws:execute-api:$Region:$AccountId:*/*/*"  # Broad for simplicity; narrow if needed

# Step 3: Create or get API
$apiId = (aws apigatewayv2 get-apis --query "Items[?Name=='$ApiName'].ApiId" --output text)
if (!$apiId) {
  $apiId = (aws apigatewayv2 create-api --name $ApiName --protocol-type HTTP --query ApiId --output text)
}
Write-Output "API ID: $apiId"

# Step 4: Create integrations (AWS_PROXY to Lambda)
$lambdaArn = "arn:aws:lambda:$Region:$AccountId:function:UploadAPIHandler"
$postIntegrationId = (aws apigatewayv2 create-integration --api-id $apiId --integration-type AWS_PROXY --integration-uri $lambdaArn --integration-method POST --payload-format-version 2.0 --query IntegrationId --output text)
$getIntegrationId = (aws apigatewayv2 create-integration --api-id $apiId --integration-type AWS_PROXY --integration-uri $lambdaArn --integration-method GET --payload-format-version 2.0 --query IntegrationId --output text)

# Step 5: Create routes
aws apigatewayv2 create-route --api-id $apiId --route-key "POST /upload" --target integrations/$postIntegrationId
aws apigatewayv2 create-route --api-id $apiId --route-key "GET /view" --target integrations/$getIntegrationId

# Step 6: Deploy the API
aws apigatewayv2 create-deployment --api-id $apiId --stage-name $StageName

Write-Output "API Endpoint: https://$apiId.execute-api.$Region.amazonaws.com/$StageName"
Write-Output "Deployment complete. Test with: curl https://$apiId.execute-api.$Region.amazonaws.com/$StageName/upload" 