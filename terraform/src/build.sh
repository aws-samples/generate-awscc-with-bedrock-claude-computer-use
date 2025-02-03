#!/bin/bash

# set -e

# Default values for build arguments
DISPLAY_NUM=${DISPLAY_NUM:-1} # we are actually not using these values, just passing defaults
HEIGHT=${HEIGHT:-768} # we are actually not using these values, just passing defaults
WIDTH=${WIDTH:-1024} # we are actually not using these values, just passing defaults
IMAGE_NAME="awscc-tool-use:environment"
AWS_REGION="us-west-2"

# Get AWS account ID dynamically with error checking
if ! AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text); then
    echo "Error: Failed to get AWS account ID. Please check your AWS credentials."
    exit 1
fi

if [[ -z "${AWS_ACCOUNT_ID}" ]]; then
    echo "Error: AWS account ID is empty. Please check your AWS credentials."
    exit 1
fi

ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "Building Docker image: ${IMAGE_NAME}"
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "ECR Repository: ${ECR_REPO}"

# Build the Docker image
if ! docker build \
    --build-arg "DISPLAY_NUM=${DISPLAY_NUM}" \
    --build-arg "HEIGHT=${HEIGHT}" \
    --build-arg "WIDTH=${WIDTH}" \
    -t "${IMAGE_NAME}" \
    -f images/environment/Dockerfile .; then
    echo "Error: Docker build failed"
    exit 1
fi

echo "Build completed successfully"

# Tag and push to ECR
if ! docker tag "${IMAGE_NAME}" "${ECR_REPO}/awscc-tool-use:environment"; then
    echo "Error: Failed to tag Docker image"
    exit 1
fi

# Login to ECR
if ! aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REPO}"; then
    echo "Error: Failed to login to ECR"
    exit 1
fi

# Push to ECR
if ! docker push "${ECR_REPO}/awscc-tool-use:environment"; then
    echo "Error: Failed to push image to ECR"
    exit 1
fi

# Show the built image
docker images | grep "${IMAGE_NAME}"

echo "Successfully built and pushed image to ECR"