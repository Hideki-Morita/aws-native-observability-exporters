"""
freetier_usage_exporter.py

Metadata:
- Author: Hideki.M (Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==)
- Version: 1.0.0+ts1.coldasyou
- Last Updated: 2024-07-24
- License: MIT

Description:
This script retrieves and exports information about AWS Free Tier, it's part of AWS Billing and Cost Management.

Usage:
    python freetier_usage_exporter.py --mgmt-account-id <management_account_id> --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--cache-expiry <cache_expiry>] [--access-token <valid_sso_access_token>]

"""

import boto3
import json
import argparse
import os
import time
import logging
from flask import Flask, jsonify, request
from datetime import datetime, timezone
from botocore.exceptions import ClientError
#from aws_utils.aws_utils import create_session # For Directory Structure
from aws_exporters.aws_utils import create_session

### INIT CONFIGURATIONS ----------------------------------------
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
#logger.info("🚨 logger: %s", logger)

### GLOBAL VARIABLES -------------------------------------------
cache = {}
cache_times = {}
default_cache_expiry = 1800  # 30 minutes
valid_sso_access_token = None

###-------------------------------------------------------------

app = Flask(__name__)

# Function to get cost and usage data from AWS Cost Explorer
def get_cost_and_usage(usage_types, time_periods=None, mgmt_account_id=None, permission_set_name=None, sso_region=None, valid_sso_access_token=None):

    # Create a Boto3 client for the FreeTier
    client = create_session(mgmt_account_id, permission_set_name, sso_region, "ce", valid_sso_access_token)

    if not client:
        return None

    if not time_periods:
        today = datetime.now(timezone.utc).date()
        first_day_of_month = today.replace(day=1)
        start_date = first_day_of_month.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    else:
        time_period_list = [time_period.strip() for time_period in time_periods.split(',')]
        start_date = time_period_list[0]
        end_date = time_period_list[1]

    usage_types_list = [usage_type.strip() for usage_type in usage_types.split(',')]

    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UsageQuantity'],
            Filter={
                'Dimensions': {
                    'Key': 'USAGE_TYPE',
                    'Values': usage_types_list
                }
            }
        )

        results_by_time = response['ResultsByTime']
        usage_data = []

        for result in results_by_time:
            time_period = result['TimePeriod']
            amount = result['Total']['UsageQuantity']['Amount']
            usage_data.append({
                'Start': time_period['Start'],
                'End': time_period['End'],
                'UsageAmount': amount
            })

        total_usage = sum(float(result['Total']['UsageQuantity']['Amount']) for result in results_by_time)
        return {
            'UsageData': usage_data,
            'TotalUsage': total_usage
        }
    except ClientError as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        return None

# Main function to get free_tier_usage from Mmgt. account
def get_free_tier_usage(mgmt_account_id, permission_set_name, sso_region):
    # Create a Boto3 client for the FreeTier
    client = create_session(mgmt_account_id, permission_set_name, sso_region, "freetier", valid_sso_access_token)

    if not client:
        return None

    # Initialize variables for pagination    
    free_tier_usage = []
    next_token = None

    try:
        while True:
            if next_token:
                response = client.get_free_tier_usage(nextToken=next_token)
            else:
                response = client.get_free_tier_usage()

            if 'freeTierUsages' in response:
                # Append the current response's data to free_tier_usage
                free_tier_usage.extend(response['freeTierUsages'])
            else:
                logger.error("❌ 'freeTierUsages' not found in the response.")
                break
            
            next_token = response.get('nextToken')
            if not next_token:
                break

        return {'freeTierUsages': free_tier_usage}
    except ClientError as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        return None

@app.route('/freetier', methods=['GET'])
def freetier():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region
    current_time = time.time()

    # Check if the cached data is still valid (30 minutes)
    if 'freetier' in cache and (current_time - cache_times['freetier']) < cache_expiry:
        logger.info("↩️ Returning cached data to reduce API calls.")
        return jsonify(cache['freetier'])

    # If not, get new data and update the cache
    usage = get_free_tier_usage(mgmt_account_id, permission_set_name, sso_region)
    if usage:
        cache['freetier'] = usage
        cache_times['freetier'] = current_time
        return jsonify(usage)
    else:
        return jsonify({"error": "Failed to retrieve free tier usage"}), 500

@app.route('/freetier/cost-explorer', methods=['GET'])
def cost_explorer():
    global cache, cache_times, mgmt_account_id, permission_set_name, sso_region
    current_time = time.time()

    # Get the necessary parameter
    usage_types = request.args.get('usage_types')
    if not usage_types:
        return jsonify({"error": "Missing usage_types parameter"}), 400

    # Get the optional parameter
    time_periods = request.args.get('time_periods')

    # Check if the cached data is still valid (30 minutes)
    if 'cost_explorer' in cache and (current_time - cache_times['cost_explorer']) < cache_expiry:
        logger.info("↩️  Returning cached data to reduce API calls.")
        return jsonify(cache['cost_explorer'])

    # If not, get new data and update the cache
    cost_data = get_cost_and_usage(usage_types, time_periods, mgmt_account_id, permission_set_name, sso_region, valid_sso_access_token)
    if cost_data:
        cache['cost_explorer'] = cost_data
        cache_times['cost_explorer'] = current_time
        return jsonify(cost_data)
    else:
        return jsonify({"error": "Failed to retrieve cost explorer usage"}), 500

def main():
    global mgmt_account_id, permission_set_name, sso_region, cache_expiry, valid_sso_access_token

    parser = argparse.ArgumentParser(description="Retrieve free tier & cost explorer usage details from the management account.")
    parser.add_argument('--mgmt-account-id', type=str, required=True, help="Management account ID.")
    parser.add_argument('--permission-set-name', type=str, required=True, help="Name of the permission set to assume in the management account.")
    parser.add_argument('--sso-region', type=str, required=True, help="AWS SSO region.")
    parser.add_argument('--port', type=int, default=4921, help="Port to run the Flask app on.")
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
