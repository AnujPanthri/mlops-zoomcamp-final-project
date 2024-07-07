resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.s3_bucket_name
  acl = "private"
  force_destroy = true
}


output "s3_bucket_name" {
  value = aws_s3_bucket.s3_bucket.bucket
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.s3_bucket.arn
}
