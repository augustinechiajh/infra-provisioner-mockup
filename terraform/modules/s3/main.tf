# These variables come from the FastAPI app via TF_VAR_ environment variables
variable "name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "environment" {
  description = "Environment e.g. dev, staging"
  type        = string
}

# This tells Terraform to use LocalStack instead of real AWS
# LocalStack runs locally in Docker and simulates AWS services for free
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"       # LocalStack doesn't need real credentials
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3 = "http://localhost:4566"             # LocalStack S3 endpoint
  }
}

# The actual resource being provisioned
resource "aws_s3_bucket" "this" {
  bucket = "${var.environment}-${var.name}"  # e.g. "dev-my-bucket"

  tags = {
    Name        = var.name
    Environment = var.environment
    ManagedBy   = "infra-provisioner"        # Shows it was created by our tool
  }
}

# Output the bucket name so we can see it in the API response later
output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}
