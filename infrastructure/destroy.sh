#!/bin/bash

# TANGO Infrastructure Destroy Script
set -e

echo "🧨 TANGO Infrastructure Destroy"
echo "==============================="

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

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-west-2")
echo "✅ AWS Account: $AWS_ACCOUNT"
echo "✅ AWS Region: $AWS_REGION"

# Check if Terraform is initialized
if [ ! -d ".terraform" ]; then
    echo "❌ Terraform not initialized. Run './setup.sh' first or 'terraform init'."
    exit 1
fi

# Show current infrastructure
echo ""
echo "Current infrastructure:"
terraform show -no-color | head -20

# Plan destruction
echo ""
echo "Planning infrastructure destruction..."
terraform plan -destroy -var="aws_region=$AWS_REGION"

# Warning and confirmation
echo ""
echo "⚠️  WARNING: This will permanently delete:"
echo "   - S3 bucket and all its contents"
echo "   - DynamoDB table and all data"
echo "   - IAM role and policies"
echo ""
read -p "Are you sure you want to destroy the infrastructure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Infrastructure destruction cancelled."
    exit 1
fi

# Destroy infrastructure
echo ""
echo "Destroying infrastructure..."
terraform destroy -var="aws_region=$AWS_REGION" -auto-approve

echo ""
echo "🎉 Infrastructure destroyed successfully!"
echo "   You may want to remove the config.py file manually if no longer needed."
