terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">=5.8.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = ">= 0.78.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.6.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">=2.5.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = ">=3.0.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

provider "awscc" {
  region = "us-west-2"
}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}