terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  # Profile is only used in local development, not in CI/CD
  profile = var.aws_profile != "" ? var.aws_profile : null
}
