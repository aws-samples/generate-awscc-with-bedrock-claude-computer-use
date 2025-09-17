"""
TANGO Multi-Agent Pipeline - Cleanup Agent
Specialized agent for cleaning up orphaned AWS resources from failed executions
"""

from strands import Agent, tool
from strands_tools import use_aws, python_repl

CLEANUP_SYSTEM_PROMPT = """
You are a cleanup agent for orphaned AWS resources from failed pipeline executions.

YOUR TASK:
Find and delete AWS resources that were left behind when pipeline executions failed.

WORKFLOW:
1. Find AWS resources by tags (Environment=example, Name contains "example-")
2. Delete resources in safe order: instances first, then networking

SAFETY: Only delete resources tagged with Environment=example and Name starting with "example-"
"""

@tool
def cleanup_agent(cleanup_request: str) -> str:
    """
    Clean up orphaned AWS resources from failed executions.
    
    Args:
        cleanup_request: What to clean up (e.g., "Clean up execution exec-12345")
    
    Returns:
        Simple cleanup report
    """
    try:
        agent = Agent(
            system_prompt=CLEANUP_SYSTEM_PROMPT,
            tools=[use_aws, python_repl]
        )
        
        response = agent(cleanup_request)
        return str(response)
    except Exception as e:
        return f"Cleanup error: {str(e)}"
