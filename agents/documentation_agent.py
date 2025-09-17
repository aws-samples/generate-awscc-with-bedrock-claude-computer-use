"""
TANGO Multi-Agent Pipeline - Documentation Agent
Specialized agent for generating Terraform code for AWS CloudControl resources
"""

from strands import Agent, tool
from strands_tools import python_repl, use_llm, http_request
import config

DOCUMENTATION_SYSTEM_PROMPT = """
You are a specialized Terraform documentation generator for AWS CloudControl resources.

YOUR TASK:
Generate clean Terraform configuration code matching Terraform Registry example patterns.

REQUIREMENTS:
1. Extract resource name and provider version from input data
2. Use EXACT provider version provided (e.g., "1.48.0" becomes "~> 1.48.0")
3. Focus on the AWSCC resource - minimize supporting AWS provider resources
4. Use "example" naming throughout (example-stream, example-consumer)
5. Configure for {config.AWS_REGION} region when region-specific settings needed
6. Add Environment and Name tags when supported

OUTPUT STYLE:
- Keep minimal - essential arguments only for the AWSCC resource
- Maximum 1-2 outputs if absolutely necessary
- Clean, focused configuration like official registry examples
- Avoid complex supporting infrastructure - use simple references or existing resources when possible
- If supporting resources are absolutely required, keep them minimal

OUTPUT: Valid Terraform .tf file content starting with resources.
"""

@tool
def documentation_agent(resource_data: str) -> str:
    """
    Generate Terraform configuration code for an AWS CloudControl resource.

    Args:
        resource_data: JSON string or text containing resource name and provider version info

    Returns:
        Complete Terraform configuration code
    """
    try:
        # Create system prompt with actual config values
        system_prompt = DOCUMENTATION_SYSTEM_PROMPT.replace(
            "{config.AWS_REGION}", config.AWS_REGION
        )
        
        agent = Agent(
            system_prompt=system_prompt,
            tools=[http_request, use_llm, python_repl]
        )
        
        documentation_query = f"""
        Generate complete Terraform configuration using this resource information:
        
        {resource_data}
        """
        
        response = agent(documentation_query)
        return str(response)
    except Exception as e:
        return f"Error in documentation agent: {str(e)}"
