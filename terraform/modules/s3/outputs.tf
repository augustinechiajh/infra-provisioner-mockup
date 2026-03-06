# Output the bucket name so we can see it in the API response later
output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}
