chalice package --pkg-format terraform ./terraform/ --stage prod
export AWS_DEFAULT_REGION=us-east-1
cd terraform && terraform workspace select prod && terraform apply && cd ..