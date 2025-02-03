<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >=5.8.0 |
| <a name="requirement_awscc"></a> [awscc](#requirement\_awscc) | >= 0.78.0 |
| <a name="requirement_docker"></a> [docker](#requirement\_docker) | >=3.0.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | >=2.5.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | >= 3.2.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 3.6.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >=5.8.0 |
| <a name="provider_awscc"></a> [awscc](#provider\_awscc) | >= 0.78.0 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 3.6.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_docker_image_inference_lambda"></a> [docker\_image\_inference\_lambda](#module\_docker\_image\_inference\_lambda) | terraform-aws-modules/lambda/aws//modules/docker-build | 7.7.0 |

## Resources

| Name | Type |
|------|------|
| [aws_iam_role_policy.artifact_generator](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.cleaner_resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.create_resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.delete_resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.orchestrator](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.review_resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.summary_resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.create_administrator](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.delete_administrator](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.review_administrator](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [awscc_ecr_repository.environment](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/ecr_repository) | resource |
| [awscc_iam_role.artifact_generator](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_iam_role.cleaner_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_iam_role.create_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_iam_role.delete_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_iam_role.orchestrator](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_iam_role.review_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_iam_role.summary_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/iam_role) | resource |
| [awscc_kms_alias.environment](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/kms_alias) | resource |
| [awscc_kms_key.environment](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/kms_key) | resource |
| [awscc_lambda_function.artifact_generator](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/lambda_function) | resource |
| [awscc_lambda_function.cleaner_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/lambda_function) | resource |
| [awscc_lambda_function.create_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/lambda_function) | resource |
| [awscc_lambda_function.delete_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/lambda_function) | resource |
| [awscc_lambda_function.review_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/lambda_function) | resource |
| [awscc_lambda_function.summary_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/lambda_function) | resource |
| [awscc_logs_log_group.artifact_generator](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_logs_log_group.cleaner_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_logs_log_group.create_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_logs_log_group.delete_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_logs_log_group.orchestrator](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_logs_log_group.review_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_logs_log_group.summary_resource](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/logs_log_group) | resource |
| [awscc_s3_bucket.artifacts](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/s3_bucket) | resource |
| [awscc_s3_bucket.assets](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/s3_bucket) | resource |
| [awscc_stepfunctions_state_machine.orchestrator](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/stepfunctions_state_machine) | resource |
| [random_string.solution_prefix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_ecr_authorization_token.token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ecr_authorization_token) | data source |
| [aws_iam_policy.administrator](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy) | data source |
| [aws_iam_policy_document.artifact_generator_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.environment_kms_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.inference_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_assume_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.orchestrator_statemachine](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.statemachine_assume_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cloudwatch_log_group_retention"></a> [cloudwatch\_log\_group\_retention](#input\_cloudwatch\_log\_group\_retention) | Lambda CloudWatch log group retention period | `string` | `"365"` | no |
| <a name="input_container_platform"></a> [container\_platform](#input\_container\_platform) | The platform for the container image, default is 'linux/amd64' | `string` | `"linux/arm64"` | no |
| <a name="input_lambda_log_level"></a> [lambda\_log\_level](#input\_lambda\_log\_level) | Log level for the Lambda function - L1 = assistant\_only, L2 = assistant\_tool\_use, L3 = assistant\_tool\_use\_output, ALL = all | `string` | `"L1"` | no |
| <a name="input_solution_prefix"></a> [solution\_prefix](#input\_solution\_prefix) | Prefix to be included in all resources deployed by this solution | `string` | `"awscc-tool-use"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Map of tags to apply to resources deployed by this solution. | `map(any)` | `null` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
