resource "awscc_stepfunctions_state_machine" "orchestrator" {
  state_machine_name = "${local.solution_prefix}-orchestrator"
  state_machine_type = "STANDARD"
  role_arn           = awscc_iam_role.orchestrator.arn
  definition = templatefile("${path.module}/templates/orchestrator.asl.json", {
    resource_lambda_create   = awscc_lambda_function.create_resource.arn
    resource_lambda_delete   = awscc_lambda_function.delete_resource.arn
    resource_lambda_review   = awscc_lambda_function.review_resource.arn
    resource_lambda_cleaner  = awscc_lambda_function.cleaner_resource.arn
    resource_lambda_summary  = awscc_lambda_function.summary_resource.arn
    resource_lambda_artifact = awscc_lambda_function.artifact_generator.arn
  })

  logging_configuration = {
    destinations = [
      {
        cloudwatch_logs_log_group = {
          log_group_arn = awscc_logs_log_group.orchestrator.arn
        }
      }
    ]
    include_execution_data = true
    level                  = "ALL"
  }

  tracing_configuration = {
    enabled = true
  }

  tags = local.combined_tags_awscc
}

resource "awscc_logs_log_group" "orchestrator" {
  log_group_name    = "/aws/vendedlogs/states/${local.statemachine.orchestrator.name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = awscc_kms_key.environment.arn
  tags              = local.combined_tags_awscc
}