"""
TANGO Multi-Agent Pipeline - Orchestrator Agent
Main entry point that coordinates specialized agents using Strands Agent pattern
"""

import os
import config
from strands import Agent
from .discovery_agent import discovery_agent
from .documentation_agent import documentation_agent
from .terraform_agent import terraform_agent
from .validation_agent import validation_agent
from .terraform_cleanup_agent import terraform_cleanup_agent
from .storage_agent import storage_agent
from .cleanup_agent import cleanup_agent

# Configuration
os.environ['AWS_PROFILE'] = config.AWS_PROFILE
os.environ['AWS_REGION'] = config.AWS_REGION
os.environ['BYPASS_TOOL_CONSENT'] = 'true'

# Define the orchestrator system prompt with clear agent coordination guidance
ORCHESTRATOR_SYSTEM_PROMPT = """
You are the TANGO Pipeline Orchestrator that coordinates specialized agents to process AWS CloudControl resources:

WORKFLOW:
1. For finding unprocessed resources → Use the discovery_agent tool
2. For generating Terraform code → Use the documentation_agent tool 
3. For terraform validation (init/validate/plan/apply/destroy) → Use the terraform_agent tool
4. For independent validation review → Use the validation_agent tool
5. For cleaning up Terraform code (removing provider blocks) → Use the terraform_cleanup_agent tool
6. For storing results in DynamoDB and S3 → Use the storage_agent tool
7. For cleaning up orphaned AWS resources → Use the cleanup_agent tool (when needed)

EXECUTION ORDER:
1. Call discovery_agent to get the next resource to process AND provider version
2. Call documentation_agent with BOTH resource name AND provider version from discovery
3. Call terraform_agent to validate with real AWS deployment
4. Call validation_agent as independent reviewer of terraform agent's work
5. Call terraform_cleanup_agent to clean up the Terraform code (remove provider blocks)
6. Call storage_agent to store results (both success and failure cases)
7. Report completion and instruct user to run again for next resource

CLEANUP: Use cleanup_agent only when explicitly requested or when terraform validation fails and leaves orphaned resources.

CRITICAL REQUIREMENTS:
- Always follow the workflow in order
- Each agent has a specific purpose - use the right tool for each phase
- Pass provider version information from discovery_agent to documentation_agent
- Pass BOTH terraform_code AND provider_version from documentation_agent to terraform_agent
- Ensure terraform_agent actually runs apply/destroy for real AWS validation
- Pass corrected_code AND resource_name to validation_agent for independent review
- Validation_agent stores its own results in S3 and returns validation status
- ALWAYS call terraform_cleanup_agent before storage_agent
- ALWAYS call storage_agent regardless of success or failure
- For failures: pass error details, failed agent name, and partial results to storage_agent
- For success: pass cleaned terraform code, execution results, validation results, and timing to storage_agent

DATA FLOW:
discovery_agent → {resource_name, provider_version}
documentation_agent(resource_name + provider_version) → terraform_code
terraform_agent(terraform_code + provider_version) → corrected_code
validation_agent(corrected_code + resource_name) → validation_results
terraform_cleanup_agent(corrected_code) → cleaned_code
storage_agent(all_results + cleaned_code + validation_results) → storage_confirmation

IMPORTANT UPDATES:
- The terraform_agent returns corrected code
- The validation_agent acts as independent reviewer and stores evaluation results in S3
- The terraform_cleanup_agent removes provider blocks and terraform blocks
- The storage_agent now receives cleaned code from terraform_cleanup_agent and validation results
- This ensures that only working, validated, and cleaned code is stored in the examples

FAILURE HANDLING:
- If any agent fails (including validation_agent), still call storage_agent with failure details
- Include which agent failed, error messages, and any partial results
- If validation_agent fails, include validation failure details in storage
- This maintains complete audit trail for learning and debugging

Execute the complete pipeline workflow using the specialized agents and handle both success and failure cases.
"""

# Create the orchestrator agent with specialized agents as tools
orchestrator = Agent(
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    tools=[discovery_agent, documentation_agent, terraform_agent, validation_agent, terraform_cleanup_agent, storage_agent, cleanup_agent],
    name="TANGO Pipeline Orchestrator"
)

def run_pipeline():
    """Execute the TANGO multi-agent pipeline"""
    print("🚀 TANGO Multi-Agent Pipeline Starting")
    print("=" * 60)
    
    try:
        pipeline_prompt = "Execute the complete pipeline workflow for the next AWS CloudControl resource."
        
        result = orchestrator(pipeline_prompt)
        print("\n🎉 Multi-agent pipeline execution completed!")
        return result
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        return None

if __name__ == "__main__":
    run_pipeline()
