"""
identity_center_exporter.py

Metadata:
- Author: Hideki.M (Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==)
- Version: 1.0.0+ts1.coldasyou
- Last Updated: 2024-07-24
- License: MIT

Description:
This script retrieves and exports information about AWS Identity Center.
It includes endpoints for Identity Center structure, and PermissionSets.

Usage:
    python identity_center_exporter.py --mgmt-account-id <management_account_id> --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--cache-expiry <cache_expiry>] [--access-token <valid_sso_access_token>]

"""

import boto3
import json
import argparse
import os
import time
import logging
from flask import Flask, jsonify
#from aws_utils.aws_utils import create_session # For Directory Structure
from aws_exporters.aws_utils import create_session

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

def get_users(identitystore_client, sso_admin_client, identity_store_id, instance_arn):
    paginator = identitystore_client.get_paginator('list_users')
    response_iterator = paginator.paginate(IdentityStoreId=identity_store_id)
    
    users = []
    for response in response_iterator:
        for user in response['Users']:
            user_details = identitystore_client.describe_user(IdentityStoreId=identity_store_id, UserId=user['UserId'])
            user_details['JoinedGroup'] = get_groups_for_user(identitystore_client, identity_store_id, user['UserId'])
            user_details['AccountAssignments'] = get_account_assignments(sso_admin_client, instance_arn, user['UserId'])
            user_details.pop('ResponseMetadata', None)
            users.append(user_details)
    if not users:
        users = [{'None': None}]
    return users

def get_groups_for_user(identitystore_client, identity_store_id, user_id):
    paginator = identitystore_client.get_paginator('list_group_memberships_for_member')
    response_iterator = paginator.paginate(IdentityStoreId=identity_store_id, MemberId={'UserId': user_id})
    
    groups = []
    for response in response_iterator:
        for group_membership in response['GroupMemberships']:
            group_id = group_membership['GroupId']
            group_details = identitystore_client.describe_group(IdentityStoreId=identity_store_id, GroupId=group_id)
            group_details.pop('ResponseMetadata', None)
            groups.append(group_details)
    if not groups:
        groups = [{'None': None}]
    return groups

def get_permission_set_details(sso_admin_client, instance_arn, permission_set_arn):
    response = sso_admin_client.describe_permission_set(InstanceArn=instance_arn, PermissionSetArn=permission_set_arn)
    permission_set = response['PermissionSet']
    permission_set.pop('ResponseMetadata', None)
    return permission_set

def get_account_assignments(sso_admin_client, instance_arn, user_id):
    paginator = sso_admin_client.get_paginator('list_account_assignments_for_principal')
    response_iterator = paginator.paginate(InstanceArn=instance_arn, PrincipalId=user_id, PrincipalType='USER')
    
    assignments = []
    for response in response_iterator:
        for assignment in response['AccountAssignments']:
            permission_set_details = get_permission_set_details(sso_admin_client, instance_arn, assignment['PermissionSetArn'])
            assignment['PermissionSet'] = permission_set_details
            assignments.append(assignment)
    if not assignments:
        assignments = [{'None': None}]
    return assignments

def get_all_permission_set_details(sso_admin_client, instance_arn, permission_set_arn):
    response = sso_admin_client.describe_permission_set(InstanceArn=instance_arn, PermissionSetArn=permission_set_arn)
    permission_set = response['PermissionSet']
    permission_set.pop('ResponseMetadata', None)

    # Attach managed policies
    managed_policies = sso_admin_client.list_managed_policies_in_permission_set(InstanceArn=instance_arn, PermissionSetArn=permission_set_arn)['AttachedManagedPolicies']
    if not managed_policies:
        permission_set['AttachedManagedPolicies'] = [{'None': None}]
    else:
        permission_set['AttachedManagedPolicies'] = managed_policies

    # Attach customer-managed policies
    customer_managed_policies = sso_admin_client.list_customer_managed_policy_references_in_permission_set(InstanceArn=instance_arn, PermissionSetArn=permission_set_arn)['CustomerManagedPolicyReferences']
    if not customer_managed_policies:
        permission_set['CustomerManagedPolicyReferences'] = [{'None': None}]
    else:
        permission_set['CustomerManagedPolicyReferences'] = customer_managed_policies

    # Get inline policy
    try:
        inline_policy = sso_admin_client.get_inline_policy_for_permission_set(InstanceArn=instance_arn, PermissionSetArn=permission_set_arn)['InlinePolicy']
    except sso_admin_client.exceptions.ResourceNotFoundException:
        inline_policy = ''
    if not inline_policy:
        permission_set['InlinePolicy'] = [{'None': None}]
    else:
        permission_set['InlinePolicy'] = inline_policy

    # Get permissions boundary
    try:
        permissions_boundary = sso_admin_client.get_permissions_boundary_for_permission_set(InstanceArn=instance_arn, PermissionSetArn=permission_set_arn)['PermissionsBoundary']
    except sso_admin_client.exceptions.ResourceNotFoundException:
        permissions_boundary = ''
    if not permissions_boundary:
        permission_set['PermissionsBoundary'] = [{'None': None}]
    else:
        permission_set['PermissionsBoundary'] = permissions_boundary

    return permission_set

# Main function to get identity center information
def get_identity_center_structure(mgmt_account_id, permission_set_name, sso_region):
    # Create Boto3 clients for the SSO Admin and Identity Store services
    sso_admin_client = create_session(mgmt_account_id, permission_set_name, sso_region, "sso-admin", valid_sso_access_token)
    identitystore_client = create_session(mgmt_account_id, permission_set_name, sso_region, "identitystore", valid_sso_access_token)
    
    if not sso_admin_client:
        return None

    instances = sso_admin_client.list_instances()['Instances']
    identity_center_structure = []
    for instance in instances:
        identity_store_id = instance['IdentityStoreId']
        instance['Users'] = get_users(identitystore_client, sso_admin_client, identity_store_id, instance['InstanceArn'])
        if not instance['Users']:
            instance['Users'] = [{'None': None}]
        identity_center_structure.append(instance)
    
    return {'identity_center': identity_center_structure}

def get_all_permission_sets(mgmt_account_id, permission_set_name, sso_region):
    # Create Boto3 clients for the SSO Admin service
    sso_admin_client = create_session(mgmt_account_id, permission_set_name, sso_region, "sso-admin", valid_sso_access_token)

    if not sso_admin_client:
        return None

    instance_arn = sso_admin_client.list_instances()['Instances'][0]['InstanceArn']
    paginator = sso_admin_client.get_paginator('list_permission_sets')
    response_iterator = paginator.paginate(InstanceArn=instance_arn)
    
    permission_sets = []
    for response in response_iterator:
        for permission_set_arn in response['PermissionSets']:
            permission_set_details = get_all_permission_set_details(sso_admin_client, instance_arn, permission_set_arn)
            permission_sets.append(permission_set_details)
    
    return {'PermissionSets': permission_sets}

@app.route('/identity-center', methods=['GET'])
def identity_center():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region
    current_time = time.time()

    # Check if the cached data is still valid (60 minutes)
    if 'identity_center' in cache and (current_time - cache_times['identity_center']) < cache_expiry:
        logger.info("↩️  Returning cached data to reduce API calls.")
        return jsonify(cache['identity_center'])

    # If not, get new data and update the cache
    identity_center_structure = get_identity_center_structure(mgmt_account_id, permission_set_name, sso_region)
    if identity_center_structure:
        cache['identity_center'] = identity_center_structure
        cache_times['identity_center'] = current_time
        return jsonify(identity_center_structure)
    else:
        return jsonify({"error": "Failed to retrieve identity center structure"}), 500

@app.route('/identity-center/permsets', methods=['GET'])
def permission_sets():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region
    current_time = time.time()

    # Check if the cached data is still valid (60 minutes)
    if 'permission_sets' in cache and (current_time - cache_times['permission_sets']) < cache_expiry:
        logger.info("↩️  Returning cached data to reduce API calls.")
        return jsonify(cache['permission_sets'])

    # If not, get new data and update the cache
    permission_sets = get_all_permission_sets(mgmt_account_id, permission_set_name, sso_region)
    if permission_sets:
        cache['permission_sets'] = permission_sets
        cache_times['permission_sets'] = current_time
        return jsonify(permission_sets)
    else:
        return jsonify({"error": "Failed to retrieve permission sets"}), 500

def main():
    global mgmt_account_id, permission_set_name, sso_region, cache_expiry, valid_sso_access_token

    parser = argparse.ArgumentParser(description="Retrieve AWS Identity Center structure and users.")
    parser.add_argument('--mgmt-account-id', type=str, required=True, help="Management account ID.")
    parser.add_argument('--permission-set-name', type=str, required=True, help="Name of the permission set to assume in the management account.")
    parser.add_argument('--sso-region', type=str, required=True, help="AWS SSO region.")
    parser.add_argument('--port', type=int, default=11121, help="Port to run the Flask app on.")
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
