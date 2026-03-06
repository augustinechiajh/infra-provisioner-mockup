resource "aws_instance" "this" {
  ami           = "ami-00000000"
  instance_type = "t2.micro"

  tags = {
    Name        = "${var.environment}-${var.name}"
    Environment = var.environment
    ManagedBy   = "infra-provisioner"
  }
}