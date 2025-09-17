# DynamoDB Schema - TANGO Multi-Agent Pipeline

## Table Configuration

**Table Name**: `tango-pipeline-state`  
**Region**: `us-west-2`  
**Billing Mode**: `PAY_PER_REQUEST`

## Key Schema
- **Partition Key**: `resource_name` (String)
- **Sort Key**: `timestamp` (Number)

## Item Attributes

### Required Attributes
- `resource_name` (String) - AWS CloudControl resource name (e.g., "awscc_s3_bucket")
- `timestamp` (Number) - Unix timestamp of execution (e.g., 1753897013)
- `status` (String) - Execution status: "success" | "failed"
- `s3_terraform_link` (String) - S3 path to terraform file (e.g., "examples/resources/awscc_s3_bucket/s3_bucket.tf")
- `s3_template_link` (String) - S3 path to template file (e.g., "templates/resources/awscc_s3_bucket.md.tmpl")
- `s3_analysis_link` (String) - S3 path to detailed validation results (e.g., "analysis/resource/awscc_s3_bucket/2025-07-30.txt")

## Creation Command

```bash
aws dynamodb create-table \
  --table-name tango-pipeline-state \
  --attribute-definitions \
    AttributeName=resource_name,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=resource_name,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-west-2
```
