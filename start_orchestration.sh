#!/bin/bash

#!/bin/bash

# =============================================================================
# AWS Step Functions Orchestration Script
# =============================================================================
# Description:
#   This script orchestrates AWS Step Functions execution and manages related
#   S3 bucket operations. It starts a Step Function execution using input from
#   resources.json, monitors the execution status, and downloads resulting
#   artifacts from S3.
#
# Usage:
#   ./start_orchestration.sh <state_machine_arn> <s3_bucket>
#
# Arguments:
#   state_machine_arn - ARN of the AWS Step Function state machine
#   s3_bucket        - Name of the S3 bucket for artifacts
#
# Requirements:
#   - AWS CLI configured with appropriate credentials
#   - jq command-line JSON processor
#   - resources.json file in the same directory
#
# Output:
#   - Execution status and details
#   - Downloaded artifacts in ./outputs directory
# =============================================================================


# Set AWS region
export AWS_DEFAULT_REGION="us-west-2"

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <state_machine_arn> <s3_bucket>"
    echo "Example: $0 arn:aws:states:region:account:stateMachine:name my-artifact-bucket-name"
    exit 1
fi

# Assign command line arguments to variables
STATE_MACHINE_ARN="$1"
S3_BUCKET="$2"

# Validate inputs are not empty
if [ -z "$STATE_MACHINE_ARN" ] || [ -z "$S3_BUCKET" ]; then
    echo "Error: Both STATE_MACHINE_ARN and S3_BUCKET must be provided"
    exit 1
fi

# Validate S3 bucket exists
if ! aws s3 ls "s3://${S3_BUCKET}" >/dev/null 2>&1; then
    echo "Error: S3 bucket '${S3_BUCKET}' does not exist or you don't have access to it"
    exit 1
fi

STATE_MACHINE_NAME=$(echo $STATE_MACHINE_ARN | awk -F':' '{print $NF}')

# Read and display target resources from resources.json
echo -e "${BLUE}Reading target resources from resources.json...${NC}"
if [ -f "resources.json" ]; then
    RESOURCES=$(jq -r '.target_resources[]' resources.json)
    echo -e "${GREEN}Target resources to be created:${NC}"
    echo "$RESOURCES" | while read resource; do
        echo -e "${YELLOW}- $resource${NC}"
    done
    echo -e "${BLUE}----------------------------------------${NC}"
else
    echo -e "${RED}Error: resources.json file not found!${NC}"
    exit 1
fi

echo -e "${BLUE}Starting Step Function execution with input from resources.json...${NC}"

# Start the execution and capture the response
EXECUTION_RESPONSE=$(aws stepfunctions start-execution \
    --state-machine-arn "$STATE_MACHINE_ARN" \
    --input file://resources.json)

# Extract the execution ARN from the response
EXECUTION_ARN=$(echo $EXECUTION_RESPONSE | jq -r '.executionArn')

# Extract the execution ID (last part after ':')
EXECUTION_ID=$(echo $EXECUTION_ARN | awk -F ':' '{print $NF}')

echo -e "${GREEN}Execution started with ARN: ${YELLOW}$EXECUTION_ARN${NC}"
echo -e "${GREEN}Execution ID: ${YELLOW}$EXECUTION_ID${NC}"

# Function to check execution status
check_status() {
    aws stepfunctions describe-execution --execution-arn "$EXECUTION_ARN" | jq -r '.status'
}

echo -e "${BLUE}Monitoring execution status...${NC}"

# Monitor the execution status
STATUS="RUNNING"
while [ "$STATUS" == "RUNNING" ]
do
    STATUS=$(check_status)
    echo -e "${GREEN}Current status: ${YELLOW}$STATUS${NC}"

    # # Get the execution logs using the execution ID as the log stream
    # echo -e "${BLUE}Recent logs:${NC}"
    # aws logs get-log-events \
    #     --log-group-name "/aws/states/$STATE_MACHINE_NAME" \
    #     --log-stream-name "$EXECUTION_ID" \
    #     --limit 5 2>/dev/null | jq -r '.events[].message' 2>/dev/null

    # Wait for 5 seconds before checking again
    sleep 5
done

echo -e "${GREEN}Execution completed with status: ${YELLOW}$STATUS${NC}"

# Get final execution results
echo -e "${BLUE}Getting execution results...${NC}"
aws stepfunctions describe-execution \
    --execution-arn "$EXECUTION_ARN" \
    | jq '.'

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}Listing contents of S3 bucket: ${YELLOW}$S3_BUCKET${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${BLUE}Downloading S3 bucket contents to outputs directory...${NC}"

# Create outputs directory if it doesn't exist
mkdir -p outputs

# Remove any existing contents in the outputs directory
rm -rf outputs/*

# Sync the S3 bucket contents to the outputs directory
aws s3 sync "s3://$S3_BUCKET" "outputs/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully downloaded S3 bucket contents to outputs directory${NC}"
    echo -e "${BLUE}Local directory structure:${NC}"
    tree outputs 2>/dev/null || find outputs -print | sed -e "s;outputs/;;" -e "s;^;outputs/;" -e "s;[^/]*\/;|----;g"
else
    echo -e "${RED}Error downloading S3 bucket contents${NC}"
fi

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}Script completed${NC}"
