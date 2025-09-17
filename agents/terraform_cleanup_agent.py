"""
TANGO Multi-Agent Pipeline - Terraform Cleanup Agent
Specialized agent for cleaning up Terraform code
"""

from strands import Agent, tool
from strands_tools import python_repl

CLEANUP_SYSTEM_PROMPT = """
You are a specialized Terraform code cleanup agent.

Your objective is to clean up Terraform code and make it ready for examples in the AWSCC repository.

CLEANUP RULES:
1. Remove the `terraform` block - not needed for examples
2. Remove the `provider "aws"` and `provider "awscc"` blocks - not needed for examples
3. Remove any `provider "random"` blocks - not needed for examples
4. Remove any `random_id` or `random_*` resources - not needed for examples
5. Replace dynamic names with simple, static names:
   - `"example-bucket-${random_id.bucket_suffix.hex}"` → `"example-bucket"`
   - `"test-function-${random_string.suffix.result}"` → `"example-function"`
   - Any random suffixes or dynamic references → simple static names
6. Remove excessive comments that explain testing or validation purposes
7. Remove comments like "# Bucket name must be globally unique" unless essential
8. Keep only essential comments that explain configuration choices
9. Make the code look clean and production-ready like official Terraform Registry examples
10. Keep all resource configurations and outputs intact
11. Ensure proper formatting and indentation

WHAT TO KEEP:
- All main AWSCC resource configurations
- Essential configuration comments
- Output blocks (but clean up any random references)
- Variable references (if any, but clean up random ones)
- Clean, descriptive resource names

Your task is to clean up the provided Terraform code using the rules above.

Return ONLY the cleaned Terraform code with no additional commentary.
"""

@tool
def terraform_cleanup_agent(terraform_code: str) -> str:
    """
    Clean up Terraform code by removing provider blocks, terraform blocks, 
    excessive comments, and test-specific names.

    Args:
        terraform_code: The Terraform code to clean

    Returns:
        Cleaned Terraform code ready for examples
    """
    try:
        agent = Agent(
            system_prompt=CLEANUP_SYSTEM_PROMPT,
            tools=[python_repl]
        )
        
        cleanup_query = f"""
        Clean up this Terraform code to make it look like a clean, production-ready example:
        
        {terraform_code}
        """
        
        response = agent(cleanup_query)
        return str(response)
    except Exception as e:
        return f"Error in terraform cleanup agent: {str(e)}"
