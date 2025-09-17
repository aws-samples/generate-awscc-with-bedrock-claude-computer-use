# TANGO Multi-Agent Pipeline - Usage Guide

A multi-agent system for automated AWS CloudControl resource validation using Terraform.

## Prerequisites

- **Python 3.8+**
- **Terraform 1.0+**
- **AWS CLI 2.0+**
- **AWS Account** with appropriate permissions

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd awscc-tango
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
```

## AWS Setup

### Required AWS Resources

You need to create:
- **DynamoDB table**: As specified in `DYNAMODB_TABLE` config (default: `tango-pipeline-state`)
- **S3 bucket**: As specified in `S3_BUCKET` config (default: `tango-project-docs`)

> **Setup Instructions:** See [`dynamodb-schema.md`](dynamodb-schema.md) for DynamoDB table creation and schema details.

### Required Permissions

Your AWS user/role needs permissions for:
- CloudControl API operations
- DynamoDB read/write access
- S3 read/write access
- IAM role creation/deletion (for resource testing)
- EC2, Lambda, and other AWS services (for resource validation)

## Configuration

The pipeline uses [`config.py`](config.py) with these defaults:

```python
AWS_REGION = "us-west-2"
AWS_PROFILE = "default"
S3_BUCKET = "tango-project-docs"
DYNAMODB_TABLE = "tango-pipeline-state"
DEFAULT_PROVIDER_VERSION = "1.53.0"
```

You can either:
1. **Edit [`config.py`](config.py) directly** for permanent changes
2. **Override via environment variables** for temporary changes:

```bash
export AWS_REGION="eu-west-1"
export S3_BUCKET="my-custom-bucket"
export DEFAULT_PROVIDER_VERSION="1.48.0"
```

## Usage

### 1. Automatic Processing

Process the next unprocessed resource:

```bash
python main.py
```

This will:
- Discover an unprocessed AWSCC resource
- Generate Terraform code
- Validate with real AWS deployment
- Clean up and store results

### 2. Target Specific Resource

Process a specific resource:

```bash
# With default provider version
python target_resource.py awscc_s3_bucket

# With specific provider version
python target_resource.py awscc_s3_bucket 1.48.0
```

### 3. Evaluate Code Quality

Assess existing Terraform code:

```bash
python evaluation_agent.py awscc_s3_bucket
```

