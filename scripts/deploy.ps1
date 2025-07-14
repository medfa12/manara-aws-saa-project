param(
  [string]$LayerArn,  
  [string]$ProcessedBucket,
  [string]$RoleName = "image-processor-lambda-role"
)

$zip="function.zip"
Compress-Archive -Path source\image_processor\* -DestinationPath $zip -Force

$functionArn = (aws lambda get-function --function-name ImageProcessor `
   --query 'Configuration.FunctionArn' --output text 2>$null)

if (!$functionArn) {
  aws lambda create-function `
    --function-name ImageProcessor `
    --runtime python3.12 `
    --role arn:aws:iam::$((aws sts get-caller-identity --query Account --output text)):role/$RoleName `
    --handler handler.lambda_handler `
    --zip-file "fileb://$zip" `
    --layers $LayerArn `
    --environment "Variables={DEST_BUCKET=$ProcessedBucket}"
} else {
  aws lambda update-function-code `
    --function-name ImageProcessor `
    --zip-file "fileb://$zip"
}