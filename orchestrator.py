#!/usr/bin/env python3
"""
Multi-Cloud Terraform Orchestrator
Deploys infrastructure across AWS, Azure, and GCP using a single parameter file
"""

import subprocess
import os
import sys
import json
from pathlib import Path
import argparse

class MultiCloudOrchestrator:
    def __init__(self, params_file, env, action='plan', clouds=None, modules=None):
        self.params_file = params_file
        self.env = env
        self.action = action
        self.selected_clouds = clouds  # Filter specific clouds
        self.selected_modules = modules  # Filter specific modules
        self.params = self.load_parameters()
        self.results = {}
        
    def load_parameters(self):
        """Load parameters from JSON file"""
        with open(self.params_file, 'r') as f:
            data = json.load(f)
        
        if self.env not in data['environments']:
            raise ValueError(f"Environment {self.env} not found in parameters file")
        
        return data['environments'][self.env]
    
    def generate_tfvars(self, cloud, module, module_config):
        """Generate terraform.tfvars content for specific cloud and module"""
        common = self.params['common']
        cloud_params = self.params[cloud].copy()
        
        # Merge common and cloud-specific params
        tfvars = {**common, **cloud_params}
        
        # Remove metadata fields
        tfvars.pop('modules', None)
        tfvars.pop('enabled', None)
        
        # Add module-specific configuration
        if module_config:
            tfvars['module_config'] = module_config
        
        return tfvars
    
    def write_tfvars(self, cloud, module, tfvars):
        """Write tfvars to module directory"""
        module_path = Path(cloud) / module
        tfvars_file = module_path / 'terraform.tfvars.json'
        
        with open(tfvars_file, 'w') as f:
            json.dump(tfvars, f, indent=2)
        
        print(f"✓ Generated tfvars for {cloud}/{module}")
        return tfvars_file
    
    def write_backend_config(self, cloud, module):
        """Write backend configuration file for S3 remote state"""
        backend_config = self.params.get('backend', {})
        
        if not backend_config.get('enabled', False):
            return None
        
        module_path = Path(cloud) / module
        backend_file = module_path / 'backend.hcl'
        
        # Single state file per CSP: <cloud>/<environment>/terraform.tfstate
        state_key = f"{cloud}/{self.env}/terraform.tfstate"
        
        backend_hcl = {
            'bucket': backend_config['s3_bucket'],
            'key': state_key,
            'region': backend_config['s3_region'],
            'encrypt': backend_config.get('encrypt', True),
            'workspace_key_prefix': f"{cloud}/{self.env}"
        }
        
        # Add optional parameters if specified
        if 'dynamodb_table' in backend_config:
            backend_hcl['dynamodb_table'] = backend_config['dynamodb_table']
        
        if 'profile' in backend_config:
            backend_hcl['profile'] = backend_config['profile']
        
        if 'kms_key_id' in backend_config:
            backend_hcl['kms_key_id'] = backend_config['kms_key_id']
        
        # Write backend config in HCL format
        with open(backend_file, 'w') as f:
            for key, value in backend_hcl.items():
                if isinstance(value, bool):
                    f.write(f'{key} = {str(value).lower()}\n')
                else:
                    f.write(f'{key} = "{value}"\n')
        
        print(f"✓ Generated backend config for {cloud}/{module}")
        return backend_file
    
    def write_root_tfvars(self):
        """Write root-level terraform.tfvars.json for provider configuration"""
        common = self.params['common']
        root_tfvars_file = Path('terraform.tfvars.json')
        
        with open(root_tfvars_file, 'w') as f:
            json.dump(common, f, indent=2)
        
        print(f"✓ Generated root terraform.tfvars.json")
        return root_tfvars_file
    
    def run_terraform(self, cloud, module):
        """Execute terraform commands for a module"""
        module_path = Path(cloud) / module
        
        if not module_path.exists():
            print(f"⚠ Module path {module_path} does not exist, skipping...")
            return {'status': 'skipped', 'reason': 'path_not_found'}
        
        os.chdir(module_path)
        
        try:
            # Initialize with backend config if available
            print(f"\n{'='*60}")
            print(f"Initializing {cloud}/{module}...")
            print(f"{'='*60}")
            
            init_cmd = ['terraform', 'init']
            
            # Check if backend config exists
            backend_file = Path('backend.hcl')
            if backend_file.exists():
                init_cmd.extend(['-backend-config=backend.hcl'])
                print(f"  Using S3 backend configuration")
            
            subprocess.run(init_cmd, check=True)
            
            # Validate
            print(f"\nValidating {cloud}/{module}...")
            subprocess.run(['terraform', 'validate'], check=True)
            
            # Plan or Apply
            if self.action == 'plan':
                print(f"\nPlanning {cloud}/{module}...")
                result = subprocess.run(
                    ['terraform', 'plan', '-out=tfplan'],
                    check=True
                )
            elif self.action == 'apply':
                print(f"\nApplying {cloud}/{module}...")
                result = subprocess.run(
                    ['terraform', 'apply', '-auto-approve'],
                    check=True
                )
            elif self.action == 'destroy':
                print(f"\nDestroying {cloud}/{module}...")
                result = subprocess.run(
                    ['terraform', 'destroy', '-auto-approve'],
                    check=True
                )
            
            return {'status': 'success', 'cloud': cloud, 'module': module}
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error in {cloud}/{module}: {e}")
            return {'status': 'failed', 'cloud': cloud, 'module': module, 'error': str(e)}
        finally:
            os.chdir('../..')
    
    def orchestrate(self):
        """Main orchestration logic"""
        print(f"\n{'#'*60}")
        print(f"Multi-Cloud Deployment Orchestrator")
        print(f"Environment: {self.env}")
        print(f"Action: {self.action}")
        if self.selected_clouds:
            print(f"Clouds: {', '.join(self.selected_clouds)}")
        if self.selected_modules:
            print(f"Modules: {', '.join(self.selected_modules)}")
        print(f"{'#'*60}\n")
        
        clouds = ['aws', 'azure', 'gcp']
        
        for cloud in clouds:
            # Skip if cloud not selected
            if self.selected_clouds and cloud not in self.selected_clouds:
                print(f"⊗ {cloud.upper()} not selected, skipping...")
                continue
                
            if cloud not in self.params:
                print(f"⚠ {cloud.upper()} configuration not found, skipping...")
                continue
            
            cloud_config = self.params[cloud]
            
            if not cloud_config.get('enabled', True):
                print(f"⚠ {cloud.upper()} is disabled, skipping...")
                continue
            
            modules = cloud_config.get('modules', {})
            if isinstance(modules, list):
                # Old format support
                modules = {m: {} for m in modules}
                
            print(f"\n{'='*60}")
            print(f"Processing {cloud.upper()} - {len(modules)} module(s)")
            print(f"{'='*60}")
            
            for module, module_config in modules.items():
                # Skip if module not selected
                if self.selected_modules and module not in self.selected_modules:
                    print(f"⊗ Module '{module}' not selected, skipping...")
                    continue
                    
                print(f"\n→ Processing module: {module}")
                
                # Generate and write tfvars
                tfvars = self.generate_tfvars(cloud, module, module_config)
                self.write_tfvars(cloud, module, tfvars)
                
                # Generate backend configuration
                self.write_backend_config(cloud, module)
                
                # Run terraform
                result = self.run_terraform(cloud, module)
                
                key = f"{cloud}/{module}"
                self.results[key] = result
        
        self.print_summary()
    
    def print_summary(self):
        """Print deployment summary"""
        print(f"\n{'#'*60}")
        print("Deployment Summary")
        print(f"{'#'*60}\n")
        
        success_count = sum(1 for r in self.results.values() if r['status'] == 'success')
        failed_count = sum(1 for r in self.results.values() if r['status'] == 'failed')
        skipped_count = sum(1 for r in self.results.values() if r['status'] == 'skipped')
        
        print(f"Total modules processed: {len(self.results)}")
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {failed_count}")
        print(f"⊗ Skipped: {skipped_count}\n")
        
        if failed_count > 0:
            print("Failed modules:")
            for key, result in self.results.items():
                if result['status'] == 'failed':
                    print(f"  ✗ {key}: {result.get('error', 'Unknown error')}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Multi-Cloud Terraform Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy only AWS in dev environment
  python orchestrator.py -e dev -c aws -a apply
  
  # Deploy AWS and Azure, only network module
  python orchestrator.py -e dev -c aws azure -m network -a plan
  
  # Deploy all clouds, only compute module
  python orchestrator.py -e prod -m compute -a apply
  
  # Deploy specific cloud and module
  python orchestrator.py -e dev -c gcp -m network compute -a plan
        """
    )
    parser.add_argument(
        '-e', '--environment',
        required=True,
        help='Environment to deploy (dev, prod, etc.)'
    )
    parser.add_argument(
        '-a', '--action',
        choices=['plan', 'apply', 'destroy'],
        default='plan',
        help='Terraform action to perform (default: plan)'
    )
    parser.add_argument(
        '-p', '--params-file',
        default='parameters.json',
        help='Path to parameters file (default: parameters.json)'
    )
    parser.add_argument(
        '-c', '--clouds',
        nargs='+',
        choices=['aws', 'azure', 'gcp'],
        help='Specific cloud(s) to deploy (e.g., -c aws azure). If not specified, deploys to all enabled clouds.'
    )
    parser.add_argument(
        '-m', '--modules',
        nargs='+',
        help='Specific module(s) to deploy (e.g., -m network compute). If not specified, deploys all modules.'
    )
    
    args = parser.parse_args()
    
    orchestrator = MultiCloudOrchestrator(
        params_file=args.params_file,
        env=args.environment,
        action=args.action,
        clouds=args.clouds,
        modules=args.modules
    )
    
    orchestrator.orchestrate()

if __name__ == '__main__':
    main()