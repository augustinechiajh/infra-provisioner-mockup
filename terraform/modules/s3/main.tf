resource "aws_s3_bucket" "this" {
  bucket = "${var.environment}-${var.name}"  # e.g. "dev-my-bucket"

  tags = {
    Name        = var.name
    Environment = var.environment
    ManagedBy   = "infra-provisioner"        # Shows it was created by our tool
  }
}