# GitHub Actions Workflow Guide

## Overview

This GitHub Actions workflow provides automated CI/CD pipelines for the Terraform Multi-Cloud Orchestrator with two distinct workflows:

1. **Pull Request Workflow** (`terraform-plan-pr.yml`) - Automatic validation and planning on PRs
2. **Manual Deployment Workflow** (`terraform-deploy.yml`) - User-triggered deployments with runtime configuration

Both workflows are designed to work seamlessly in CI/CD environments without requiring AWS profiles or local credential files.

---

## Workflows

### 1. Pull Request Workflow (Automatic)

**Trigger**: Automatically runs on pull requests to `main` or `develop` branches

**Purpose**: 
- Validates Terraform configurations
- Generates plans for both `dev` and `prod` environments
- Posts plan results as PR comments
- Ensures code quality before merging

**What it checks**:
- Changes to `orchestrator.py`
- Changes to `parameters.json`
- Changes to any Terraform files in `aws/`, `azure/`, or `gcp/` directories
- Changes to workflow files

**Process**:
1. Runs in parallel for both `dev` and `prod` environments
2. Configures cloud credentials from GitHub secrets
3. Cleans any cached Terraform state
4. Executes `terraform plan` for each environment
5. Comments results on the PR

**Example Output**:
```
## Terraform Plan - dev
✓ Plan completed for dev environment
📝 Review the logs for detailed changes
```

---

### 2. Manual Deployment Workflow (On-Demand)

**Trigger**: Manually via GitHub Actions UI

**Purpose**: Deploy infrastructure changes to specific environments with granular control

**How to trigger**:
1. Go to your GitHub repository
2. Click on the **Actions** tab
3. Select **Deploy Multi-Cloud Infrastructure**
4. Click **Run workflow**
5. Fill in the required and optional parameters
6. Click **Run workflow** button

---

## Required Secrets Configuration

⚠️ **CRITICAL**: Set these secrets in your GitHub repository before running workflows:

**Location**: `Settings → Secrets and variables → Actions`

### AWS Authentication (Choose ONE method)

#### Method 1: Access Keys (Currently Configured - Simple but less secure)
- `AWS_ACCESS_KEY_ID` - Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret access key
- `AWS_REGION` - AWS region (optional, defaults to `us-east-1`)

**Pros**: Simple setup, works immediately  
**Cons**: Long-lived credentials, less secure

#### Method 2: OIDC with IAM Role (Recommended - More Secure)
- `AWS_ROLE_ARN` - IAM role ARN configured for GitHub OIDC
- `AWS_REGION` - AWS region (optional, defaults to `us-east-1`)

**Pros**: No long-lived credentials, more secure, follows AWS best practices  
**Cons**: Requires IAM role setup with trust policy

**To switch to OIDC**: 
1. Create an IAM role with GitHub OIDC trust policy
2. Add `AWS_ROLE_ARN` secret to GitHub
3. Uncomment OIDC section in workflow files
4. Comment out access key section

### Azure Authentication
- `AZURE_CLIENT_ID` - Azure service principal client ID
- `AZURE_CLIENT_SECRET` - Azure service principal client secret
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_TENANT_ID` - Azure tenant ID

### GCP Authentication
- `GCP_SA_KEY` - GCP service account JSON key

---

## CI/CD Features

### Automatic CI/CD Detection
The orchestrator automatically detects when running in CI/CD environments and:
- ✅ Removes AWS profile requirements
- ✅ Uses environment variables for authentication
- ✅ Skips profile configuration in backend state
- ✅ Adapts provider configuration automatically

**Detection Indicators**:
- `GITHUB_ACTIONS` environment variable
- `CI` environment variable
- Other CI/CD platform indicators (GitLab, Jenkins, CircleCI, Travis)

### Terraform Cache Management
Both workflows automatically clean cached Terraform files to prevent stale configuration issues:
- `.terraform` directories
- `terraform.tfvars.json` files
- `backend.hcl` files
- `.terraform.lock.hcl` files

### Authentication Flow

```
┌─────────────────────────────────────────┐
│   GitHub Actions Workflow Starts        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Configure AWS Credentials Action      │
│   (Sets AWS_* environment variables)    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Verify AWS Identity                   │
│   (aws sts get-caller-identity)         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Clean Terraform Cache                 │
│   (Remove stale configurations)         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Run Orchestrator                      │
│   (Detects CI/CD, removes profiles)     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Terraform Uses Environment Variables  │
│   (No profile required)                 │
└─────────────────────────────────────────┘
```

---

## Available Parameters

### Required Parameters

#### **Environment** ⚠️
- **Description**: The environment to deploy to
- **Type**: Dropdown/Choice
- **Available Options**: 
  - `dev` - Development environment
  - `prod` - Production environment
  - `staging` - Staging environment (if configured)
- **Default**: None (must be selected)
- **Example**: Select `dev` for development deployment

#### **Action** ⚠️
- **Description**: The Terraform action to perform
- **Type**: Dropdown/Choice
- **Available Options**:
  - `plan` - Generate and display an execution plan (safe, no changes)
  - `apply` - Apply the Terraform changes (creates/updates resources)
  - `destroy` - Destroy the infrastructure (removes resources)
- **Default**: None (must be selected)
- **Example**: Select `plan` to preview changes before applying

### Optional Parameters

#### **Clouds**
- **Description**: Specific cloud provider(s) to deploy to
- **Type**: Text input (comma-separated)
- **Available Options**: `aws`, `azure`, `gcp`
- **Default**: `aws` (deploys to AWS only by default)
- **Format**: Comma-separated values
- **Examples**:
  - `aws` - Deploy to AWS only
  - `aws,azure` - Deploy to AWS and Azure
  - `aws,azure,gcp` - Deploy to all three clouds
- **Use Case**: When you only want to update infrastructure in specific cloud providers

#### **Modules**
- **Description**: Specific module(s) to deploy
- **Type**: Text input (comma-separated)
- **Available Modules**: `network`, `compute`
- **Default**: `compute` (deploys compute module only by default)
- **Format**: Comma-separated values
- **Examples**:
  - `network` - Deploy only network infrastructure
  - `compute` - Deploy only compute resources
  - `network,compute` - Deploy both modules
- **Use Case**: When you need to update only specific infrastructure components

#### **Auto Approve**
- **Description**: Automatically approve apply/destroy actions without manual confirmation
- **Type**: Boolean (checkbox)
- **Default**: `false` (manual approval required)
- **Use Case**: 
  - Automated deployments in dev environment
  - CI/CD pipeline automation
  - ⚠️ Use with caution in production

## Common Workflows

### 1. Preview Changes (Safest Option)
```
Environment: dev
Action: plan
Clouds: aws
Modules: compute
Auto Approve: false
```
**What it does**: Shows all changes for AWS compute resources in dev environment

### 2. Deploy Network to AWS Only
```
Environment: prod
Action: apply
Clouds: aws
Modules: network
Auto Approve: false
```
**What it does**: Deploys network infrastructure changes for AWS in prod environment (requires manual approval)

### 3. Automated Dev Deployment
```
Environment: dev
Action: apply
Clouds: aws
Modules: compute
Auto Approve: true
```
**What it does**: Automatically deploys compute resources to AWS dev without manual confirmation

### 4. Multi-Cloud Network Update
```
Environment: prod
Action: plan
Clouds: aws,azure
Modules: network
Auto Approve: false
```
**What it does**: Plans network infrastructure changes to AWS and Azure in production

### 5. Destroy Dev Environment
```
Environment: dev
Action: destroy
Clouds: aws
Modules: compute
Auto Approve: false
```
**What it does**: Destroys compute infrastructure in dev environment (requires confirmation)

### 6. Update Only Compute Resources
```
Environment: prod
Action: apply
Clouds: aws,azure
Modules: compute
Auto Approve: false
```
**What it does**: Updates compute resources in AWS and Azure

---

## Workflow Execution Steps

### Pull Request Workflow
1. **Checkout Code** - Fetches the PR branch code
2. **Setup Python** - Installs Python 3.11
3. **Setup Terraform** - Installs latest Terraform version
4. **Configure Cloud Credentials** - Sets up AWS, Azure, and GCP credentials from secrets
5. **Clean Terraform Cache** - Removes any stale cached files
6. **Run Terraform Plan** - Executes plan for the environment (dev/prod in parallel)
7. **Comment Plan Result** - Posts plan summary to the PR

### Deployment Workflow
1. **Checkout Code** - Fetches the latest code from repository
2. **Setup Python** - Installs Python 3.11
3. **Setup Terraform** - Installs Terraform version specified in environment
4. **Configure AWS Credentials** - Sets up AWS authentication (access keys or OIDC)
5. **Verify AWS Identity** - Confirms AWS credentials are working
6. **Clean Terraform Cache** - Removes cached Terraform files to ensure fresh state
7. **Prepare Environment** - Displays selected configuration parameters
8. **Run Orchestrator** - Executes the deployment command with specified parameters
9. **Upload Terraform Logs** - Saves Terraform state and plan files as artifacts

---

## Required Secrets

Set these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

### AWS
- `AWS_ROLE_TO_ASSUME` - IAM role ARN for AWS deployment
- `AWS_REGION` - AWS region (e.g., `us-east-1`)

### Azure
- `AZURE_CLIENT_ID` - Azure service principal client ID
- `AZURE_CLIENT_SECRET` - Azure service principal client secret
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_TENANT_ID` - Azure tenant ID

### GCP
- `GCP_SA_KEY` - GCP service account JSON key (base64 encoded)

## Environment Configuration

The available environments and their cloud configurations are defined in `parameters.json`:

- **dev** environment:
  - AWS: ✅ Enabled
  - Azure: ✅ Enabled
  - GCP: ❌ Disabled

- **prod** environment:
  - Configure as needed based on your `parameters.json`

To add new environments:
1. Update `parameters.json` with new environment configuration
2. Add the environment name to workflow input choices (if using manual workflow)
3. The orchestrator automatically supports new environments

---

## Provider Configuration

### AWS Provider
The AWS provider is configured to work in both local and CI/CD environments:

```hcl
provider "aws" {
  region = var.aws_region
  # Profile is only used in local development, not in CI/CD
  # In CI/CD, AWS credentials come from environment variables
  profile = var.aws_profile != "" ? var.aws_profile : null
}
```

**Local Development**: Uses AWS profile from `parameters.json`  
**CI/CD Environment**: Uses `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables

### Backend Configuration
Remote state backend automatically adapts to CI/CD:
- **Local**: Uses AWS profile from `parameters.json`
- **CI/CD**: Uses environment variables, skips profile configuration

---

## Understanding the Orchestrator Command

The workflow builds a command based on your inputs:

```bash
# Example with all parameters specified
python orchestrator.py -e dev -a plan -c aws azure -m network compute

# Parameters breakdown:
# -e dev              → environment
# -a plan             → action (plan/apply/destroy)
# -c aws azure        → specific clouds (optional)
# -m network compute  → specific modules (optional)
```

## Tips & Best Practices

### ✅ Do's
- ✅ Always run `plan` first before `apply` in production
- ✅ Use Pull Request workflow for code review and validation
- ✅ Specify clouds and modules when updating specific resources
- ✅ Review the workflow summary and logs before confirming changes
- ✅ Use access keys for quick setup, migrate to OIDC for production
- ✅ Test changes in dev environment before applying to prod
- ✅ Keep `parameters.json` version controlled and reviewed
- ✅ Rotate AWS access keys regularly if not using OIDC
- ✅ Use auto-approve cautiously and only in dev environments

### ❌ Don'ts
- ❌ Don't run `destroy` in production without planning first
- ❌ Don't store secrets in code or commit them to repository
- ❌ Don't use long-lived credentials in production (prefer OIDC)
- ❌ Don't skip the Pull Request workflow for infrastructure changes
- ❌ Don't specify invalid cloud or module names
- ❌ Don't run apply without reviewing the plan output
- ❌ Don't use auto-approve in production environments
- ❌ Don't ignore Terraform warnings and validation errors

---

## Security Best Practices

### Credential Management
1. **Use GitHub Secrets**: Never hardcode credentials in workflow files
2. **Rotate Regularly**: Change access keys every 90 days
3. **Principle of Least Privilege**: Grant only necessary permissions
4. **Prefer OIDC**: Use temporary credentials over long-lived keys
5. **Audit Access**: Review who has access to secrets regularly

### Workflow Security
1. **Require PR Reviews**: Enforce code review for infrastructure changes
2. **Branch Protection**: Protect main/prod branches from direct pushes
3. **Status Checks**: Require successful plan before allowing merge
4. **Limit Auto-Approve**: Use only for non-critical environments
5. **Monitor Actions**: Review workflow run logs regularly

### State File Security
1. **Encrypt Backend**: Enable S3 bucket encryption for state files
2. **Restrict Access**: Limit who can access state storage
3. **Enable Versioning**: Keep S3 versioning on for state recovery
4. **Lock State**: Use DynamoDB for state locking to prevent conflicts

---

## Troubleshooting

### "Credentials could not be loaded" Error
**Symptom**: `Error: Credentials could not be loaded, please check your action inputs`

**Causes**:
1. GitHub secrets not configured correctly
2. Wrong authentication method selected in workflow
3. Secrets not accessible to workflow

**Solutions**:
- ✅ Verify secrets exist: Go to `Settings → Secrets and variables → Actions`
- ✅ Check secret names match exactly: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- ✅ If using OIDC, ensure `AWS_ROLE_ARN` is set and IAM role trust policy is correct
- ✅ Confirm secrets are not expired or rotated

### "Failed to get shared config profile, default" Error
**Symptom**: `Error: failed to get shared config profile, default`

**Causes**:
1. Old cached Terraform state with profile configuration
2. AWS profile referenced but not available in CI/CD
3. Provider configuration not updated

**Solutions**:
- ✅ Ensure latest code is deployed (provider.tf updated)
- ✅ Workflow now automatically cleans cache before running
- ✅ Verify `aws_profile` variable default is empty string `""`
- ✅ Check provider.tf has conditional: `profile = var.aws_profile != "" ? var.aws_profile : null`

### Workflow Failed with "Environment Not Found"
**Symptom**: Environment configuration error

**Solutions**:
- ✅ Check that the environment name matches exactly with entries in `parameters.json`
- ✅ Ensure the environment is properly configured with all required fields
- ✅ Verify JSON syntax is valid

### "Cloud not configured for this environment"
**Symptom**: Cloud provider not available for selected environment

**Solutions**:
- ✅ Verify the cloud provider is enabled in `parameters.json` for the selected environment
- ✅ Check that credentials are set correctly in GitHub secrets
- ✅ Ensure `enabled: true` is set for the cloud in parameters

### Terraform Validation Errors
**Symptoms**: Syntax or configuration errors

**Solutions**:
- ✅ Ensure all `.tf` files in module directories are syntactically correct
- ✅ Check that variable names and types match across files
- ✅ Verify `provider.tf` is correctly configured
- ✅ Run `terraform validate` locally before committing

### Terraform Init Fails
**Symptoms**: Backend initialization errors

**Solutions**:
- ✅ Verify S3 bucket exists and is accessible
- ✅ Check DynamoDB table exists for state locking
- ✅ Ensure AWS credentials have permissions for S3 and DynamoDB
- ✅ Confirm backend configuration in `parameters.json` is correct

### Authentication Issues
**Symptoms**: Permission denied, unauthorized, or access errors

**Solutions**:
- ✅ Verify all required secrets are set in the repository
- ✅ Check that credentials have appropriate IAM/permissions for resources
- ✅ Ensure service account keys are not expired
- ✅ For AWS, verify IAM user/role has necessary policies attached
- ✅ Test credentials locally with AWS CLI: `aws sts get-caller-identity`

### CI/CD Detection Not Working
**Symptom**: Orchestrator using local profile in CI/CD

**Solutions**:
- ✅ Verify `GITHUB_ACTIONS` environment variable is set (GitHub sets this automatically)
- ✅ Check orchestrator logs for "Running in CI/CD environment" message
- ✅ Run test script locally: `python test_cicd_detection.py`

---

## Viewing Results

1. Go to **Actions** tab in your GitHub repository
2. Click on the completed workflow run
3. View step-by-step logs in the workflow details
4. Check the **Summary** for deployment status
5. Review any errors or warnings in the logs

## Advanced Usage

### Testing CI/CD Detection Locally
Run the test script to verify CI/CD detection and profile removal:

```powershell
# Windows PowerShell
python test_cicd_detection.py
```

Expected output:
```
✓ CI/CD detected: True
✓ GITHUB_ACTIONS env: true
✓ CI env: true
✓ SUCCESS: aws_profile correctly removed from tfvars
```

### Switching from Access Keys to OIDC

**Step 1**: Create IAM OIDC Identity Provider in AWS
```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Step 2**: Create IAM Role with Trust Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:ref:refs/heads/main"
      }
    }
  }]
}
```

**Step 3**: Update GitHub Secrets
- Add `AWS_ROLE_ARN` with the IAM role ARN
- Remove `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (optional)

**Step 4**: Update Workflow Files
In both `terraform-deploy.yml` and `terraform-plan-pr.yml`:
- Comment out the access key configuration section
- Uncomment the OIDC configuration section

### Extending the Workflow

#### Add New Environments
1. Update `parameters.json` with new environment configuration:
```json
{
  "environments": {
    "staging": {
      "common": {...},
      "aws": {...},
      "azure": {...}
    }
  }
}
```

2. Update workflow input choices in `terraform-deploy.yml`:
```yaml
environment:
  type: choice
  options:
    - dev
    - prod
    - staging
```

#### Add New Cloud Providers
1. Add provider configuration to `provider.tf`
2. Create module directories: `<cloud>/network`, `<cloud>/compute`
3. Update `parameters.json` with cloud configuration
4. Add credential secrets to GitHub

#### Custom Modules
1. Create new module directory: `aws/database`
2. Add Terraform files: `main.tf`, `variables.tf`, `outputs.tf`
3. Update `parameters.json` with module configuration
4. Module is automatically available for deployment

---

## Support & Documentation

### Key Files
- **Orchestrator Script**: `orchestrator.py` - Main deployment logic and CI/CD detection
- **Terraform Modules**: 
  - `aws/compute/` - AWS EC2 instances
  - `aws/network/` - AWS VPC and networking
  - `azure/compute/` - Azure VMs
  - `azure/network/` - Azure VNet
  - `gcp/compute/` - GCP Compute Engine
  - `gcp/network/` - GCP VPC
- **Parameters**: `parameters.json` - Environment and cloud configurations
- **Workflows**: 
  - `.github/workflows/terraform-deploy.yml` - Manual deployment
  - `.github/workflows/terraform-plan-pr.yml` - PR validation
- **Provider Config**: `provider.tf` - Root provider configuration with CI/CD support
- **Test Script**: `test_cicd_detection.py` - Verify CI/CD detection

### Useful Commands

#### Local Testing
```powershell
# Test CI/CD detection
python test_cicd_detection.py

# Run orchestrator locally
python orchestrator.py -e dev -a plan -c aws -m compute

# Validate Terraform syntax
terraform validate

# Format Terraform files
terraform fmt -recursive
```

#### GitHub CLI Commands
```bash
# Trigger workflow manually
gh workflow run "Deploy Multi-Cloud Infrastructure" \
  -f environment=dev \
  -f action=plan \
  -f clouds=aws \
  -f modules=compute

# List workflow runs
gh run list --workflow=terraform-deploy.yml

# View workflow logs
gh run view <run-id> --log
```

### Quick Reference

#### Orchestrator CLI Options
```
-e, --environment    Environment (dev, prod, staging)
-a, --action        Action (plan, apply, destroy)
-p, --params-file   Parameters file (default: parameters.json)
-c, --clouds        Cloud providers (aws, azure, gcp)
-m, --modules       Modules (network, compute)
```

#### Environment Variables (CI/CD)
- `GITHUB_ACTIONS` - Set by GitHub Actions
- `CI` - Generic CI/CD indicator
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `AWS_SESSION_TOKEN` - Temporary credentials (OIDC)
- `AWS_REGION` - AWS region
- `ARM_CLIENT_ID` - Azure credentials
- `ARM_CLIENT_SECRET` - Azure credentials
- `ARM_SUBSCRIPTION_ID` - Azure subscription
- `ARM_TENANT_ID` - Azure tenant

---

## Changelog

### Version 2.0 (December 2025)
- ✅ Added automatic CI/CD detection
- ✅ Implemented AWS profile conditional logic
- ✅ Added Terraform cache cleaning step
- ✅ Enhanced error handling and debugging
- ✅ Improved authentication flow with environment variables
- ✅ Added Pull Request validation workflow
- ✅ Support for both access keys and OIDC authentication
- ✅ Added test script for CI/CD detection verification

### Version 1.0 (Initial Release)
- Initial multi-cloud orchestrator
- Manual deployment workflow
- Basic parameter configuration

---

**Last Updated**: December 5, 2025  
**Version**: 2.0  
**Maintainer**: DevOps Team
