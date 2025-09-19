variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
  default     = "tango-project-docs"
}

variable "dynamodb_table_prefix" {
  description = "Prefix for DynamoDB table name"
  type        = string
  default     = "tango-pipeline-state"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "awscc_provider_version" {
  description = "AWSCC provider version to use"
  type        = string
  default     = "1.53.0"
}
