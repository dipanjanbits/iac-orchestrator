output "instance_ids" {
  description = "IDs of created instances"
  value       = aws_instance.this[*].id
}

output "instance_details" {
  description = "Detailed information about instances"
  value = [
    for idx, instance in aws_instance.this : {
      name       = var.module_config.instances[idx].name
      id         = instance.id
      arn        = instance.arn
      private_ip = instance.private_ip
      public_ip  = instance.public_ip
    }
  ]
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.instance.id
}

output "security_group_arn" {
  description = "Security group ARN"
  value       = aws_security_group.instance.arn
}