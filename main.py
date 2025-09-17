"""
TANGO Multi-Agent Pipeline - Main Entry Point
Executes the complete multi-agent pipeline for AWS CloudControl resource validation
"""

import sys
import os
from agents.orchestrator_agent import run_pipeline
import config

# Set environment variables from config
os.environ['AWS_PROFILE'] = config.AWS_PROFILE
os.environ['AWS_REGION'] = config.AWS_REGION
os.environ['BYPASS_TOOL_CONSENT'] = 'true'

def main():
    """Main entry point for the TANGO multi-agent pipeline"""
    print("🎯 TANGO Multi-Agent Pipeline")
    print("Automated AWS CloudControl Resource Validation")
    print("=" * 60)
    
    try:
        # Execute the multi-agent pipeline
        result = run_pipeline()
        
        if result:
            print("\n✅ Pipeline execution completed successfully!")
            print("🔄 Run again to process the next resource")
            sys.exit(0)
        else:
            print("\n❌ Pipeline execution failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
