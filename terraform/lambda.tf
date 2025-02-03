module "docker_image_inference_lambda" {
  source  = "terraform-aws-modules/lambda/aws//modules/docker-build"
  version = "7.7.0"

  ecr_repo      = awscc_ecr_repository.environment.id
  use_image_tag = true
  image_tag     = local.lambda.common_inference.docker_image_tag
  source_path   = local.lambda.common_inference.source_path
  platform      = local.lambda.common_inference.platform

  triggers = {
    dir_sha = local.lambda.common_inference.dir_sha
  }
  #checkov:skip=CKV_TF_1:skip module source commit hash
}

############################################################################################################
# CREATE RESOURCE
############################################################################################################

resource "awscc_lambda_function" "create_resource" {
  function_name = local.lambda.create_resource.name
  description   = local.lambda.create_resource.description
  role          = awscc_iam_role.create_resource.arn
  code = {
    image_uri = module.docker_image_inference_lambda.image_uri
  }
  package_type = "Image"
  ephemeral_storage = {
    size = 2024
  }
  architectures = [local.lambda.common_inference.runtime_architecture]
  timeout       = local.lambda.common_inference.timeout
  memory_size   = local.lambda.common_inference.memory_size
  kms_key_arn   = awscc_kms_key.environment.arn
  environment = {
    variables = local.lambda.create_resource.environment.variables
  }
  tracing_config = {
    mode = "Active"
  }
  reserved_concurrent_executions = local.lambda.common_inference.lambda_reserved_concurrency
  tags                           = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_116:not using DLQ, re-drive via state machine
  #checkov:skip=CKV_AWS_272:skip code-signing
}

resource "awscc_logs_log_group" "create_resource" {
  log_group_name    = "/aws/lambda/${local.lambda.create_resource.log_group_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}

############################################################################################################
# DELETE RESOURCE
############################################################################################################

resource "awscc_lambda_function" "delete_resource" {
  function_name = local.lambda.delete_resource.name
  description   = local.lambda.delete_resource.description
  role          = awscc_iam_role.delete_resource.arn
  code = {
    image_uri = module.docker_image_inference_lambda.image_uri
  }
  package_type = "Image"
  ephemeral_storage = {
    size = 2024
  }
  architectures = [local.lambda.common_inference.runtime_architecture]
  timeout       = local.lambda.common_inference.timeout
  memory_size   = local.lambda.common_inference.memory_size
  kms_key_arn   = awscc_kms_key.environment.arn
  environment = {
    variables = local.lambda.delete_resource.environment.variables
  }
  tracing_config = {
    mode = "Active"
  }
  reserved_concurrent_executions = local.lambda.common_inference.lambda_reserved_concurrency
  tags                           = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_116:not using DLQ, re-drive via state machine
  #checkov:skip=CKV_AWS_272:skip code-signing
}

resource "awscc_logs_log_group" "delete_resource" {
  log_group_name    = "/aws/lambda/${local.lambda.delete_resource.log_group_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}

############################################################################################################
# REVIEW RESOURCE
############################################################################################################

resource "awscc_lambda_function" "review_resource" {
  function_name = local.lambda.review_resource.name
  description   = local.lambda.review_resource.description
  role          = awscc_iam_role.review_resource.arn
  code = {
    image_uri = module.docker_image_inference_lambda.image_uri
  }
  package_type = "Image"
  ephemeral_storage = {
    size = 2024
  }
  architectures = [local.lambda.common_inference.runtime_architecture]
  timeout       = local.lambda.common_inference.timeout
  memory_size   = local.lambda.common_inference.memory_size
  kms_key_arn   = awscc_kms_key.environment.arn
  environment = {
    variables = local.lambda.review_resource.environment.variables
  }
  tracing_config = {
    mode = "Active"
  }
  reserved_concurrent_executions = local.lambda.common_inference.lambda_reserved_concurrency
  tags                           = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_116:not using DLQ, re-drive via state machine
  #checkov:skip=CKV_AWS_272:skip code-signing
}

resource "awscc_logs_log_group" "review_resource" {
  log_group_name    = "/aws/lambda/${local.lambda.review_resource.log_group_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}

############################################################################################################
# CLEANER RESOURCE
############################################################################################################

resource "awscc_lambda_function" "cleaner_resource" {
  function_name = local.lambda.cleaner_resource.name
  description   = local.lambda.cleaner_resource.description
  role          = awscc_iam_role.cleaner_resource.arn
  code = {
    image_uri = module.docker_image_inference_lambda.image_uri
  }
  package_type = "Image"
  ephemeral_storage = {
    size = 2024
  }
  architectures = [local.lambda.common_inference.runtime_architecture]
  timeout       = local.lambda.common_inference.timeout
  memory_size   = local.lambda.common_inference.memory_size
  kms_key_arn   = awscc_kms_key.environment.arn
  environment = {
    variables = local.lambda.cleaner_resource.environment.variables
  }
  tracing_config = {
    mode = "Active"
  }
  reserved_concurrent_executions = local.lambda.common_inference.lambda_reserved_concurrency
  tags                           = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_116:not using DLQ, re-drive via state machine
  #checkov:skip=CKV_AWS_272:skip code-signing
}

resource "awscc_logs_log_group" "cleaner_resource" {
  log_group_name    = "/aws/lambda/${local.lambda.cleaner_resource.log_group_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}

############################################################################################################
# SUMMARY RESOURCE
############################################################################################################

resource "awscc_lambda_function" "summary_resource" {
  function_name = local.lambda.summary_resource.name
  description   = local.lambda.summary_resource.description
  role          = awscc_iam_role.summary_resource.arn
  code = {
    image_uri = module.docker_image_inference_lambda.image_uri
  }
  package_type = "Image"
  ephemeral_storage = {
    size = 2024
  }
  architectures = [local.lambda.common_inference.runtime_architecture]
  timeout       = local.lambda.common_inference.timeout
  memory_size   = local.lambda.common_inference.memory_size
  kms_key_arn   = awscc_kms_key.environment.arn
  environment = {
    variables = local.lambda.summary_resource.environment.variables
  }
  tracing_config = {
    mode = "Active"
  }
  reserved_concurrent_executions = local.lambda.common_inference.lambda_reserved_concurrency
  tags                           = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_116:not using DLQ, re-drive via state machine
  #checkov:skip=CKV_AWS_272:skip code-signing
}

resource "awscc_logs_log_group" "summary_resource" {
  log_group_name    = "/aws/lambda/${local.lambda.summary_resource.log_group_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}

############################################################################################################
# ARTIFACT GENERATOR
############################################################################################################

resource "awscc_lambda_function" "artifact_generator" {
  function_name = local.lambda.artifact_generator.name
  description   = local.lambda.artifact_generator.description
  role          = awscc_iam_role.artifact_generator.arn
  code = {
    image_uri = module.docker_image_inference_lambda.image_uri
  }
  package_type = "Image"
  ephemeral_storage = {
    size = 2024
  }
  architectures = [local.lambda.common_inference.runtime_architecture]
  timeout       = local.lambda.common_inference.timeout
  memory_size   = local.lambda.common_inference.memory_size
  kms_key_arn   = awscc_kms_key.environment.arn
  environment = {
    variables = local.lambda.artifact_generator.environment.variables
  }
  tracing_config = {
    mode = "Active"
  }
  reserved_concurrent_executions = local.lambda.common_inference.lambda_reserved_concurrency
  tags                           = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_116:not using DLQ, re-drive via state machine
  #checkov:skip=CKV_AWS_272:skip code-signing
}

resource "awscc_logs_log_group" "artifact_generator" {
  log_group_name    = "/aws/lambda/${local.lambda.artifact_generator.log_group_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}