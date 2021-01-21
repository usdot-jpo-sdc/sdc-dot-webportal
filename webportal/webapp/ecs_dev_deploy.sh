#/bin/bash

echo "***"
echo "Building assets..."
ng build --configuration=ecs-dev


# Copy everything over to S3 bucket
echo "Copying to s3..."
aws s3 cp ./dist s3://gov.dot.sdc.dev-portal --recursive --only-show-errors

# Refresh assets on nginx proxies
echo "Refreshing assets on proxies..."
aws ssm send-command --region us-east-1 \
  --document-name dev-nginx-asset-update \
  --parameters staticAssetsBucket="gov.dot.sdc.dev-portal" \
  --targets "Key=tag:Name,Values=dev-nginx-web-proxy" \
  --comment "Deploying sdc-dot-webportal to dev at $(date) and refreshing assets"