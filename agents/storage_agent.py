"""
TANGO Multi-Agent Pipeline - Storage Agent
Specialized agent for storing pipeline results in DynamoDB and S3 (both success and failure)
"""

import json
import os
import boto3
from datetime import datetime
from strands import Agent, tool
from strands_tools import python_repl, use_aws
import config

def create_template_replacement_tool():
    """Create a programmatic template replacement tool"""
    @tool
    def template_replacer(resource_name: str, service_name: str, description: str, heading: str) -> str:
        """
        Programmatically replace template variables in the generic template.
        
        Args:
            resource_name: Full resource name (e.g., "awscc_b2bi_capability")
            service_name: Service name without prefix (e.g., "b2bi_capability") 
            description: Brief description for the resource
            heading: Descriptive heading for the example
            
        Returns:
            The processed template content
        """
        try:
            s3_client = boto3.client('s3')
            response = s3_client.get_object(
                Bucket=config.S3_BUCKET,
                Key='templates/resources/generic_resource.md.tmpl'
            )
            template_content = response['Body'].read().decode('utf-8')
            
            replacements = {
                "Description about the first example": description,
                "First example": heading,
                "SERVICE_NAME": service_name
            }
            
            processed_content = template_content
            for old_text, new_text in replacements.items():
                processed_content = processed_content.replace(old_text, new_text)
            
            if "{{ tffile" not in processed_content:
                return "Error: Template processing failed - missing {{ tffile }} pattern"
                
            if "resource \"" in processed_content and "{{ tffile" in processed_content:
                lines = processed_content.split('\n')
                terraform_lines = [i for i, line in enumerate(lines) if "resource \"" in line]
                tffile_lines = [i for i, line in enumerate(lines) if "{{ tffile" in line]
                
                if terraform_lines and tffile_lines:
                    return "Error: Template contains both embedded Terraform code and {{ tffile }} - this is incorrect"
            
            return processed_content
            
        except Exception as e:
            return f"Error in template replacement: {str(e)}"
    
    return template_replacer

STORAGE_SYSTEM_PROMPT = """
You are a specialized storage agent for pipeline results and template generation.

YOUR TASKS:
1. Store pipeline execution results in DynamoDB and S3
2. Generate resource-specific templates from generic template using the template_replacer tool
3. Receive validation results and S3 analysis link from validation agent
4. Create simplified DynamoDB entries with S3 links
5. Return clean, structured execution summary

REGION CONFIGURATION:
- DynamoDB: {config.AWS_REGION} region ({config.DYNAMODB_TABLE} table)
- S3: {config.AWS_REGION} region ({config.S3_BUCKET} bucket)

CRITICAL: Always specify region="{config.AWS_REGION}" in ALL use_aws tool calls.

DYNAMODB SCHEMA ({config.DYNAMODB_TABLE} table):
- resource_name (Partition Key): AWS CloudControl resource name
- timestamp (Sort Key): Unix timestamp
- status: "success" or "failed"
- s3_terraform_link: S3 path to terraform file 
  * SUCCESS: examples/resources/{resource_name}/{service_name}.tf
  * FAILED: failed/resources/{resource_name}/{service_name}.tf
- s3_template_link: S3 path to template file (templates/resources/{resource_name}.md.tmpl)
- s3_analysis_link: S3 path to detailed validation results (analysis/resource/{resource_name}/{date}.txt)

WORKFLOW:
1. Extract service name from resource_name (remove "awscc_" prefix)
2. Extract validation results and S3 analysis link from input
3. Clean up old entries: Query DynamoDB for existing entries with same resource_name and delete them
4. Use the template_replacer tool to create the resource-specific template:
   - Reads generic template from S3: s3://{config.S3_BUCKET}/templates/resources/generic_resource.md.tmpl
   - Pass the resource_name, service_name, a brief description, and a descriptive heading
   - The tool will handle reading the generic template and doing exact replacements
   - It will validate the output format automatically
5. Store template directly to S3
6. Store .tf file directly to S3
7. Create simplified DynamoDB entry with:
   - resource_name (partition key)
   - timestamp (sort key)
   - status (success/failed)
   - s3_terraform_link
   - s3_template_link
   - s3_analysis_link (from validation agent)
8. Return structured summary

TEMPLATE REPLACEMENT EXAMPLES:
- For awscc_s3_bucket: description="Create an S3 bucket with versioning and encryption", heading="Create an S3 bucket"

IMPORTANT: Always use the template_replacer tool - do NOT try to do template replacements manually.

OUTPUT FORMAT:
PIPELINE EXECUTION [STATUS]
========================================
Resource: {resource_name}
Status: [SUCCESS/FAILED]

Storage:
- Stored Terraform code in S3 at {s3_terraform_link}
- Stored template in S3 at {s3_template_link}
- Stored validation analysis in S3 at {s3_analysis_link}
- Logged execution details to DynamoDB with S3 links
========================================
"""

@tool
def storage_agent(storage_request: str) -> str:
    """
    Store pipeline results in DynamoDB and S3, generate resource-specific templates.

    Args:
        storage_request: JSON string with execution results

    Returns:
        Storage confirmation with DynamoDB and S3 locations
    """
    try:
        template_replacer = create_template_replacement_tool()
        
        # Create system prompt with actual config values
        system_prompt = STORAGE_SYSTEM_PROMPT.replace(
            "{config.AWS_REGION}", config.AWS_REGION
        ).replace(
            "{config.S3_BUCKET}", config.S3_BUCKET
        ).replace(
            "{config.DYNAMODB_TABLE}", config.DYNAMODB_TABLE
        )
        
        agent = Agent(
            system_prompt=system_prompt,
            tools=[use_aws, python_repl, template_replacer]
        )
        
        response = agent(storage_request)
        return str(response)
    except Exception as e:
        return f"Error in storage agent: {str(e)}"
