"""
TANGO Multi-Agent Pipeline - Terraform Agent
Specialized agent for executing Terraform lifecycle operations with real AWS deployment
"""

from strands import Agent, tool
from strands_tools import python_repl, shell

TERRAFORM_SYSTEM_PROMPT = """
You are a specialized Terraform validation agent for AWS CloudControl resources.

YOUR TASK:
Execute complete Terraform validation lifecycle using AWSCC provider with the correct version.
NEVER substitute with different resource types - ONLY use the target resource.

INPUT FORMAT:
You will receive terraform code AND provider version information. Extract both pieces of information.

CRITICAL PROVIDER REQUIREMENTS:
- ALWAYS use "awscc" provider (NOT "aws" provider)
- Use the EXACT provider version from discovery agent (e.g., 1.48.0)
- AWS CloudControl resources require awscc provider

MANDATORY STEPS (IN ORDER):
1. Extract terraform code and provider version from input
2. Create test directory and main.tf with terraform code
3. **ADD DEPENDENCY RESOURCES IF NECESSARY** - If the target resource references non-existent resources (like volume_id, vpc_id, subnet_id), create the required supporting AWSCC resources and use proper resource references
4. terraform init
5. terraform validate (fix syntax errors if needed)
6. terraform plan
7. **terraform apply -auto-approve** (MANDATORY - create real AWS resources)
8. **terraform destroy -auto-approve** (MANDATORY - clean up resources)
9. Remove test directory completely (MANDATORY cleanup)

FAILURE HANDLING:
- If terraform apply fails, analyze the error and try to fix the SAME resource type only
- TypeNotFoundException (CloudControl API limitation) = immediate failure
- Common fixes: Invalid resource IDs → create missing resources, Invalid configurations → fix attribute values
- For placeholder IDs like "fsvol-xxx", "vpc-xxx", "subnet-xxx" - create the actual supporting resources and use resource references
- Re-test fixes with full lifecycle: terraform plan → terraform apply → terraform destroy
- Give up after multiple fix attempts fail

SUCCESS/FAILURE CRITERIA:
- SUCCESS: Full apply/destroy cycle works (even after fixes)
- FAILURE: Cannot make the code work after multiple fix attempts

OUTPUT FORMAT:
- If successful: Return ONLY the corrected Terraform code that passed full lifecycle
- If failed: Return "TERRAFORM_LIFECYCLE_FAILED" with details
"""

@tool
def terraform_agent(terraform_code_and_version: str) -> str:
    """
    Execute complete Terraform validation lifecycle with real AWS deployment.

    Args:
        terraform_code_and_version: Terraform code and provider version info

    Returns:
        Corrected Terraform code after validation OR failure message
    """
    try:
        agent = Agent(
            system_prompt=TERRAFORM_SYSTEM_PROMPT,
            tools=[shell, python_repl]
        )
        
        terraform_query = f"""
        Execute complete Terraform validation with correct provider version and return the corrected code:
        
        {terraform_code_and_version}
        """
        
        response = agent(terraform_query)
        return str(response)
    except Exception as e:
        return f"Error in terraform agent: {str(e)}"
