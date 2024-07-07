provider "aws" {
    region = "us-east-1"
}

module "model_bucket" {
    source = "./modules/s3/"
    s3_bucket_name = "${var.project_name}-${var.model_bucket_name}"
}

output "model_bucket_name" {
    value = module.model_bucket.s3_bucket_name
}
