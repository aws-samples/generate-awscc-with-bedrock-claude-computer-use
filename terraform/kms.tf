resource "awscc_kms_key" "environment" {
  description = "KMS key for ${local.solution_prefix}"
  key_policy = jsonencode(jsondecode(data.aws_iam_policy_document.environment_kms_key.json))
  enable_key_rotation    = true
  pending_window_in_days = 30
  tags                   = local.combined_tags_awscc
}

resource "awscc_kms_alias" "environment" {
  alias_name    = "alias/${local.solution_prefix}-environment"
  target_key_id = awscc_kms_key.environment.key_id
}

