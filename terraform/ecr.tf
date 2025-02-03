resource "awscc_ecr_repository" "environment" {
  repository_name      = local.ecr.repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration = {
    scan_on_push = true
  }

  encryption_configuration = {
    encryption_type = "KMS"
    kms_key         = awscc_kms_key.environment.arn
  }

  tags = local.combined_tags_awscc
  #checkov:skip=CKV_AWS_51:allow customer to re-write Lambda image and re-deploy
}