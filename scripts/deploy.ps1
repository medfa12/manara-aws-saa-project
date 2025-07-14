param(
  [string]$LayerArn = $layerArn  # paste value or pass in
)

$zip="function.zip"
Compress-Archive -Path source\image_processor\* -DestinationPath $zip -Force

$functionArn = (aws lambda get-function --function-name ImageProcessor `
   --query 'Configuration.FunctionArn' --output text 2>$null)

if (!$functionArn) {
  aws lambda create-function `
    --function-name ImageProcessor `
    --runtime python3.12 `
    --role arn:aws:iam::$((aws sts get-caller-identity --query Account --output text)):role/$roleName `
    --handler handler.lambda_handler `
    --zip-file "fileb://$zip" `
    --layers $LayerArn `
    --environment Variables="{DEST_BUCKET=$processedBucket}"
} else {
  aws lambda update-function-code `
    --function-name ImageProcessor `
    --zip-file "fileb://$zip"
}
