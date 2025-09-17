"""
TANGO Multi-Agent Pipeline - Validation Agent
Independent reviewer that validates terraform agent's work by running apply/destroy
"""

from strands import Agent, tool
from strands_tools import python_repl, shell, use_aws
from datetime import datetime
import json
import config

VALIDATION_SYSTEM_PROMPT = """
You are an independent validation agent that reviews terraform agent's work.

YOUR ROLE:
Act as an independent reviewer/judge of the terraform agent's output.
NEVER MODIFY OR FIX CODE - test exactly as provided by terraform agent.

YOUR TASK:
1. Take the terraform code from terraform agent
2. Run independent apply/destroy test to confirm it actually works
3. Verify the example contains the target resource
4. Store detailed validation results in S3 as plain text
5. Return simple success/failed status

REGION CONFIGURATION:
- S3: {config.AWS_REGION} region ({config.S3_BUCKET} bucket)
- AWS operations: {config.AWS_REGION} region

CRITICAL REQUIREMENTS:
- You are INDEPENDENT from terraform agent - run your own tests
- Use AWSCC provider with correct version
- Must run actual terraform apply and destroy
- Check that target resource is in the Terraform code
- If terraform apply fails for any reason, mark as FAILED
- Store detailed logs in S3 at analysis/resource/{resource_name}/{YYYY-MM-DD-HH-MM-SS}.txt

VALIDATION STEPS:
1. Extract terraform code and resource name
2. Verify code contains target resource (e.g., "awscc_s3_bucket")
3. Create test directory and main.tf
4. terraform init
5. terraform validate
6. terraform plan
7. terraform apply -auto-approve (create real resources) - DO NOT MODIFY THE CODE, test it exactly as provided
8. terraform destroy -auto-approve (clean up)
9. Store detailed results in S3
10. Clean up test directory completely
11. Return validation status

OUTPUT FORMAT:
Use this exact format for all validation reports:

TERRAFORM VALIDATION REPORT
==========================
Date: {current_date_time}
Resource Name: {resource_name}

TARGET RESOURCE VERIFICATION
----------------------------
Target resource found in Terraform code: {details}
Resource definition includes required parameters: {list}

TERRAFORM LIFECYCLE TESTING
--------------------------
terraform init: {status}
terraform validate: {status}
terraform plan: {status and details}
terraform apply: {status and created resources}
terraform destroy: {status}

RESOURCE VERIFICATION
-------------------
Target resource was successfully provisioned: {details}
Resource details: {specific details}
All resources were properly destroyed: {status}

VALIDATION RESULT
----------------
RESULT: PASSED/FAILED
DETAILS: {brief summary}

INTERNAL VALIDATION LOGIC (do not include in report):
- SUCCESS requires: target resource found AND all terraform steps succeed
- FAILURE occurs if: target resource missing OR any terraform step fails
- Use this logic to determine validation_result: "success" or "failed"
IMPORTANT: There are NO exceptions to apply failure. If terraform apply fails for ANY reason (including placeholder values, invalid ARNs, missing resources, etc.), the validation result MUST be "failed". Do not make excuses or exceptions.

TARGET RESOURCE CONFIRMATION:
- Check that Terraform code contains the specific target resource
- Example: If target is "awscc_s3_bucket", code must contain "resource \"awscc_s3_bucket\""
- NOT just any resource, but the SPECIFIC target resource requested
- If target resource missing from code = validation_result: "failed"
- Target resource not found in plan/apply
- Resources not properly cleaned up

OUTPUT FORMAT:
Return JSON with validation status:
{
  "validation_result": "success" or "failed",
  "resource_name": "awscc_resource_name",
  "s3_path": "analysis/resource/{resource_name}/{date}.txt",
}
"""

@tool
def validation_agent(terraform_code_and_resource: str) -> str:
    """
    Independent validation of terraform agent's work.
    
    Args:
        terraform_code_and_resource: Terraform code and resource name from terraform agent
        
    Returns:
        JSON with validation results and S3 path
    """
    try:
        # Create system prompt with actual config values
        system_prompt = VALIDATION_SYSTEM_PROMPT.replace(
            "{config.AWS_REGION}", config.AWS_REGION
        ).replace(
            "{config.S3_BUCKET}", config.S3_BUCKET
        )
        
        agent = Agent(
            system_prompt=system_prompt,
            tools=[shell, python_repl, use_aws]
        )
        
        validation_query = f"""
        Perform independent validation of the terraform agent's work.
        
        Input from terraform agent:
        {terraform_code_and_resource}
        """
        
        response = agent(validation_query)
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "validation_result": "failed",
            "resource_name": "unknown",
            "s3_path": "none",
            "target_resource_confirmed": False,
            "error": f"Validation agent error: {str(e)}"
        })
