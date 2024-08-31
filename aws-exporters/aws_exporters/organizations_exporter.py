"""
organizations_exporter.py

Metadata:
- Author: Hideki.M (Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==)
- Version: 1.0.0+ts1.coldasyou
- Last Updated: 2024-07-24
- License: MIT

Description:
This script retrieves and exports information about AWS Organizations and Identity Center.
It includes endpoints for organization structure, policies, and access reports.

Usage:
    python organizations_exporter.py --mgmt-account-id <management_account_id> --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--cache-expiry <cache_expiry>] [--access-token <valid_sso_access_token>]

"""

import boto3
import json
import argparse
import os
import time
import logging
from flask import Flask, jsonify, request
#from aws_utils.aws_utils import create_session # For Directory Structure
from aws_exporters.aws_utils import create_session
from datetime import datetime

### INIT CONFIGURATIONS ----------------------------------------
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

### GLOBAL VARIABLES -------------------------------------------
cache = {}
cache_times = {}
default_cache_expiry = 3600  # 60 minutes
valid_sso_access_token = None

###-------------------------------------------------------------

app = Flask(__name__)

def get_accounts_for_parent(org_client, parent_id):
    paginator = org_client.get_paginator('list_accounts_for_parent')
    response_iterator = paginator.paginate(ParentId=parent_id)
    
    accounts = []
    for response in response_iterator:
        for account in response['Accounts']:
            # Convert datetime objects to strings
            if 'JoinedTimestamp' in account:
                account['JoinedTimestamp'] = account['JoinedTimestamp'].isoformat()
            accounts.append(account)
    if not accounts:
        accounts = [{'None': None}]
    return accounts

def get_organizational_units(org_client, parent_id):
    paginator = org_client.get_paginator('list_organizational_units_for_parent')
    response_iterator = paginator.paginate(ParentId=parent_id)
    
    ous = []
    for response in response_iterator:
        for ou in response['OrganizationalUnits']:
            ou['OrganizationalUnits'] = get_organizational_units(org_client, ou['Id'])
            ou['Accounts'] = get_accounts_for_parent(org_client, ou['Id'])
            if not ou['OrganizationalUnits']:
                ou['OrganizationalUnits'] = [{'None': None}]
            if not ou['Accounts']:
                ou['Accounts'] = [{'None': None}]
            ous.append(ou)
    return ous

def get_policies(org_client, policy_type):
    paginator = org_client.get_paginator('list_policies')
    response_iterator = paginator.paginate(Filter=policy_type)
    
    policies = []
    for response in response_iterator:
        for policy in response['Policies']:
            policy_details = org_client.describe_policy(PolicyId=policy['Id'])['Policy']
            policy_targets = org_client.list_targets_for_policy(PolicyId=policy['Id'])['Targets']
            policy_details['Targets'] = policy_targets
            policies.append(policy_details)
    
    return policies

def generate_organizations_access_report(iam_client, org_client):
    try:
        response = org_client.describe_organization()
        org_id = response['Organization']['Id']
        response = org_client.list_roots()
        org_root_id = response['Roots'][0]['Id']
        response = iam_client.generate_organizations_access_report(EntityPath=f"{org_id}/{org_root_id}")
        job_id = response['JobId']
        logger.info(f"🔍 The EntityPath is like this: {org_id}/{org_root_id}")
        logger.info(f"🔍 Access report job started: {job_id}")

        # Wait for report to be completed
        while True:
            time.sleep(3)
            report_details = iam_client.get_organizations_access_report(JobId=job_id)
            if report_details['JobStatus'] == 'COMPLETED':
                logger.info(f"✅ Access report job completed: {job_id}")
                break
            elif report_details['JobStatus'] == 'FAILED':
                logger.error(f"❌ Access report job failed: {job_id}")
                return None

        return report_details
    except Exception as e:
        logger.error(f"❌ Failed to generate access report: {e}")
        return None

# Main function to get organization information
def get_org_structure(mgmt_account_id, permission_set_name, sso_region):
    # Create a Boto3 client for the Organizations service
    org_client = create_session(mgmt_account_id, permission_set_name, sso_region, "organizations", valid_sso_access_token)

    if not org_client:
        return None
    
    roots = org_client.list_roots()['Roots']
    org_structure = []
    for root in roots:
        root['OrganizationalUnits'] = get_organizational_units(org_client, root['Id'])
        root['Accounts'] = get_accounts_for_parent(org_client, root['Id'])
        if not root['OrganizationalUnits']:
            root['OrganizationalUnits'] = [{'None': None}]
        if not root['Accounts']:
            root['Accounts'] = [{'None': None}]
        org_structure.append(root)
    
    return {'organizations': org_structure}

@app.route('/organization', methods=['GET'])
def organization():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region, cache_expiry
    current_time = time.time()

    # Check if the cached data is still valid (60 minutes)
    if 'organization' in cache and (current_time - cache_times['organization']) < cache_expiry:
        logger.info("↩️  Returning cached data to reduce API calls.")
        return jsonify(cache['organization'])

    # If not, get new data and update the cache
    organization_structure = get_org_structure(mgmt_account_id, permission_set_name, sso_region)
    if organization_structure:
        cache['organization'] = organization_structure
        cache_times['organization'] = current_time
        return jsonify(organization_structure)
    else:
        return jsonify({"error": "Failed to retrieve organization structure"}), 500

@app.route('/organization/policies', methods=['GET'])
def organization_policies():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region, cache_expiry
    current_time = time.time()

    # Check if the cached data is still valid (60 minutes)
    if 'policies' in cache and (current_time - cache_times['policies']) < cache_expiry:
        logger.info("↩️  Returning cached data to reduce API calls.")
        return jsonify(cache['policies'])

    # If not, get new data and update the cache
    # Create a Boto3 client for the Organizations service
    org_client = create_session(mgmt_account_id, permission_set_name, sso_region, "organizations", valid_sso_access_token)

    if not org_client:
        return None

    scp_policies = get_policies(org_client, 'SERVICE_CONTROL_POLICY')
    tag_policies = get_policies(org_client, 'TAG_POLICY')
    policies = {
        'ServiceControlPolicies': scp_policies,
        'TagPolicies': tag_policies
    }
    if policies:
        cache['policies'] = policies
        cache_times['policies'] = current_time
        return jsonify(policies)
    else:
        return jsonify({"error": "Failed to retrieve organization structure"}), 500

@app.route('/organization/access-report', methods=['GET'])
def access_report():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region, cache_expiry
    current_time = time.time()

    # Check if the cached data is still valid (60 minutes)
    if 'access_report' in cache and (current_time - cache_times['access_report']) < cache_expiry:
        logger.info("↩️  Returning cached data to reduce API calls.")
        return jsonify(cache['access_report'])

    # If not, get new data and update the cache
    # Create a Boto3 client for the Organizations and IAM service
    org_client = create_session(mgmt_account_id, permission_set_name, sso_region, "organizations", valid_sso_access_token)
    iam_client = create_session(mgmt_account_id, permission_set_name, sso_region, "iam", valid_sso_access_token)

    if not org_client:
        return None

    access_report = generate_organizations_access_report(iam_client, org_client)
    if access_report:
        cache['access_report'] = access_report
        cache_times['access_report'] = current_time
        return jsonify(access_report)
    else:
        return jsonify({"error": "Failed to retrieve access report"}), 500

def main():
    global mgmt_account_id, permission_set_name, sso_region, cache_expiry, valid_sso_access_token

    parser = argparse.ArgumentParser(description="Retrieve AWS Organizations structure, policies and Organizations Access Report.")
    parser.add_argument('--mgmt-account-id', type=str, required=True, help="Management account ID.")
    parser.add_argument('--permission-set-name', type=str, required=True, help="Name of the permission set to assume in the management account.")
    parser.add_argument('--sso-region', type=str, required=True, help="AWS SSO region.")
    parser.add_argument('--port', type=int, default=7723, help="Port to run the Flask app on.")
    parser.add_argument('--cache-expiry', type=int, default=default_cache_expiry, help="Cache expiry time in seconds.")
    parser.add_argument('--access-token', type=str, default=valid_sso_access_token, help="Valid access token.")
    args = parser.parse_args()

    mgmt_account_id = args.mgmt_account_id
    permission_set_name = args.permission_set_name
    sso_region = args.sso_region
    cache_expiry = args.cache_expiry
    valid_sso_access_token = args.access_token

    app.run(host='0.0.0.0', port=args.port)

if __name__ == "__main__":
    main()
