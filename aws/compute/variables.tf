variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "default"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "owner" {
  description = "Owner tag"
  type        = string
  default     = ""
}

variable "module_config" {
  description = "Module-specific configuration"
  type = object({
    instances = list(object({
      name          = string
      instance_type = string
      ami           = string
      subnet_index  = number
      tags          = optional(map(string), {})
    }))
  })
}