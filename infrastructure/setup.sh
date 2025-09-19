#!/bin/bash

# TANGO Infrastructure Setup Script
set -e

echo "🏗️  TANGO Infrastructure Setup"
echo "=============================="

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install Terraform 1.0.7 or later."
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI."
    exit 1
fi

# Check Terraform version
TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
echo "✅ Terraform version: $TERRAFORM_VERSION"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-west-2")
echo "✅ AWS Account: $AWS_ACCOUNT"
echo "✅ AWS Region: $AWS_REGION"

# Initialize Terraform
echo ""
echo "Initializing Terraform..."
terraform init

# Plan infrastructure
echo ""
echo "Planning infrastructure..."
terraform plan -var="aws_region=$AWS_REGION"

# Ask for confirmation
echo ""
read -p "Do you want to create the infrastructure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Infrastructure setup cancelled."
    exit 1
fi

# Apply infrastructure
echo ""
echo "Creating infrastructure..."
terraform apply -var="aws_region=$AWS_REGION" -auto-approve

# Get outputs
echo ""
echo "📋 Infrastructure created successfully!"
echo "======================================"

S3_BUCKET=$(terraform output -raw s3_bucket_name)
DYNAMODB_TABLE=$(terraform output -raw dynamodb_table_name)
IAM_ROLE=$(terraform output -raw iam_role_arn)

echo "S3 Bucket: $S3_BUCKET"
echo "DynamoDB Table: $DYNAMODB_TABLE"
echo "IAM Role: $IAM_ROLE"
echo "Region: $AWS_REGION"

# Update config.py
echo ""
echo "Setting environment variables..."
export AWS_REGION=$AWS_REGION
export S3_BUCKET=$S3_BUCKET
export DYNAMODB_TABLE=$DYNAMODB_TABLE
export IAM_ROLE_ARN=$IAM_ROLE

echo "✅ Environment variables set"
echo ""
echo "🎉 Setup complete! Run: python main.py"
