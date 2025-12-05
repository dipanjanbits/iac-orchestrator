# Multi-Cloud Infrastructure Orchestrator

A unified Infrastructure as Code (IaC) orchestration tool for deploying and managing resources across AWS, Azure, and GCP using Terraform with centralized configuration.

## 🌟 Features

- **Multi-Cloud Support**: Deploy infrastructure across AWS, Azure, and GCP from a single configuration
- **Centralized Configuration**: Manage all environments and cloud providers through `parameters.json`
- **S3 Remote State**: Centralized Terraform state management with S3 backend and DynamoDB locking
- **Environment Management**: Support for multiple environments (dev, prod, staging, etc.)
- **Selective Deployment**: Deploy specific clouds or modules using command-line filters
- **Automated Workflow**: Handles `init`, `validate`, `plan`, `apply`, and `destroy` operations
- **Module-Based Architecture**: Organized structure with separate modules for network and compute resources

## 📋 Prerequisites

- Python 3.7+
- Terraform >= 1.0
- AWS CLI configured with appropriate profiles
- Azure CLI (for Azure deployments)
- GCloud CLI (for GCP deployments)

## 🚀 Quick Start

### 1. Setup Backend Infrastructure

Create the S3 bucket and DynamoDB table for Terraform state management:

```powershell
.\setup-backend.ps1 -Region us-east-1 -Profile dev-profile
```

Or manually create:
- **S3 Bucket**: For storing Terraform state files
- **DynamoDB Table**: Named `terraform-state-lock` with partition key `LockID` (String type)

### 2. Configure Parameters

Edit `parameters.json` to define your infrastructure requirements:

```json
{
  "environments": {
    "dev": {
      "common": {
        "project_name": "myapp",
        "environment": "dev",
        "aws_profile": "dev-profile",
        "aws_region": "us-east-1"
      },
      "backend": {
        "enabled": true,
        "s3_bucket": "your-terraform-state-bucket",
        "s3_region": "us-east-1",
        "dynamodb_table": "terraform-state-lock"
      },
      "aws": {
        "enabled": true,
        "vpc_cidr": "172.31.0.0/16",
        "modules": {
          "compute": {
            "instances": [...]
          }
        }
      }
    }
  }
}
```

### 3. Deploy Infrastructure

**Plan deployment:**
```bash
python orchestrator.py -e dev -c aws -a plan
```

**Apply changes:**
```bash
python orchestrator.py -e dev -c aws -a apply
```

**Destroy resources:**
```bash
python orchestrator.py -e dev -c aws -a destroy
```

## 📖 Usage

### Command-Line Options

```bash
python orchestrator.py [OPTIONS]
```

| Option | Description | Required | Example |
|--------|-------------|----------|---------|
| `-e, --env` | Environment name | Yes | `dev`, `prod` |
| `-a, --action` | Terraform action | No (default: plan) | `plan`, `apply`, `destroy` |
| `-c, --clouds` | Cloud provider(s) to deploy | No (default: all) | `aws`, `azure`, `gcp` |
| `-m, --modules` | Specific module(s) to deploy | No (default: all) | `compute`, `network` |

### Examples

**Deploy all clouds for dev environment:**
```bash
python orchestrator.py -e dev -a apply
```

**Deploy only AWS compute module:**
```bash
python orchestrator.py -e dev -c aws -m compute -a apply
```

**Plan Azure infrastructure:**
```bash
python orchestrator.py -e prod -c azure -a plan
```

**Destroy all GCP resources:**
```bash
python orchestrator.py -e dev -c gcp -a destroy
```

## 📁 Project Structure

```
iac-orchestrator/
├── orchestrator.py              # Main orchestration script
├── parameters.json              # Centralized configuration
├── provider.tf                  # Root-level provider definitions
├── setup-backend.ps1           # Backend setup script
├── BACKEND_SETUP.md            # Backend configuration guide
├── README.md                    # This file
│
├── aws/
│   ├── compute/
│   │   ├── backend.tf          # S3 backend configuration
│   │   ├── provider.tf         # AWS provider configuration
│   │   ├── main.tf             # EC2 and security group resources
│   │   ├── variables.tf        # Input variables
│   │   ├── outputs.tf          # Output values (IDs, ARNs, IPs)
│   │   └── terraform.tfvars.json  # Auto-generated variables
│   └── network/
│       └── ...
│
├── azure/
│   ├── compute/
│   └── network/
│
└── gcp/
    ├── compute/
    └── network/
```

## 🔧 Configuration Details

### Backend Configuration

The orchestrator automatically generates backend configuration for each module:

```hcl
bucket = "your-terraform-state-bucket"
key = "aws/dev/terraform.tfstate"
region = "us-east-1"
encrypt = true
dynamodb_table = "terraform-state-lock"
profile = "dev-profile"
```

### Module Configuration

Each module receives:
- **Common parameters**: `project_name`, `environment`, `owner`, cloud-specific settings
- **Cloud-specific parameters**: `vpc_cidr`, region settings, etc.
- **Module-specific configuration**: Instance definitions, networking details

## 🔒 Security Best Practices

- S3 bucket encryption enabled by default
- Public access blocked on state bucket
- DynamoDB table for state locking prevents concurrent modifications
- Profile-based AWS authentication
- Separate state files per cloud provider and environment

## 📊 Outputs

After successful deployment, the orchestrator provides:
- **Instance IDs and ARNs**: Unique identifiers for created resources
- **Public/Private IPs**: Network addresses for instances
- **Security Group IDs/ARNs**: Security resource identifiers
- **Resource Names**: Tagged resource names

Example output:
```json
{
  "instance_details": [
    {
      "name": "web-server",
      "id": "i-1234567890abcdef0",
      "arn": "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
      "private_ip": "172.31.1.151",
      "public_ip": "54.123.45.67"
    }
  ]
}
```

## 🐛 Troubleshooting

### Backend Region Mismatch
**Error**: `requested bucket from "us-east-1", actual location "us-east-2"`

**Solution**: Ensure `s3_region` in `parameters.json` matches your S3 bucket's actual region.

### AWS Credentials Issues
**Error**: `No valid credential sources found`

**Solution**: 
- Verify AWS CLI profile configuration: `aws sts get-caller-identity --profile dev-profile`
- Ensure IAM user has necessary permissions for EC2, VPC, and S3 access

### DynamoDB Table Missing
**Error**: `Error acquiring state lock`

**Solution**: Create DynamoDB table with partition key `LockID` (String type)

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- Parameters are properly documented
- Changes are tested across environments

## 📝 License

This project is provided as-is for infrastructure orchestration purposes.

## 📧 Support

For issues or questions, please refer to the project documentation or contact the DevOps team.

---

**Built with ❤️ for multi-cloud infrastructure management**