"""
TANGO Multi-Agent Pipeline - Discovery Agent
Direct API-based discovery for finding unprocessed AWS CloudControl resources
"""

import json
import os
import re
import boto3
import requests
from strands import tool
from typing import Dict, List, Set
import config

def get_processed_resources() -> Set[str]:
    """Get list of processed resources from DynamoDB."""
    try:
        dynamodb = boto3.client('dynamodb', region_name=config.AWS_REGION)
        
        response = dynamodb.scan(
            TableName=config.DYNAMODB_TABLE,
            ProjectionExpression='resource_name'
        )
        
        processed = set()
        for item in response.get('Items', []):
            if 'resource_name' in item and 'S' in item['resource_name']:
                processed.add(item['resource_name']['S'])
        
        return processed
    except Exception as e:
        print(f"Warning: Could not access DynamoDB: {e}")
        return set()

def get_github_releases() -> List[Dict]:
    """Get recent releases from terraform-provider-awscc GitHub repository."""
    try:
        url = "https://api.github.com/repos/hashicorp/terraform-provider-awscc/releases"
        response = requests.get(url, timeout=30, params={'per_page': 10})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching GitHub releases: {e}")
        return []

def extract_resources_from_release(release: Dict) -> tuple[List[str], str]:
    """Extract new resources and provider version from a release."""
    body = release.get('body', '')
    tag = release.get('tag_name', '')
    
    # Extract provider version (e.g., "v1.49.0" -> "1.49.0")
    version = tag.lstrip('v') if tag else "unknown"
    
    # Find new resources using regex pattern
    pattern = r'\*\*New Resource:\*\*\s*`(awscc_[^`]+)`'
    resources = re.findall(pattern, body, re.IGNORECASE)
    
    return resources, version

def find_unprocessed_resource() -> Dict[str, str]:
    """Find the next unprocessed AWS CloudControl resource."""
    print("🔍 Checking processed resources...")
    processed_resources = get_processed_resources()
    print(f"Found {len(processed_resources)} processed resources")
    
    print("📡 Fetching GitHub releases...")
    releases = get_github_releases()
    
    if not releases:
        return {"resource_name": "NONE", "provider_version": "NONE"}
    
    # Get latest version from the most recent release
    latest_version = releases[0].get('tag_name', '').lstrip('v') if releases else "unknown"
    print(f"🔄 Using latest provider version: {latest_version}")
    
    # Check releases from newest to oldest for unprocessed resources
    for release in releases:
        resources, _ = extract_resources_from_release(release)  # Ignore original version
        print(f"Release {release.get('tag_name', 'unknown')}: {len(resources)} resources")
        
        # Find first unprocessed resource
        for resource in resources:
            if resource not in processed_resources:
                print(f"✅ Found unprocessed resource: {resource} (using latest version {latest_version})")
                return {"resource_name": resource, "provider_version": latest_version}
    
    print("ℹ️ All resources are processed")
    return {"resource_name": "NONE", "provider_version": "NONE"}

@tool
def discovery_agent(query: str) -> str:
    """
    Find the next unprocessed AWS CloudControl resource using direct API calls.
    
    Args:
        query: Request to find next resource to process
        
    Returns:
        JSON string with resource name and provider version
    """
    try:
        result = find_unprocessed_resource()
        return json.dumps(result)
    except Exception as e:
        error_result = {"resource_name": "ERROR", "provider_version": "ERROR", "error": str(e)}
        return json.dumps(error_result)
