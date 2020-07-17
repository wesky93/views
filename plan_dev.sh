chalice package --pkg-format terraform ./terraform/
cd terraform && terraform workspace select dev && terraform plan && cd ..