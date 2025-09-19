# TANGO Infrastructure Setup

This directory contains Terraform configuration to automatically provision the required AWS infrastructure for the TANGO Multi-Agent Pipeline.

## Resources Created

- **S3 Bucket**: For storing Terraform files, templates, and analysis results
- **DynamoDB Table**: For tracking pipeline state and processed resources
- **IAM Role**: For pipeline execution with necessary permissions

## Quick Setup

```bash
cd infrastructure
./setup.sh
```

The setup script will:
1. Check prerequisites (Terraform, AWS CLI, credentials)
2. Initialize and plan Terraform configuration
3. Create AWS resources
4. Update `../config.py` with the created resource names

## Manual Setup

If you prefer manual control:

```bash
cd infrastructure

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan

# Apply infrastructure
terraform apply

# Get resource names
terraform output
```

Then manually update `../config.py` with the output values.

## Cleanup

To destroy the infrastructure:

```bash
cd infrastructure
terraform destroy
```

**⚠️ Warning**: This will delete all data in the S3 bucket and DynamoDB table.

## Customization

Edit `variables.tf` to customize:
- AWS region
- Resource name prefixes
- Environment tags
- AWSCC provider version

## Cost Considerations

- **S3**: Pay for storage and requests (minimal for this use case)
- **DynamoDB**: Pay-per-request billing (cost-effective for low usage)
- **IAM**: No additional charges

Estimated monthly cost: < $5 for typical usage patterns.
