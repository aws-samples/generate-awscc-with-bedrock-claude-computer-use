locals {
  solution_prefix = "${var.solution_prefix}-${random_string.solution_prefix.result}"
  concurrency     = 10

  ecr = {
    repository_name = "${local.solution_prefix}"
  }

  combined_tags = merge(
    var.tags,
    {
      Solution    = var.solution_prefix
      Application = "awscc_tool_use"
    }
  )

  combined_tags_awscc = [
    for k, v in local.combined_tags :
    {
      key : k,
      value : v
    }
  ]

  lambda = {
    common_inference = {
      name                        = "${local.solution_prefix}-create"
      docker_image_tag            = "inference"
      source_path                 = "${path.module}/src"
      dir_sha                     = sha1(join("", [for f in fileset("${path.module}/src", "**") : filesha1("${path.module}/src/${f}")]))
      platform                    = var.container_platform
      runtime_architecture        = var.container_platform == "linux/arm64" ? "arm64" : "x86_64"
      timeout                     = 900
      memory_size                 = 7076
      lambda_reserved_concurrency = local.concurrency
    }

    create_resource = {
      name           = "${local.solution_prefix}-create"
      description    = "Lambda function to run create resource inference from source schema"
      log_group_name = "/aws/lambda/${local.solution_prefix}-create"
      environment = {
        variables = {
          LOG_LEVEL        = var.lambda_log_level
          ASSETS_BUCKET    = awscc_s3_bucket.assets.bucket_name
          ARTIFACTS_BUCKET = awscc_s3_bucket.artifacts.bucket_name
        }
      }
    }

    delete_resource = {
      name           = "${local.solution_prefix}-delete"
      description    = "Lambda function to run delete resource from Terraform state"
      log_group_name = "/aws/lambda/${local.solution_prefix}-delete"
      environment = {
        variables = {
          LOG_LEVEL        = var.lambda_log_level
          ASSETS_BUCKET    = awscc_s3_bucket.assets.bucket_name
          ARTIFACTS_BUCKET = awscc_s3_bucket.artifacts.bucket_name
        }
      }
    }

    review_resource = {
      name           = "${local.solution_prefix}-review"
      description    = "Lambda function to run review resource configuration and add revision as needed"
      log_group_name = "/aws/lambda/${local.solution_prefix}-review"
      environment = {
        variables = {
          LOG_LEVEL        = var.lambda_log_level
          ASSETS_BUCKET    = awscc_s3_bucket.assets.bucket_name
          ARTIFACTS_BUCKET = awscc_s3_bucket.artifacts.bucket_name
        }
      }
    }

    cleaner_resource = {
      name           = "${local.solution_prefix}-cleaner"
      description    = "Lambda function to clean up resource configuration and prep it for documentation"
      log_group_name = "/aws/lambda/${local.solution_prefix}-cleaner"
      environment = {
        variables = {
          LOG_LEVEL        = var.lambda_log_level
          ASSETS_BUCKET    = awscc_s3_bucket.assets.bucket_name
          ARTIFACTS_BUCKET = awscc_s3_bucket.artifacts.bucket_name
        }
      }
    }

    summary_resource = {
      name           = "${local.solution_prefix}-summary"
      description    = "Lambda function to generate summary about the resource configuration and prep it for documentation"
      log_group_name = "/aws/lambda/${local.solution_prefix}-summary"
      environment = {
        variables = {
          LOG_LEVEL        = var.lambda_log_level
          ASSETS_BUCKET    = awscc_s3_bucket.assets.bucket_name
          ARTIFACTS_BUCKET = awscc_s3_bucket.artifacts.bucket_name
        }
      }
    }

    artifact_generator = {
      name           = "${local.solution_prefix}-artifact"
      description    = "Lambda function to generate collection of artifacts from the output of the orchestrator state machine"
      log_group_name = "/aws/lambda/${local.solution_prefix}-artifact"
      environment = {
        variables = {
          LOG_LEVEL        = var.lambda_log_level
          ASSETS_BUCKET    = awscc_s3_bucket.assets.bucket_name
          ARTIFACTS_BUCKET = awscc_s3_bucket.artifacts.bucket_name
        }
      }
    }

  }

  statemachine = {
    orchestrator = {
      name = "${local.solution_prefix}-orchestrator"
    }
  }
}

resource "random_string" "solution_prefix" {
  length  = 4
  special = false
  upper   = false
}