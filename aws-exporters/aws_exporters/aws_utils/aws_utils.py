"""
aws_utils.py

Metadata:

- Author: Hideki.M (Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==)
- Version: 1.0.0+ts1.coldasyou
- Last Updated: 2024-07-24
- License: MIT

AWS Utilities for SSO and Organizations Management.

This module provides functions to manage and retrieve information 
from AWS Single Sign-On (SSO) and AWS Organizations services. 

Functions included:
- get_sso_access_token: Retrieves the latest SSO access token.
- get_temporary_credentials: Retrieves temporary credentials using AWS SSO.
- get_all_account_ids_by_sso: Retrieves all account IDs using AWS SSO.
- get_all_account_ids: Retrieves all account IDs using AWS Organizations.
"""

import boto3
import json
import os
import logging
import pytz
from botocore.exceptions import ClientError
from datetime import datetime, timezone, timedelta

### INIT CONFIGURATIONS ----------------------------------------
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

### GLOBAL VARIABLES -------------------------------------------
cache_times = {}

###-------------------------------------------------------------

# Function to get the latest 🔴SSO access token
def get_sso_access_token():
    # Determine the config directory from the AWS_CONFIG_FILE environment variable or default to ~/.aws/config
    aws_config_file = os.getenv('AWS_CONFIG_FILE', os.path.expanduser('~/.aws/config'))
    config_directory = os.path.dirname(aws_config_file)
    cache_directory = os.path.join(config_directory, 'sso/cache/')

    try:
        # Check if the cache directory exists
        if not os.path.exists(cache_directory):
            logger.error(f"❌ Cache directory {cache_directory} does not exist.")
            return None
        
        # Find the latest token file
        token_files = [os.path.join(cache_directory, f) for f in os.listdir(cache_directory) if f.endswith('.json')]
        if not token_files:
            logger.error("❌ No token files found in the cache directory.")
            return None

        latest_token_file = sorted(token_files, key=os.path.getmtime, reverse=True)[0]

        # Read the token file
        with open(latest_token_file, 'r') as f:
            token_data = json.load(f)

        # Check if the accessToken key exists in the JSON data
        if 'accessToken' not in token_data:
            logger.error("❌ 'accessToken' not found in the token data.")
            return None

        access_token = token_data['accessToken']
        expires_at = datetime.fromisoformat(token_data['expiresAt'].replace('Z', '+00:00'))
        #refresh_token = token_data['refreshToken']

        local_tz = pytz.timezone("Asia/Tokyo")
        local_expires_at = expires_at.astimezone(local_tz)
        logger.info(f"🔔 The access token will be expired at {local_expires_at}")
        return access_token, expires_at

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error decoding JSON from the token file: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        return None

# Function to check if the token is expired
def is_token_expired(expires_at):
    current_time = datetime.now(timezone.utc)
    if not expires_at:
        if not cache_times:
            expires_at = current_time + timedelta(hours=1)
        else:
            expires_at = cache_times

    return current_time >= expires_at

# Function to get permission set credentials using 🔴AWS Identity Center
def get_temporary_credentials(account_id, permission_set_name, sso_region, sso_access_token=None):
    if not sso_access_token:
        sso_access_token, expires_at = get_sso_access_token()
        if is_token_expired(expires_at):
            logger.error("❌ The SSO access token is expired.")
            return None

    sso_client = boto3.client('sso', region_name=sso_region)
    try:
        response = sso_client.get_role_credentials(
            accountId=account_id,
            roleName=permission_set_name,
            accessToken=sso_access_token
        )
        return response['roleCredentials']
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedException':
            logger.error(f"❌ Unauthorized: {e}")
        elif error_code == 'InvalidRequestException':
            logger.error(f"❌ Invalid request: {e}")
        elif error_code == 'ResourceNotFoundException':
            logger.error(f"❌ Resource not found: {e}")
        elif error_code == 'TooManyRequestsException':
            logger.error(f"❌ Too many requests: {e}")
        else:
            logger.error(f"❌ An unexpected error occurred: {e}")
        return None
    finally:
        del sso_access_token

def create_session(account_id, permission_set_name, sso_region, service_name, valid_sso_access_token=None):
    """
    Creates a session using 🔴SSO credentials and returns a client for the specified service.
    
    Parameters:
    - account_id (str): Account ID.
    - permission_set_name (str): Name of the permission set.
    - sso_region (str): AWS SSO region.
    - service_name (str): AWS service name to create a client for.
    - valid_sso_access_token (str, optional): Pre-existing SSO access token, if available.
    
    Returns:
    - boto3.client: A boto3 client for the specified service, or None if the session could not be created.
    """
    try:
        # Get the latest 🔴SSO access token
        if not valid_sso_access_token:
            sso_access_token, expires_at = get_sso_access_token()
        else:
            sso_access_token = valid_sso_access_token

        # Check if the token is expired
        if is_token_expired(expires_at):
            logger.error("❌ The access token is expired. 🥲")
            return None

        # Get permission set credentials using 🔴AWS Identity Center
        credentials = get_temporary_credentials(account_id, permission_set_name, sso_region, sso_access_token)
        if not valid_sso_access_token:
            del sso_access_token

        # Create a new session using the role credentials    
        if not credentials:
            raise ValueError("❌ Failed to retrieve temporary credentials.")

        session = boto3.Session(
            aws_access_key_id=credentials['accessKeyId'],
            aws_secret_access_key=credentials['secretAccessKey'],
            aws_session_token=credentials['sessionToken']
        )
        del credentials
        return session.client(service_name)
    except Exception as e:
        logger.error(f"❌ Failed to create session (the 🔴SSO access token might be expired.): \n{e}")
        return None

# Function to get all account IDs from 🔴AWS Identity Center
def get_all_account_ids_by_sso(sso_region):
    account_ids = []
    
    sso_access_token, expires_at = get_sso_access_token()
    if is_token_expired(expires_at):
        logger.error("❌ The SSO access token is expired.")
        return account_ids

    try:
        sso_client = boto3.client('sso', region_name=sso_region)
        
        if not sso_client:
            logger.error(f"❌ Failed to create session (Your 🔴SSO access token might be expired.)")
        else:
            response = sso_client.list_accounts(accessToken=sso_access_token)
            accounts = response['accountList']
            
            for account in accounts:
                account_ids.append(account['accountId'])

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedException':
            logger.error(f"❌ Unauthorized: {e}")
        elif error_code == 'InvalidRequestException':
            logger.error(f"❌ Invalid request: {e}")
        elif error_code == 'ResourceNotFoundException':
            logger.error(f"❌ Resource not found: {e}")
        elif error_code == 'TooManyRequestsException':
            logger.error(f"❌ Too many requests: {e}")
        else:
            logger.error(f"❌ An unexpected error occurred: \n{e}")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: \n{e}")
    finally:
        del sso_access_token

    return account_ids
    
# Function to get all account IDs from 🔴AWS Organizations
def get_all_account_ids():
    try:
        client = boto3.client('organizations')
        paginator = client.get_paginator('list_accounts')
        account_ids = []

        for page in paginator.paginate():
            for account in page['Accounts']:
                account_ids.append(account['Id'])
        return account_ids

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            logger.error(f"❌ Access denied: {e}")
        else:
            logger.error(f"❌ An unexpected error occurred: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        raise
