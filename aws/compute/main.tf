# Data source to get VPC info by CIDR block
data "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}

# Create security group
resource "aws_security_group" "instance" {
  name_prefix = "${var.project_name}-${var.environment}-"
  description = "Security group for EC2 instances"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-sg"
  }
}

# Create multiple EC2 instances based on configuration
resource "aws_instance" "this" {
  count = length(var.module_config.instances)

  ami           = var.module_config.instances[count.index].ami
  instance_type = var.module_config.instances[count.index].instance_type
  
  subnet_id              = data.aws_subnets.public.ids[var.module_config.instances[count.index].subnet_index]
  vpc_security_group_ids = [aws_security_group.instance.id]

  tags = merge(
    {
      Name = "${var.project_name}-${var.environment}-${var.module_config.instances[count.index].name}"
    },
    var.module_config.instances[count.index].tags
  )
}