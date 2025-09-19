output "s3_bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.tango_docs.bucket
}

output "dynamodb_table_name" {
  description = "Name of the created DynamoDB table"
  value       = aws_dynamodb_table.tango_pipeline_state.name
}

output "aws_region" {
  description = "AWS region used"
  value       = var.aws_region
}

output "iam_role_arn" {
  description = "ARN of the IAM role for pipeline execution"
  value       = aws_iam_role.tango_pipeline_role.arn
}

output "config_values" {
  description = "Configuration values for config.py"
  value = {
    AWS_REGION      = var.aws_region
    S3_BUCKET       = aws_s3_bucket.tango_docs.bucket
    DYNAMODB_TABLE  = aws_dynamodb_table.tango_pipeline_state.name
    PROVIDER_VERSION = var.awscc_provider_version
  }
}
