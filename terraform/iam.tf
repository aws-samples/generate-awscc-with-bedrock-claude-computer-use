############################################################################################################
# IAM Role for CREATE RESOURCE Lambda
############################################################################################################

resource "awscc_iam_role" "create_resource" {
  role_name                   = local.lambda.create_resource.name
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.lambda_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "create_resource" {
  name   = local.lambda.create_resource.name
  role   = awscc_iam_role.create_resource.role_name
  policy = data.aws_iam_policy_document.inference_lambda.json
}

resource "aws_iam_role_policy_attachment" "create_administrator" {
  role       = awscc_iam_role.create_resource.role_name
  policy_arn = data.aws_iam_policy.administrator.arn
  #checkov:skip=CKV_AWS_274:to cover wide range of use-cases
}

############################################################################################################
# IAM Role for DELETE RESOURCE Lambda
############################################################################################################

resource "awscc_iam_role" "delete_resource" {
  role_name                   = local.lambda.delete_resource.name
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.lambda_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "delete_resource" {
  name   = local.lambda.delete_resource.name
  role   = awscc_iam_role.delete_resource.role_name
  policy = data.aws_iam_policy_document.inference_lambda.json
}

resource "aws_iam_role_policy_attachment" "delete_administrator" {
  role       = awscc_iam_role.delete_resource.role_name
  policy_arn = data.aws_iam_policy.administrator.arn
  #checkov:skip=CKV_AWS_274:to cover wide range of use-cases
}

############################################################################################################
# IAM Role for REVIEW RESOURCE Lambda
############################################################################################################

resource "awscc_iam_role" "review_resource" {
  role_name                   = local.lambda.review_resource.name
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.lambda_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "review_resource" {
  name   = local.lambda.review_resource.name
  role   = awscc_iam_role.review_resource.role_name
  policy = data.aws_iam_policy_document.inference_lambda.json
}

resource "aws_iam_role_policy_attachment" "review_administrator" {
  role       = awscc_iam_role.review_resource.role_name
  policy_arn = data.aws_iam_policy.administrator.arn
  #checkov:skip=CKV_AWS_274:to cover wide range of use-cases
}

############################################################################################################
# IAM Role for CLEANER RESOURCE Lambda
############################################################################################################

resource "awscc_iam_role" "cleaner_resource" {
  role_name                   = "${local.lambda.cleaner_resource.name}-2"
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.lambda_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "cleaner_resource" {
  name   = local.lambda.cleaner_resource.name
  role   = awscc_iam_role.cleaner_resource.role_name
  policy = data.aws_iam_policy_document.inference_lambda.json
}

############################################################################################################
# IAM Role for SUMMARY RESOURCE Lambda
############################################################################################################

resource "awscc_iam_role" "summary_resource" {
  role_name                   = local.lambda.summary_resource.name
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.lambda_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "summary_resource" {
  name   = local.lambda.summary_resource.name
  role   = awscc_iam_role.summary_resource.role_name
  policy = data.aws_iam_policy_document.inference_lambda.json
}

############################################################################################################
# IAM Role for ARTIFACT RESOURCE Lambda
############################################################################################################

resource "awscc_iam_role" "artifact_generator" {
  role_name                   = local.lambda.artifact_generator.name
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.lambda_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "artifact_generator" {
  name   = local.lambda.artifact_generator.name
  role   = awscc_iam_role.artifact_generator.role_name
  policy = data.aws_iam_policy_document.artifact_generator_lambda.json
}

############################################################################################################
# IAM for run task StateMachine 
############################################################################################################

resource "awscc_iam_role" "orchestrator" {
  role_name                   = local.statemachine.orchestrator.name
  assume_role_policy_document = jsonencode(jsondecode(data.aws_iam_policy_document.statemachine_assume_role.json))
  tags                        = local.combined_tags_awscc
}

resource "aws_iam_role_policy" "orchestrator" {
  name   = local.statemachine.orchestrator.name
  role   = awscc_iam_role.orchestrator.role_name
  policy = data.aws_iam_policy_document.orchestrator_statemachine.json
}
