resource "awscc_s3_bucket" "assets" {
  bucket_name = "${local.solution_prefix}-assets"

  public_access_block_configuration = {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }

  bucket_encryption = {
    server_side_encryption_configuration = [{
      server_side_encryption_by_default = {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = awscc_kms_alias.environment.target_key_id
      }
    }]
  }

  versioning_configuration = {
    status = "Enabled"
  }

  tags = local.combined_tags_awscc
}

resource "awscc_s3_bucket" "artifacts" {
  bucket_name = "${local.solution_prefix}-artifacts"

  public_access_block_configuration = {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }

  bucket_encryption = {
    server_side_encryption_configuration = [{
      server_side_encryption_by_default = {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = awscc_kms_alias.environment.target_key_id
      }
    }]
  }

  versioning_configuration = {
    status = "Enabled"
  }

  tags = local.combined_tags_awscc
}