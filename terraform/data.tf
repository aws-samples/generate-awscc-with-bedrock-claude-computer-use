data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

data "aws_ecr_authorization_token" "token" {}

# IMPORTANT: this policy is required to allow Lambda to test variety of resources, change this if you want to limit the scope
data "aws_iam_policy" "administrator" {
  arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  #checkov:skip=CKV_AWS_275:to cover wide range of use-cases
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole", ]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "statemachine_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "inference_lambda" {
  statement {
    sid = "CloudWatchLog"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect = "Allow"
    resources = [
      "arn:${data.aws_partition.current.partition}:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.solution_prefix}*"
    ]
  }

  statement {
    sid = "S3Access"
    actions = [
      "s3:ListBucket",
      "s3:*Object",
    ]
    effect = "Allow"
    resources = [
      awscc_s3_bucket.assets.arn,
      awscc_s3_bucket.artifacts.arn,
      "${awscc_s3_bucket.assets.arn}/*",
      "${awscc_s3_bucket.artifacts.arn}/*"
    ]
  }

  statement {
    sid = "XRayAccess"
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
    ]
    effect = "Allow"
    resources = [
      "*"
    ]
  }

  statement {
    sid = "KMSAccess"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey"
    ]
    effect    = "Allow"
    resources = [awscc_kms_key.environment.arn]
  }

  statement {
    sid = "Bedrock"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    effect = "Allow"
    resources = [
      "arn:${data.aws_partition.current.partition}:bedrock:${data.aws_region.current.name}::foundation-model/*"
    ]
  }
  #checkov:skip=CKV_AWS_356:Xray permission require wildcard
  #checkov:skip=CKV_AWS_111:Xray permission require wildcard
  #checkov:skip=CKV_AWS_109:KMS management permission by IAM user
  #checkov:skip=CKV_AWS_111:wildcard permission required for kms key
  #checkov:skip=CKV_AWS_356:wildcard permission required for kms key
}

data "aws_iam_policy_document" "artifact_generator_lambda" {
  statement {
    sid = "CloudWatchLog"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect = "Allow"
    resources = [
      "arn:${data.aws_partition.current.partition}:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.solution_prefix}*"
    ]
  }

  statement {
    sid = "S3Access"
    actions = [
      "s3:ListBucket",
      "s3:*Object",
    ]
    effect = "Allow"
    resources = [
      awscc_s3_bucket.assets.arn,
      awscc_s3_bucket.artifacts.arn,
      "${awscc_s3_bucket.assets.arn}/*",
      "${awscc_s3_bucket.artifacts.arn}/*"
    ]
  }

  statement {
    sid = "XRayAccess"
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
    ]
    effect = "Allow"
    resources = [
      "*"
    ]
  }

  statement {
    sid = "KMSAccess"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey"
    ]
    effect    = "Allow"
    resources = [awscc_kms_key.environment.arn]
  }
  #checkov:skip=CKV_AWS_356:Xray permission require wildcard
  #checkov:skip=CKV_AWS_111:Xray permission require wildcard
  #checkov:skip=CKV_AWS_109:KMS management permission by IAM user
  #checkov:skip=CKV_AWS_111:wildcard permission required for kms key
  #checkov:skip=CKV_AWS_356:wildcard permission required for kms key
}

data "aws_iam_policy_document" "orchestrator_statemachine" {
  statement {
    sid = "InvokeLambda"
    actions = [
      "lambda:InvokeFunction"
    ]
    effect    = "Allow"
    resources = ["arn:${data.aws_partition.current.partition}:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${local.solution_prefix}*"]
  }

  statement {
    sid = "CloudWatchLog"
    actions = [
      "logs:CreateLogDelivery",
      "logs:GetLogDelivery",
      "logs:UpdateLogDelivery",
      "logs:DeleteLogDelivery",
      "logs:ListLogDeliveries",
      "logs:PutResourcePolicy",
      "logs:DescribeResourcePolicies",
      "logs:DescribeLogGroups",
      "logs:PutRetentionPolicy"
    ]
    effect    = "Allow"
    resources = ["*"]
  }

  statement {
    sid = "PutLog"
    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream"
    ]
    effect    = "Allow"
    resources = ["arn:${data.aws_partition.current.partition}:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/vendedlogs/states/${local.solution_prefix}*"]
  }

  statement {
    sid = "XRayAccess"
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
    ]
    effect = "Allow"
    resources = [
      "*"
    ]
  }
  #checkov:skip=CKV_AWS_356:Xray permission require wildcard
  #checkov:skip=CKV_AWS_111:Xray permission require wildcard
}

data "aws_iam_policy_document" "environment_kms_key" {
  statement {
    sid = "AllowECR"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*",
    ]

    resources = ["*"]

    principals {
      type        = "Service"
      identifiers = ["ecr.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["ecr.${data.aws_region.current.name}.amazonaws.com"]
    }
  }

  statement {
    sid = "AllowS3"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
    ]

    resources = ["*"]

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
  }

  statement {
    sid = "AllowLambda"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey"
    ]

    resources = ["*"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }

  statement {
    sid = "AllowCloudWatchLogGroup"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
    }
    condition {
      test     = "ArnLike"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:${data.aws_partition.current.partition}:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
    }
  }

  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    actions = [
      "kms:*"
    ]
    resources = ["*"]
    principals {
      type = "AWS"
      identifiers = [
        "arn:${data.aws_partition.current.id}:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
    }
  }
  #checkov:skip=CKV_AWS_109:KMS management permission by IAM user
  #checkov:skip=CKV_AWS_111:wildcard permission required for kms key
  #checkov:skip=CKV_AWS_356:wildcard permission required for kms key
}