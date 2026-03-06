# This tells Terraform to use LocalStack instead of real AWS
# LocalStack runs locally in Docker and simulates AWS services for free
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"       # LocalStack doesn't need real credentials
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true  # Required for LocalStack S3 compatibility

  endpoints {
    s3 = "http://localstack:4566"             # LocalStack S3 endpoint
  }
}