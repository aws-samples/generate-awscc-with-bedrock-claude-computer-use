"""
Configuration module for tango-multi-agent-pipeline.
Uses environment variables with sensible defaults.
"""
import os

# AWS Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
AWS_PROFILE = os.environ.get("AWS_PROFILE", "default")

# S3 Configuration  
S3_BUCKET = os.environ.get("S3_BUCKET", "tango-project-docs")

# DynamoDB Configuration
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "tango-pipeline-state")

# Provider Configuration
DEFAULT_PROVIDER_VERSION = os.environ.get("DEFAULT_PROVIDER_VERSION", "1.53.0")
