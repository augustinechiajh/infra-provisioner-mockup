# These variables come from the FastAPI app via TF_VAR_ environment variables
variable "name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "environment" {
  description = "Environment e.g. dev, staging"
  type        = string
}