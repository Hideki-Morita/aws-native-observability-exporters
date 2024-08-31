"""
multi_acc_iam_exporter.py

Metadata:
- Author: Hideki.M (Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==)
- Version: 1.0.0+ts1.coldasyou
- Last Updated: 2024-07-24
- License: MIT

Description:
This script retrieves and exports all account's information about AWS Identity and Access Management(IAM).
It includes endpoints for User, Group, Role, LocalManagedPolicy and AWSManagedPolicy.

Usage:
    python multi_acc_iam_exporter.py --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--cache-expiry <cache_expiry>] [--access-token <valid_sso_access_token>]

"""

import boto3
import json
import argparse
import os
import time
import logging
from flask import Flask, jsonify
#from aws_utils.aws_utils import create_session, get_all_account_ids_by_sso # For Directory Structure
from aws_exporters.aws_utils import create_session, get_all_account_ids_by_sso

### INIT CONFIGURATIONS ----------------------------------------
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

### GLOBAL VARIABLES -------------------------------------------
cache = {}
cache_times = {}
default_cache_expiry = 300  # 5 minutes
valid_sso_access_token = None

###-------------------------------------------------------------

app = Flask(__name__)

# Main function to get account auth details for an account
def get_account_auth_details_for_account(account_id, permission_set_name, sso_region, filter_type):
    # Create a Boto3 client for the IAM
    client = create_session(account_id, permission_set_name, sso_region, "iam", valid_sso_access_token)

    paginator = client.get_paginator('get_account_authorization_details')
    response_iterator = paginator.paginate(Filter=[filter_type])

    # Combining paginated responses
    auth_details = {}
    for response in response_iterator:
        for key in response:
            if key in auth_details:
                if isinstance(auth_details[key], list):
                    auth_details[key].extend(response[key])
                elif isinstance(auth_details[key], dict):
                    auth_details[key].update(response[key])
                else:
                    auth_details[key] = response[key]
            else:
                auth_details[key] = response[key]

    # Insert AccountID into each entry in RoleDetailList/UserDetailList/Policies/GroupDetailList
    for key in ['RoleDetailList', 'UserDetailList', 'Policies', 'GroupDetailList']:
        if key in auth_details and auth_details[key]:
            for entry in auth_details[key]:
                entry['AccountID'] = account_id

    return auth_details

@app.route('/multi-account-auth/<filter_type>', methods=['GET'])
def multiAccountAuth(filter_type):
    global cache, cache_times, permission_set_name, sso_region
    current_time = time.time()

    # Check if the cached data is still valid (5 minutes)
    if filter_type in cache and (current_time - cache_times[filter_type]) < cache_expiry:
        logger.info(f"↩️ Returning cached data for {filter_type} to reduce API calls.")
        return jsonify(cache[filter_type])

    # If not, get new data and update the cache
    logger.info("🔍 Retrieving account IDs from AWS Identity Center...")

    # Get all account IDs from 🔴AWS Identity Center
    account_ids = get_all_account_ids_by_sso(sso_region)
    logger.info(f"✅ Retrieved {len(account_ids)} accounts.")
    print(f'\n')
    all_auth_details = []

    for account_id in account_ids:
        try:
            logger.info("ℹ️  The target account is ... %s", account_id)
            auth_details = get_account_auth_details_for_account(account_id, permission_set_name, sso_region, filter_type)
            if auth_details:
                auth_details['AccountID'] = account_id
                all_auth_details.append(auth_details)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve details for account {account_id}: {e}")
            continue  # Skip to the next account

    if all_auth_details:
        cache[filter_type] = all_auth_details
        cache_times[filter_type] = current_time
        return jsonify(all_auth_details)
    else:
        return jsonify({"error": "Failed to retrieve account authorization details"}), 500

def main():
    global valid_sso_access_token
    global permission_set_name, sso_region, cache_expiry, valid_sso_access_token

    parser = argparse.ArgumentParser(description="Getting account's details within across multiple AWS accounts.")
    parser.add_argument('--permission-set-name', type=str, required=True, help="Name of the permission set to assume in each target account.")
    parser.add_argument('--sso-region', type=str, required=True, help="AWS SSO region.")
    parser.add_argument('--port', type=int, default=1989, help="Port to run the Flask app on.")
    parser.add_argument('--cache-expiry', type=int, default=default_cache_expiry, help="Cache expiry time in seconds.")
    parser.add_argument('--access-token', type=str, default=valid_sso_access_token, help="Valid access token.")
    args = parser.parse_args()

    permission_set_name = args.permission_set_name
    sso_region = args.sso_region
    cache_expiry = args.cache_expiry
    valid_sso_access_token = args.access_token

    app.run(host='0.0.0.0', port=args.port)

if __name__ == "__main__":
    main()
