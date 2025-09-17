"""
TANGO Multi-Agent Pipeline - Target Resource Processing
Processes a specific AWSCC resource through the full orchestration pipeline
"""

import sys
import os
from agents.orchestrator_agent import orchestrator
import config

# Set environment variables from config
os.environ['AWS_PROFILE'] = config.AWS_PROFILE
os.environ['AWS_REGION'] = config.AWS_REGION
os.environ['BYPASS_TOOL_CONSENT'] = 'true'

def process_resource(resource_name, provider_version=None):
    """Process a specific resource through the full orchestration pipeline"""
    if provider_version is None:
        provider_version = config.DEFAULT_PROVIDER_VERSION
        
    print("🎯 TANGO Multi-Agent Pipeline - Target Resource Processing")
    print(f"Processing resource: {resource_name}")
    print(f"Using provider version: {provider_version}")
    print("=" * 60)
    
    processing_prompt = f"""
    Execute the complete pipeline workflow for the AWS CloudControl resource: {resource_name}
    
    IMPORTANT: Skip the discovery step and use this resource information directly:
    {{
      "resource_name": "{resource_name}",
      "provider_version": "{provider_version}"
    }}
    
    Continue with the normal workflow from there:
    1. Generate Terraform code using the documentation_agent
    2. Validate with the terraform_agent
    3. Clean up the Terraform code with the terraform_cleanup_agent
    4. Store results with the storage_agent
    """
    
    try:
        # Execute the orchestrator with our processing prompt
        result = orchestrator(processing_prompt)
        print("\n✅ Resource processing completed!")
        return True
    except Exception as e:
        print(f"\n❌ Resource processing error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python target_resource.py <resource_name> [provider_version]")
        sys.exit(1)
    
    resource_name = sys.argv[1]
    provider_version = sys.argv[2] if len(sys.argv) > 2 else "1.53.0"
    
    success = process_resource(resource_name, provider_version)
    sys.exit(0 if success else 1)
