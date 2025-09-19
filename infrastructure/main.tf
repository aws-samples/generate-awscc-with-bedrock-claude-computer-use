terraform {
  required_version = ">= 1.0.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# S3 bucket for storing results
resource "aws_s3_bucket" "tango_docs" {
  bucket = "${var.s3_bucket_prefix}-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "tango_docs" {
  bucket = aws_s3_bucket.tango_docs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tango_docs" {
  bucket = aws_s3_bucket.tango_docs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tango_docs" {
  bucket = aws_s3_bucket.tango_docs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for pipeline state
resource "aws_dynamodb_table" "tango_pipeline_state" {
  name           = "${var.dynamodb_table_prefix}-${random_id.suffix.hex}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "resource_name"
  range_key      = "timestamp"

  attribute {
    name = "resource_name"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Name        = "TANGO Pipeline State"
    Environment = var.environment
    Project     = "TANGO"
  }
}

# IAM role for pipeline execution (optional - for enhanced permissions)
resource "aws_iam_role" "tango_pipeline_role" {
  name = "tango-pipeline-role-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "tango_pipeline_policy" {
  name = "tango-pipeline-policy"
  role = aws_iam_role.tango_pipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudcontrol:*",
          "dynamodb:*",
          "s3:*",
          "iam:*",
          "ec2:*",
          "lambda:*",
          "logs:*"
        ]
        Resource = "*"
      }
    ]
  })
}

data "aws_caller_identity" "current" {}
