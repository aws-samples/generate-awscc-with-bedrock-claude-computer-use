variable "solution_prefix" {
  description = "Prefix to be included in all resources deployed by this solution"
  type        = string
  default     = "awscc-tool-use"
}

variable "tags" {
  description = "Map of tags to apply to resources deployed by this solution."
  type        = map(any)
  default     = null
}

variable "container_platform" {
  description = "The platform for the container image, default is 'linux/amd64'"
  default     = "linux/arm64"
  type        = string
}

variable "cloudwatch_log_group_retention" {
  description = "Lambda CloudWatch log group retention period"
  type        = string
  default     = "365"
  validation {
    condition     = contains(["1", "3", "5", "7", "14", "30", "60", "90", "120", "150", "180", "365", "400", "545", "731", "1827", "3653", "0"], var.cloudwatch_log_group_retention)
    error_message = "Valid values for var: cloudwatch_log_group_retention are (1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653, and 0)."
  }
}

variable "lambda_log_level" {
  description = "Log level for the Lambda function - L1 = assistant_only, L2 = assistant_tool_use, L3 = assistant_tool_use_output, ALL = all"
  type        = string
  default     = "L1"
  validation {
    condition     = contains(["L1", "L2", "L3", "ALL"], var.lambda_log_level)
    error_message = "Valid values for var: lambda_log_level are (L1, L2, L3, ALL)."
  }

}