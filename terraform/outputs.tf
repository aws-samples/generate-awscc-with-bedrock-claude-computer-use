output "step_function_arn" {
  value = awscc_stepfunctions_state_machine.orchestrator.arn
  description = "ARN of the Step Function orchestrator"
}

output "s3_bucket_artifact" {
  value = awscc_s3_bucket.artifacts.bucket_name
  description = "S3 bucket for storing artifacts (use this to create pull request)"
}

output "s3_bucket_assets" {
  value = awscc_s3_bucket.assets.bucket_name
  description = "S3 bucket for storing assets (use this to analyze the resource example)"
}