chalice package --pkg-format terraform ./terraform/
export AWS_DEFAULT_REGION=us-east-1
cd terraform && terraform workspace select dev && terraform apply && cd ..