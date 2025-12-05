# Multi-Cloud Infrastructure Orchestrator

A unified Infrastructure as Code (IaC) orchestration tool for deploying and managing resources across AWS, Azure, and GCP using Terraform with centralized configuration. Fully integrated with GitHub Actions for automated CI/CD pipeline deployment.

## 🌟 Features

- **Multi-Cloud Support**: Deploy infrastructure across AWS, Azure, and GCP from a single configuration
- **Centralized Configuration**: Manage all environments and cloud providers through `parameters.json`
- **S3 Remote State**: Centralized Terraform state management with S3 backend and DynamoDB locking
- **Environment Management**: Support for multiple environments (dev, prod, staging, etc.)
- **Selective Deployment**: Deploy specific clouds or modules using command-line filters
- **Automated Workflow**: Handles `init`, `validate`, `plan`, `apply`, and `destroy` operations
- **Module-Based Architecture**: Organized structure with separate modules for network and compute resources
- **GitHub Actions Integration**: Full CI/CD pipeline with runtime options for users
- **Multiple Authentication Methods**: Support for AWS Access Keys and IAM Role-based authentication
- **Dynamic Configuration**: Environment-specific and cloud-specific parameters
- **Flexible Filtering**: Deploy any combination of clouds and modules

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

---

## � Codebase Architecture

### `orchestrator.py` - Core Orchestration Engine

The main Python script that orchestrates all deployment operations. It's a class-based implementation with the following key components:

#### **MultiCloudOrchestrator Class**

**Initialization:**
```python
__init__(self, params_file, env, action='plan', clouds=None, modules=None)
```
- `params_file`: Path to parameters.json (default: 'parameters.json')
- `env`: Environment to deploy (dev, prod, staging, etc.)
- `action`: Terraform action - 'plan', 'apply', or 'destroy'
- `clouds`: List of clouds to deploy (optional filter)
- `modules`: List of modules to deploy (optional filter)

#### **Key Methods**

**1. `load_parameters()`**
- Reads and validates parameters.json
- Throws error if environment not found
- Returns environment-specific configuration

**2. `generate_tfvars(cloud, module, module_config)`**
- Merges common parameters with cloud-specific parameters
- Removes metadata fields (modules, enabled flags)
- Adds module-specific configuration
- Returns tfvars dictionary ready for Terraform

**3. `write_tfvars(cloud, module, tfvars)`**
- Creates `terraform.tfvars.json` file in module directory
- Writes tfvars with proper JSON formatting
- Location: `{cloud}/{module}/terraform.tfvars.json`

**4. `write_backend_config(cloud, module)`**
- Generates `backend.hcl` for S3 remote state
- Creates unique state key per cloud and environment
- Format: `{cloud}/{environment}/terraform.tfstate`
- Configures:
  - S3 bucket and region
  - Encryption (enabled by default)
  - DynamoDB table for state locking
  - AWS profile for authentication
  - Optional KMS key for encryption

**5. `write_root_tfvars()`**
- Creates root-level `terraform.tfvars.json`
- Contains common parameters for provider configuration

**6. `run_terraform(cloud, module)`**
- Executes Terraform commands in module directory
- Steps:
  1. `terraform init` (with backend config if available)
  2. `terraform validate`
  3. `terraform plan/apply/destroy` (based on action)
- Handles:
  - Error checking and reporting
  - Working directory management
  - Subprocess execution
- Returns status dictionary with success/failure info

**7. `orchestrate()` - Main Orchestration Logic**
- Iterates through all clouds (aws, azure, gcp)
- Applies cloud filters if specified
- For each enabled cloud:
  - Loads cloud configuration
  - Iterates through modules
  - Applies module filters if specified
  - Generates tfvars and backend config
  - Executes Terraform
- Collects and reports results

**8. `print_summary()`**
- Displays deployment summary
- Shows success/failed/skipped counts
- Details failed modules with error messages
- Exits with error code 1 if any failures

### Command-Line Interface

**Arguments:**
```bash
python orchestrator.py -e ENV [-a ACTION] [-c CLOUDS ...] [-m MODULES ...] [-p PARAMS_FILE]
```

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `-e, --environment` | string | Yes | - | Environment name (dev, prod, etc.) |
| `-a, --action` | choice | No | plan | Terraform action (plan/apply/destroy) |
| `-c, --clouds` | list | No | all | Clouds to deploy (aws/azure/gcp) |
| `-m, --modules` | list | No | all | Modules to deploy |
| `-p, --params-file` | string | No | parameters.json | Path to parameters file |

**Usage Examples:**
```bash
# Deploy AWS only in dev (plan mode)
python orchestrator.py -e dev -c aws

# Apply changes to AWS and Azure, compute module only
python orchestrator.py -e prod -a apply -c aws azure -m compute

# Destroy all resources in dev
python orchestrator.py -e dev -a destroy

# Plan multi-cloud deployment with specific modules
python orchestrator.py -e staging -c aws azure gcp -m network compute -a plan

# Deploy with custom parameters file
python orchestrator.py -e prod -c aws -a apply -p ./custom-params.json
```

---

## ⚙️ Configuration Management (`parameters.json`)

Central configuration file that defines infrastructure for each environment and cloud provider.

### Structure Overview
```json
{
  "environments": {
    "ENV_NAME": {
      "common": { /* Shared across all clouds */ },
      "backend": { /* S3 state management */ },
      "aws": { /* AWS-specific config */ },
      "azure": { /* Azure-specific config */ },
      "gcp": { /* GCP-specific config */ }
    }
  }
}
```

### Section Details

#### **1. `common` Section**
Shared parameters applied to all cloud deployments:
```json
{
  "project_name": "myapp",
  "environment": "dev",
  "owner": "devops-team",
  "aws_profile": "dev-profile",
  "aws_region": "us-east-1",
  "azure_subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "azure_tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "gcp_project_id": "my-gcp-project-dev",
  "gcp_region": "us-central1"
}
```

#### **2. `backend` Section**
S3 remote state configuration:
```json
{
  "enabled": true,
  "s3_bucket": "dip-terraform-state-2025",
  "s3_region": "us-east-1",
  "dynamodb_table": "terraform-state-lock",
  "encrypt": true,
  "profile": "dev-profile"
}
```

**Parameters:**
- `enabled`: Enable/disable remote state
- `s3_bucket`: S3 bucket for state storage
- `s3_region`: Bucket region (must match actual S3 region)
- `dynamodb_table`: Table for state locking
- `encrypt`: Enable state encryption (recommended: true)
- `profile`: AWS profile for access

#### **3. Cloud-Specific Sections (aws, azure, gcp)**

**AWS Section:**
```json
{
  "vpc_cidr": "172.31.0.0/16",
  "enabled": true,
  "modules": {
    "compute": {
      "instances": [
        {
          "name": "web-server",
          "instance_type": "t3.micro",
          "ami": "ami-0fa3fe0fa7920f68e",
          "subnet_index": 0,
          "tags": {"Role": "web", "Tier": "frontend"}
        }
      ]
    },
    "network": {
      "subnet_count": 2,
      "availability_zones": ["us-east-1a", "us-east-1b"]
    }
  }
}
```

**Azure Section:**
```json
{
  "location": "eastus",
  "vnet_cidr": "10.1.0.0/16",
  "enabled": true,
  "modules": {
    "compute": {
      "instances": [
        {
          "name": "web-vm-1",
          "vm_size": "Standard_D2s_v3",
          "image": {
            "publisher": "Canonical",
            "offer": "UbuntuServer",
            "sku": "18.04-LTS",
            "version": "latest"
          },
          "tags": {"Role": "web"}
        }
      ]
    }
  }
}
```

**GCP Section:**
```json
{
  "vpc_cidr": "10.2.0.0/16",
  "enabled": true,
  "modules": {
    "compute": {
      "instances": [
        {
          "name": "web-instance-1",
          "machine_type": "n1-standard-2",
          "zone": "us-central1-a",
          "image": "debian-cloud/debian-11",
          "tags": ["web", "frontend"]
        }
      ]
    }
  }
}
```

### Environment Configuration Examples

**Development Environment:**
- Smaller instance types (t3.micro, Standard_D2s_v3)
- Single subnet deployment
- Cost-optimized settings
- Fewer compute instances

**Production Environment:**
- Larger instance types (t3.xlarge, Standard_D4s_v3)
- Multiple availability zones
- High availability configuration
- Auto-scaling ready
- Security-hardened settings

---

## 🏗️ Terraform Module Structure

### Directory Layout
```
terraform/
├── provider.tf              # Root-level provider definitions
├── terraform.tfvars.json   # Auto-generated common parameters
│
├── aws/
│   ├── compute/
│   │   ├── main.tf          # EC2, security groups, autoscaling
│   │   ├── variables.tf     # Input variable definitions
│   │   ├── outputs.tf       # Instance IDs, IPs, security group IDs
│   │   ├── provider.tf      # AWS provider configuration
│   │   ├── backend.tf       # S3 backend reference
│   │   ├── backend.hcl      # Auto-generated backend config
│   │   └── terraform.tfvars.json # Auto-generated variables
│   │
│   └── network/
│       ├── main.tf          # VPC, subnets, route tables
│       ├── variables.tf     # Network variables
│       ├── outputs.tf       # Network resource IDs
│       ├── provider.tf      # AWS provider
│       ├── backend.tf       # Backend reference
│       ├── backend.hcl      # Auto-generated
│       └── terraform.tfvars.json
│
├── azure/
│   ├── compute/
│   │   ├── main.tf          # VMs, load balancers
│   │   ├── variables.tf     # VM variables
│   │   ├── outputs.tf       # VM details
│   │   ├── provider.tf      # Azure provider
│   │   ├── backend.tf
│   │   ├── backend.hcl
│   │   └── terraform.tfvars.json
│   │
│   └── network/
│       └── (similar structure)
│
└── gcp/
    ├── compute/
    │   └── (similar structure)
    │
    └── network/
        └── (similar structure)
```

### Module Contents

#### **Compute Modules**
- EC2/VM instance creation
- Security group/firewall rules
- Key pair management
- Instance tags and metadata
- Load balancer configuration
- Auto-scaling groups (where applicable)

#### **Network Modules**
- VPC/Virtual Network creation
- Subnet provisioning
- Route table configuration
- Internet gateway setup
- NAT gateway configuration
- VPN/connectivity setup

### Variable Flow

```
parameters.json
    ↓
orchestrator.py generates:
    ├── backend.hcl (for state management)
    ├── terraform.tfvars.json (module variables)
    └── root terraform.tfvars.json (common)
    ↓
Terraform modules receive:
    ├── Common parameters (project_name, environment, owner)
    ├── Cloud-specific settings (regions, credentials)
    ├── Module configuration (instances, networks)
    └── Backend configuration (S3, DynamoDB)
```

---

## �🚀 GitHub Actions Integration

This project includes fully configured GitHub Actions workflows for CI/CD pipeline automation. Users can trigger deployments with custom runtime options through the GitHub UI.

### 📋 Available Workflows

#### 1. **Main Deployment Workflow** (`.github/workflows/deploy.yml`)
Triggered manually with full configuration options.

**Runtime Inputs:**
- **Environment**: `dev`, `prod`, `staging`
- **Action**: `plan`, `apply`, `destroy`
- **Cloud Providers**: `aws`, `azure`, `gcp`, or any combination
- **Modules**: `compute`, `network`, or both
- **Auto-approve**: `true` or `false` (auto-approve apply/destroy)
- **Verbose Output**: `true` or `false`

**How to use:**
1. Go to repository → Actions tab
2. Select "Deploy Infrastructure" workflow
3. Click "Run workflow"
4. Fill in the required inputs
5. Click "Run workflow"

#### 2. **Pull Request Workflow** (`.github/workflows/pr-validate.yml`)
Automatically triggers on pull requests to validate Terraform configurations.

**What it does:**
- Runs `terraform init` and `validate` for all configurations
- Generates Terraform plans and posts them as PR comments
- Validates syntax and module integrity

#### Example Workflow Triggers

**Scenario 1: Plan AWS infrastructure for dev environment**
```
Environment: dev
Action: plan
Cloud Providers: aws
Modules: all
Auto-approve: false
Verbose Output: true
```

**Scenario 2: Apply changes to prod environment**
```
Environment: prod
Action: apply
Cloud Providers: aws,azure
Modules: compute
Auto-approve: true
Verbose Output: false
```

**Scenario 3: Destroy all GCP resources**
```
Environment: dev
Action: destroy
Cloud Providers: gcp
Modules: all
Auto-approve: true
Verbose Output: false
```

---

## 🔐 GitHub Secrets Setup

### Prerequisites

Before using the GitHub Actions workflows, you need to set up authentication credentials. Choose one of two methods:

### Method 1: AWS Access Key & Secret Key (Recommended for Testing)

**Step 1: Generate AWS Credentials**
```powershell
# Login to AWS Console
# Navigate to IAM → Users → Security Credentials
# Under Access keys section, click "Create access key"
# Download and save the Access Key ID and Secret Access Key
```

**Step 2: Add GitHub Secrets**

Go to your GitHub repository:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS Access Key ID |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Access Key |
| `AWS_REGION` | Region (e.g., `us-east-1`) |

**Step 3: Verify Setup**
```powershell
# In your local terminal, verify credentials work:
$env:AWS_ACCESS_KEY_ID = "your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
aws sts get-caller-identity
```

### Method 2: IAM Role-Based Authentication (Recommended for Production)

**Step 1: Create GitHub OIDC Provider in AWS**
```powershell
# Run this once to set up OIDC provider
aws iam create-open-id-connect-provider `
  --url "https://token.actions.githubusercontent.com" `
  --client-id-list "sts.amazonaws.com" `
  --thumbprint-list "1b511abead59c6ce207077c0ef0302505b9c6e8c"
```

**Step 2: Create IAM Role for GitHub Actions**
```powershell
# Create trust policy (save as trust-policy.json)
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/iac-orchestrator:*"
        }
      }
    }
  ]
}
"@ | Out-File trust-policy.json

# Create role
aws iam create-role `
  --role-name github-actions-iac-orchestrator `
  --assume-role-policy-document file://trust-policy.json

# Attach policy for necessary permissions
aws iam attach-role-policy `
  --role-name github-actions-iac-orchestrator `
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

**Step 3: Add GitHub Secret**

Go to your GitHub repository:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:

| Secret Name | Value |
|-------------|-------|
| `AWS_ROLE_ARN` | `arn:aws:iam::YOUR_ACCOUNT_ID:role/github-actions-iac-orchestrator` |

### Secrets Configuration Summary

**For AWS Access Key Method:**
```yaml
Secrets needed:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION
```

**For IAM Role Method:**
```yaml
Secrets needed:
  - AWS_ROLE_ARN
```

**For Azure Deployments (if enabled):**
```yaml
Secrets needed:
  - AZURE_CLIENT_ID
  - AZURE_CLIENT_SECRET
  - AZURE_TENANT_ID
  - AZURE_SUBSCRIPTION_ID
```

**For GCP Deployments (if enabled):**
```yaml
Secrets needed:
  - GCP_PROJECT_ID
  - GCP_SA_KEY (base64 encoded service account JSON)
```

---

## 🔧 GitHub Actions Workflow Files

### Deploy Workflow (`deploy.yml`)

The deployment workflow accepts the following inputs at runtime:

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod
      
      action:
        description: 'Terraform action to perform'
        required: true
        type: choice
        options:
          - plan
          - apply
          - destroy
      
      clouds:
        description: 'Cloud providers (comma-separated: aws,azure,gcp)'
        required: false
        default: 'aws'
      
      modules:
        description: 'Modules to deploy (comma-separated: network,compute)'
        required: false
        default: 'network,compute'
      
      auto_approve:
        description: 'Auto-approve apply/destroy actions'
        required: false
        type: boolean
        default: false
      
      verbose:
        description: 'Enable verbose output'
        required: false
        type: boolean
        default: false
```

### Pull Request Workflow (`pr-validate.yml`)

Automatically validates all Terraform configurations on every pull request:
- Runs `terraform fmt -check` to validate formatting
- Runs `terraform validate` for syntax validation
- Generates Terraform plans and posts them as comments
- Checks for common configuration errors

---

## 🔄 Workflow Execution Steps

### Deploy Workflow Steps

1. **Checkout Code**: Clones the repository
2. **Setup Python**: Installs Python 3.11
3. **Setup Terraform**: Installs Terraform
4. **Configure AWS Credentials**: 
   - Option A: Uses Access Keys from GitHub secrets
   - Option B: Assumes IAM role via OIDC
5. **Install Dependencies**: Installs Python packages
6. **Execute Orchestrator**: Runs the orchestrator with specified options
7. **Upload Logs**: Archives and uploads execution logs
8. **Post Results**: Posts summary to workflow run

### Example Workflow Run

**Input:**
```
Environment: dev
Action: plan
Clouds: aws
Modules: compute
Verbose: true
```

**Execution:**
```bash
python orchestrator.py \
  -e dev \
  -a plan \
  -c aws \
  -m compute \
  -v
```

**Output:**
- Terraform plan results
- Resource changes summary
- Any warnings or errors
- Execution time

---

## 📊 Environment Configuration

### Parameters Configuration

Edit `parameters.json` to define your infrastructure for each environment and cloud provider:

```json
{
  "environments": {
    "dev": {
      "common": {
        "project_name": "myapp",
        "environment": "dev",
        "owner": "devops-team",
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
            "instances": [
              {
                "name": "web-server-1",
                "ami": "ami-0c55b159cbfafe1f0",
                "instance_type": "t3.micro",
                "availability_zone": "us-east-1a",
                "private_ip": "172.31.1.100"
              }
            ]
          },
          "network": {
            "security_groups": [
              {
                "name": "web-sg",
                "description": "Security group for web servers",
                "ingress_rules": [
                  {
                    "from_port": 80,
                    "to_port": 80,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"]
                  },
                  {
                    "from_port": 443,
                    "to_port": 443,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"]
                  }
                ]
              }
            ]
          }
        }
      }
    },
    "prod": {
      "common": {
        "project_name": "myapp",
        "environment": "prod",
        "owner": "devops-team",
        "aws_profile": "prod-profile",
        "aws_region": "us-west-2"
      },
      "backend": {
        "enabled": true,
        "s3_bucket": "your-terraform-state-bucket-prod",
        "s3_region": "us-west-2",
        "dynamodb_table": "terraform-state-lock-prod"
      },
      "aws": {
        "enabled": true,
        "vpc_cidr": "10.0.0.0/16",
        "modules": {
          "compute": {
            "instances": [
              {
                "name": "prod-web-1",
                "ami": "ami-0c55b159cbfafe1f0",
                "instance_type": "t3.small",
                "availability_zone": "us-west-2a",
                "private_ip": "10.0.1.100"
              },
              {
                "name": "prod-web-2",
                "ami": "ami-0c55b159cbfafe1f0",
                "instance_type": "t3.small",
                "availability_zone": "us-west-2b",
                "private_ip": "10.0.2.100"
              }
            ]
          },
          "network": {
            "security_groups": [
              {
                "name": "prod-web-sg",
                "description": "Security group for production web servers",
                "ingress_rules": [
                  {
                    "from_port": 80,
                    "to_port": 80,
                    "protocol": "tcp",
                    "cidr_blocks": ["10.0.0.0/8"]
                  }
                ]
              }
            ]
          }
        }
      }
    }
  }
}
```

---

## 🔒 Security Best Practices

### Secrets Management
- **Never commit secrets** to the repository
- Use GitHub Secrets for all sensitive data
- Rotate credentials regularly
- Use the least privilege principle for IAM roles
- Enable secret scanning in repository settings

### Workflow Security
- Review workflow files before merging
- Restrict workflow permissions in settings
- Use branch protection rules
- Audit GitHub Actions logs regularly
- Limit who can trigger manual workflows

### Infrastructure Security
- Enable S3 bucket encryption
- Enable MFA delete on state bucket
- Use VPC endpoints for private deployments
- Implement network segmentation
- Regular security audits

### AWS Best Practices
- Use IAM roles instead of access keys when possible
- Enable CloudTrail logging for audit trails
- Implement resource tagging for cost allocation
- Use security groups with minimal permissions
- Enable VPC Flow Logs for network monitoring

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- Parameters are properly documented
- Changes are tested across environments
- Security best practices are followed

---

## 📝 License

This project is provided as-is for infrastructure orchestration purposes.

## 📧 Support

For issues or questions, please refer to the project documentation or contact the DevOps team.

---

## 📚 Quick Reference

### Common Workflow Scenarios

**Plan Changes in Dev:**
- Environment: `dev`
- Action: `plan`
- Clouds: `aws`
- Auto-approve: `false`

**Apply to Production:**
- Environment: `prod`
- Action: `apply`
- Clouds: `aws`
- Auto-approve: `true` (after reviewing plan)

**Destroy Test Resources:**
- Environment: `dev`
- Action: `destroy`
- Clouds: `azure`
- Auto-approve: `true`

**Multi-Cloud Deployment:**
- Environment: `prod`
- Action: `apply`
- Clouds: `aws,azure,gcp`
- Modules: `network,compute`
- Auto-approve: `false`

---

**Built with ❤️ for multi-cloud infrastructure management**