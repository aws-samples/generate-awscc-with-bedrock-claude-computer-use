# TANGO Multi-Agent Pipeline - Usage Guide

A multi-agent system for automated AWS CloudControl resource validation using Terraform.

## Prerequisites

- **Python 3.10+**
- **Terraform 1.0.7+** (required for AWSCC provider)
- **AWS CLI 2.0+**
- **AWS Account** with appropriate permissions

## Installation

1. **Clone the repository**
```bash
git clone -b tango https://github.com/aws-samples/generate-awscc-with-bedrock-claude-computer-use.git
cd generate-awscc-with-bedrock-claude-computer-use
```

2. **Create and activate virtual environment**

**Option A: Using uv (recommended - faster)**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Option B: Using standard Python**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

**Option A: Using uv**
```bash
uv pip install -r requirements.txt
# Or install directly from pyproject.toml
uv pip install -e .
```

**Option B: Using pip**
```bash
pip install -r requirements.txt
```

4. **Verify Terraform installation**
```bash
terraform version  # Should be 1.0.7 or later
```

5. **Configure AWS credentials**
```bash
aws configure
```

6. **Verify installation**
```bash
python3 -c "from strands import Agent; print('✅ Installation successful')"
```

### Using uv for Development

For faster dependency management and better performance:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project with uv
uv venv
source .venv/bin/activate
uv pip install -e .
```

## AWS Setup

### Automated Infrastructure Setup (Recommended)

The easiest way to set up required AWS resources:

```bash
cd infrastructure
./setup.sh
```

This will automatically create:
- S3 bucket for storing results
- DynamoDB table for pipeline state
- IAM role with necessary permissions
- Update `config.py` with resource names

### Manual Infrastructure Setup

If you prefer manual setup, see [`infrastructure/README.md`](infrastructure/README.md) for detailed instructions.

### Required AWS Resources

You need:
- **DynamoDB table**: As specified in the `DYNAMODB_TABLE` config (default: `tango-pipeline-state`)
- **S3 bucket**: As specified in the `S3_BUCKET` config (default: `tango-project-docs`)

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

