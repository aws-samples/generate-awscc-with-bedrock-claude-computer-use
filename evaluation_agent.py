"""
TANGO Multi-Agent Pipeline - Standalone Evaluation Agent
Evaluates Terraform code quality and documentation alignment for a single resource
by retrieving the code from S3 and comparing with official GitHub examples
"""

import os
import sys
from strands import Agent
from strands_tools import python_repl, use_aws

os.environ['BYPASS_TOOL_CONSENT'] = 'true'

EVALUATION_SYSTEM_PROMPT = """
You are a specialized Terraform code evaluation agent for AWS CloudControl resources.

YOUR TASK:
Evaluate the provided Terraform code for quality and alignment with official Terraform examples from GitHub.

EVALUATION CRITERIA:
1. Syntax correctness and code structure
2. Resource configuration completeness
3. Attribute naming consistency with official examples
4. Proper use of variables, outputs, and dependencies
5. Best practices adherence
6. Documentation alignment

PROVIDE AN EVALUATION REPORT WITH:
1. Overall quality score (0-100%)
2. Key strengths of the code
3. Areas for improvement
4. Specific recommendations to better align with official examples
5. Comparison with official examples where applicable
6. Links to official documentation and examples
"""

def evaluate_resource(resource_name):
    """
    Evaluate Terraform code for a specific AWS CloudControl resource.
    
    Args:
        resource_name: The AWS CloudControl resource name (e.g., awscc_s3_bucket)
    
    Returns:
        Evaluation report
    """

    service_name = resource_name.replace("awscc_", "")
    
    try:
        agent = Agent(
            system_prompt=EVALUATION_SYSTEM_PROMPT,
            tools=[python_repl, use_aws]
        )
        
        evaluation_query = f"""
        Evaluate the Terraform code for the {resource_name} resource.
        
        First, retrieve the Terraform code from S3:
        1. Use the AWS CLI to get the object from S3
        2. The bucket name is "tango-project-docs"
        3. The object key is "examples/resources/{resource_name}/{service_name}.tf"
        4. Make sure to use the us-west-2 region
        
        Next, retrieve the official examples from GitHub:
        1. Use Python's requests library to explore the GitHub repository
        2. Check the directory structure at "https://api.github.com/repos/hashicorp/terraform-provider-awscc/contents/examples/resources/{resource_name}"
        3. For each file found in that directory, fetch its content from "https://raw.githubusercontent.com/hashicorp/terraform-provider-awscc/main/examples/resources/{resource_name}/[filename]"
        4. If no files are found, try searching the repository for examples related to {resource_name}
        
        Then, evaluate the retrieved Terraform code:
        1. Compare it with the official examples
        2. Check if it follows the structure and conventions shown in the examples
        3. Assess its quality, completeness, and adherence to best practices
        4. Provide specific recommendations for improvement
        
        Include in your evaluation:
        1. A comparison of attributes used in the code vs. available in the official examples
        2. Security best practices that should be implemented
        3. Resource configuration completeness
        4. Proper use of variables, outputs, and dependencies
        5. Links to official GitHub examples
        
        Return a detailed evaluation report with a quality score (0-100%).
        
        If you encounter any errors accessing S3 or GitHub, provide clear error messages and suggestions for resolving them.
        """
        
        response = agent(evaluation_query)
        return str(response)
    except Exception as e:
        return f"Error in evaluation agent: {str(e)}\n\nPlease ensure you have run 'mwinit' to authenticate with AWS before running this script."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluation_agent.py <resource_name>")
        print("Example: python evaluation_agent.py awscc_s3_bucket")
        sys.exit(1)
    
    resource_name = sys.argv[1]
    
    print(f"Evaluating {resource_name} (comparing with official GitHub examples)...")
    print("=" * 80)
    print(f"GitHub repository: https://github.com/hashicorp/terraform-provider-awscc/tree/main/examples/resources/{resource_name}")
    print("=" * 80)
    
    evaluation_report = evaluate_resource(resource_name)
    print(evaluation_report)
