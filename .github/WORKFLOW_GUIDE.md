# GitHub Actions Workflow Guide

## Overview

This GitHub Actions workflow provides a user-friendly interface to trigger the Terraform Multi-Cloud Orchestrator with all available options. Users can configure deployments at runtime without modifying any code.

## Triggering the Workflow

1. Go to your GitHub repository
2. Click on the **Actions** tab
3. Select **Terraform Multi-Cloud Deployment**
4. Click **Run workflow**
5. Fill in the required and optional parameters
6. Click **Run workflow** button

## Available Parameters

### Required Parameters

#### **Environment** ⚠️
- **Description**: The environment to deploy to
- **Type**: Dropdown/Choice
- **Available Options**: 
  - `dev` - Development environment
  - `prod` - Production environment
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
- **Default**: Empty (deploys to all enabled clouds per environment)
- **Format**: Comma or space-separated values
- **Examples**:
  - `aws` - Deploy to AWS only
  - `aws,azure` - Deploy to AWS and Azure
  - `aws azure gcp` - Deploy to all three clouds
- **Use Case**: When you only want to update infrastructure in specific cloud providers

#### **Modules**
- **Description**: Specific module(s) to deploy
- **Type**: Text input (comma-separated)
- **Available Modules**: `network`, `compute`
- **Default**: Empty (deploys all modules)
- **Format**: Comma or space-separated values
- **Examples**:
  - `network` - Deploy only network infrastructure
  - `compute` - Deploy only compute resources
  - `network,compute` - Deploy both modules
- **Use Case**: When you need to update only specific infrastructure components

#### **Skip Validation** 🔧
- **Description**: Skip the terraform validation step
- **Type**: Boolean (checkbox)
- **Default**: `false` (validation is enabled)
- **Use Case**: 
  - When you've already validated and want faster execution
  - For troubleshooting purposes
  - Not recommended for production

#### **Dry Run Mode** 🔒
- **Description**: Dry run mode forces plan-only execution
- **Type**: Boolean (checkbox)
- **Default**: `false`
- **Behavior**: 
  - When enabled, it converts `apply` or `destroy` actions to `plan`
  - Shows what would happen without making actual changes
  - Safe way to test changes before applying
- **Use Case**:
  - Testing complex changes in production environment
  - Getting approval before actual deployment
  - Verifying changes won't break anything

## Common Workflows

### 1. Preview Changes (Safest Option)
```
Environment: dev
Action: plan
Clouds: (leave empty)
Modules: (leave empty)
Dry Run: false
```
**What it does**: Shows all changes that would happen across all clouds and modules in dev environment

### 2. Deploy Network to AWS Only
```
Environment: prod
Action: plan
Clouds: aws
Modules: network
Dry Run: false
```
**What it does**: Plans network infrastructure changes for AWS in prod environment

### 3. Dry Run Destruction
```
Environment: dev
Action: destroy
Clouds: gcp
Modules: compute
Dry Run: true
```
**What it does**: Shows what would be destroyed without actually destroying (safe to test)

### 4. Multi-Cloud Network Update
```
Environment: prod
Action: apply
Clouds: aws,azure
Modules: network
Dry Run: false
```
**What it does**: Applies network infrastructure changes to AWS and Azure in production

### 5. Destroy Dev Environment
```
Environment: dev
Action: destroy
Clouds: (leave empty)
Modules: (leave empty)
Dry Run: false
```
**What it does**: Completely destroys all infrastructure in dev environment

### 6. Update Only Compute Resources
```
Environment: prod
Action: apply
Clouds: (leave empty)
Modules: compute
Dry Run: false
```
**What it does**: Updates compute resources across all enabled clouds

## Workflow Execution Steps

1. **Checkout Code** - Fetches the latest code from your repository
2. **Setup Python** - Installs Python 3.11
3. **Setup Terraform** - Installs latest Terraform version
4. **Configure Cloud Credentials**:
   - AWS credentials from secrets
   - Azure credentials from environment variables
   - GCP credentials from service account key
5. **Parse Inputs** - Normalizes and validates input parameters
6. **Validate Parameters** - Checks environment and cloud configurations
7. **Run Terraform Orchestrator** - Executes the deployment command
8. **Generate Summary** - Creates a summary in GitHub Actions

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

To add new environments, update `parameters.json` and commit the changes.

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
- ✅ Use dry run mode to test destructive operations
- ✅ Specify clouds and modules when updating specific resources
- ✅ Review the workflow summary before confirming changes
- ✅ Use version tags when deploying to production

### ❌ Don'ts
- ❌ Don't run `destroy` in production without planning first
- ❌ Don't skip validation in production environments
- ❌ Don't use dry run mode when you need actual changes
- ❌ Don't specify invalid cloud or module names

## Troubleshooting

### Workflow Failed with "Environment Not Found"
- Check that the environment name matches exactly with entries in `parameters.json`
- Ensure the environment is properly configured

### "Cloud not configured for this environment"
- Verify the cloud provider is enabled in `parameters.json` for the selected environment
- Check that credentials are set correctly in GitHub secrets

### Terraform Validation Errors
- Ensure all `.tf` files in module directories are syntactically correct
- Check that variable names and types match across files
- Verify `provider.tf` is correctly configured

### Credentials Issues
- Verify all required secrets are set in the repository
- Check that credentials have appropriate IAM/permissions
- Ensure service account keys are not expired

## Viewing Results

1. Go to **Actions** tab in your GitHub repository
2. Click on the completed workflow run
3. View step-by-step logs in the workflow details
4. Check the **Summary** for deployment status
5. Review any errors or warnings in the logs

## Advanced Usage

### Extending the Workflow

To add new environments:
1. Update `parameters.json` with new environment configuration
2. The workflow automatically supports new environments

To add new input parameters:
1. Edit `.github/workflows/terraform-deploy.yml`
2. Add new `inputs` section under `workflow_dispatch`
3. Update the orchestrator command building logic

### Integration with Pull Requests

To add workflow approval on PRs:
```yaml
on:
  pull_request:
    types: [labeled]
    
jobs:
  requires-label: 
    if: contains(github.event.pull_request.labels.*.name, 'terraform:review')
```

## Support & Documentation

- **Orchestrator Script**: See `orchestrator.py` for implementation details
- **Terraform Modules**: Check individual `main.tf` files in cloud provider directories
- **Parameters**: Review `parameters.json` for available configurations

---

**Last Updated**: December 2025
**Version**: 1.0
