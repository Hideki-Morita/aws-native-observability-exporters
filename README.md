# AWS Native Observability Exporters

<br>

![License](https://img.shields.io/badge/License-MIT-green) ![AWS](https://img.shields.io/badge/AWS-AWS_Native-orange) ![AWS](https://img.shields.io/badge/AWS-Tools-orange) ![Python](https://img.shields.io/badge/Python-3.12%2B-blue) ![#AWSAlwaysFreeChallenge](https://img.shields.io/badge/AWS-AlwaysFreeChallenge-orange)

A collection of tools for exporting various AWS data from a complex AWS environment adopting a multi-account strategy.  
Those are part of our [<mark>**AWS Native Cross-account Observability Dashboard**</mark>](https://github.com/Hideki-Morita/aws-native-observability-dashboard) as The data sources of it.

---

<br>

## 🪩 Features

<br>

|✅Features||
|---|---|
|🔴**AWS Organizations Exporter:**     |Retrieve and export your AWS Organizations structure and policies.|
|🔴**AWS Identity Center Exporter:**   |Retrieve and export user, group, permisionSets, relationship with AWS accounts information from AWS Identity Center.|
|🔴**AWS Multi-Account IAM Exporter:** |Export IAM details(Role, Custom-Policies, Boundaries...) across **multiple AWS accounts**.|
|🟢**AWS Free Tier Usage Exporter:**   |Export Free Tier usage. (Including one of the mysterious chargeable items `Global-DataScanned-Bytes` too.) |

---

<br>

### ☻ Project Phases

<br>

| Phase | Description |
|---|---|
| **Phase 1**<br> (Here) | <mark>Local Development</mark>: The initial phase where the project is run and tested locally. |
| **Phase 2** | <mark>Containerization</mark>: Transform the project into a containerized application for easier deployment and scalability. |
| **Phase 3** | <mark>Production Ready</mark>: Finalize the project for deployment in a production environment, ensuring stability, security, and performance. |

---

<br>

## 🪩 Table of Contents

- [AWS Native Observability Exporters](#aws-native-observability-exporters)
  - [🪩 Features](#-features)
    - [☻ Project Phases](#-project-phases)
  - [🪩 Table of Contents](#-table-of-contents)
  - [🪩 Installation](#-installation)
    - [☻ Requirements](#-requirements)
      - [✰ Python modules](#-python-modules)
      - [✰ AWS PoLP Permissions](#-aws-polp-permissions)
    - [☻ Install via Pip](#-install-via-pip)
      - [🐾 1. Create a Virtual Environment (Recommended)](#-1-create-a-virtual-environment-recommended)
      - [🐾 2. Install the Package as OS Command](#-2-install-the-package-as-os-command)
      - [🐾 3. Deactivate the Virtual Environment](#-3-deactivate-the-virtual-environment)
      - [🐾 4. (Option) Uninstall the Package](#-4-option-uninstall-the-package)
  - [🪩 Usage](#-usage)
    - [☻ 🔴AWS Organizations Exporter](#-aws-organizations-exporter)
    - [☻ 🔴AWS Identity Center Exporter](#-aws-identity-center-exporter)
    - [☻ 🔴AWS Multi-Account IAM Exporter](#-aws-multi-account-iam-exporter)
    - [☻ 🟢AWS Free Tier Usage Exporter](#-aws-free-tier-usage-exporter)
  - [🪩 API Documentation](#-api-documentation)
    - [☻ 🔴Organizations Exporter API](#-organizations-exporter-api)
      - [✰ Response Syntax](#-response-syntax)
    - [☻ 🔴Identity Center Exporter API](#-identity-center-exporter-api)
      - [✰ Response Syntax](#-response-syntax-1)
    - [☻ 🔴Multi-Account IAM Exporter API](#-multi-account-iam-exporter-api)
      - [✰ Response Syntax](#-response-syntax-2)
    - [☻ 🟢Free Tier Usage Exporter API](#-free-tier-usage-exporter-api)
      - [✰ Response Syntax](#-response-syntax-3)
  - [🪩 License](#-license)

---

<br>

## 🪩 Installation

---

<br>

### ☻ Requirements

---

<br>

#### ✰ Python modules

<br>

- Python 3.12+
- Boto3
- Flask
- Pytz

---

<br>

#### ✰ AWS PoLP Permissions

<br>

|Target tools|Minimum permissions|
|---|---|
|🔴**AWS Organizations Exporter:**<br>(on Mgmt. account)     |`organizations:Describe*`<br>`organizations:List*`<br>(**Explicit deny**)<br>🚫 `organizations:ListHandshakesForOrganization`<br>🚫 `organizations:ListDelegatedAdministrators`<br>🚫 `organizations:ListCreateAccountStatus`<br>🚫 `organizations:DescribeHandshake`<br>🚫 `organizations:DescribeCreateAccountStatus`<br><br>`account:ListRegions`<br>`account:GetRegionOptStatus`<br><br>`iam:GenerateOrganizationsAccessReport`<br>`iam:GetOrganizationsAccessReport`|
|🔴**AWS Identity Center Exporter:**<br>(on Mgmt. account)  |`identitystore:DescribeGroup`<br>`identitystore:DescribeUser`<br>`identitystore:IsMemberInGroups`<br>`identitystore:ListGroupMemberships`<br>`identitystore:ListGroupMembershipsForMember`<br>`identitystore:ListGroups`<br>`identitystore:ListUsers`<br><br>`sso:DescribePermissionSet`<br>`sso:GetInlinePolicyForPermissionSet`<br>`sso:GetPermissionsBoundaryForPermissionSet`<br>`sso:ListAccountAssignmentsForPrincipal`<br>`sso:ListAccountsForProvisionedPermissionSet`<br>`sso:ListCustomerManagedPolicyReferencesInPermissionSet`<br>`sso:ListInstances`<br>`sso:ListManagedPoliciesInPermissionSet`<br>`sso:ListPermissionSets`<br>`sso:ListPermissionSetsProvisionedToAccount`|
|🔴**AWS Multi-Account IAM Exporter:** <br> (on All accounts) |`GetAccountAuthorizationDetails`|
|🟢**AWS Free Tier Usage Exporter:**<br>(on Mgmt. account) |`freetier:GetFreeTierUsage`<br>`ce:GetCostAndUsage`|

---

<br>

### ☻ Install via Pip

<br>

> 💡 **Tip:**  
>|🙃 If you want to run those tools as a Python script, you'll need to modify this line:|
>|---|
>
>```python
>from aws_exporters.aws_utils import create_session
>```
>
>to:
>
>```python
>from aws_utils.aws_utils import create_session  # For Directory Structure
>```

---

<br>

#### 🐾 1. Create a Virtual Environment (Recommended)

<br>

Before installing the package, it's recommended to create a virtual environment. This isolates the dependencies required for this project from your global Python environment.

📌 **Using `venv` (Python 3.3+)**

- Navigate to the working directory where you want to set up the project:

```bash session
# cd /path/to/your/project
```

- Create a virtual environment:

```bash session
# git clone https://github.com/Hideki-Morita/aws-native-observability-exporters.git
# cd aws-exporters
# python3 -m venv awsvenv
```

- Activate the virtual environment:

  - On macOS/Linux:

  ```bash session
  # source awsvenv/bin/activate
  ```

  - On Windows:

  ```ps1
  PS1> awsvenv\Scripts\activate
  ```

---

<br>

#### 🐾 2. Install the Package as OS Command

<br>

Once the virtual environment is activated, install the package using `pip`:

```bash session
# pip install build
# python3 -m build
# pip install .
```

<details>

<summary>📖An example of output</summary>

>```console
>Collecting build
>  Downloading build-1.2.1-py3-none-any.whl (21 kB)
>Collecting tomli>=1.1.0
>  Downloading tomli-2.0.1-py3-none-any.whl (12 kB)
>Collecting packaging>=19.1
>  Downloading packaging-24.1-py3-none-any.whl (53 kB)
>     |████████████████████████████████| 53 kB 2.6 MB/s             
>Collecting pyproject_hooks
>  Downloading pyproject_hooks-1.1.0-py3-none-any.whl (9.2 kB)
>Collecting importlib-metadata>=4.6
>  Downloading importlib_metadata-8.4.0-py3-none-any.whl (26 kB)
>Collecting zipp>=0.5
>  Downloading zipp-3.20.1-py3-none-any.whl (9.0 kB)
>Installing collected packages: zipp, tomli, pyproject-hooks, packaging, importlib-metadata, build
>Successfully installed build-1.2.1 importlib-metadata-8.4.0 packaging-24.1 pyproject-hooks-1.1.0 tomli-2.0.1 zipp-3.20.1
>WARNING: You are using pip version 21.3.1; however, version 24.2 is available.
>You should consider upgrading via the '/path/to/your/project/aws-exporters/awsvenv/bin/python3 -m pip install --upgrade pip' command.
>
>
>* Creating isolated environment: venv+pip...
>* Installing packages in isolated environment:
>  - setuptools >= 40.8.0
>* Getting build dependencies for sdist...
>running egg_info
>creating aws_exporters.egg-info
>writing aws_exporters.egg-info/PKG-INFO
>:
>* Building sdist...
>running sdist
>running egg_info
>writing aws_exporters.egg-info/PKG-INFO
>:
>running check
>creating aws_exporters-1.0.0+ts1.coldasyou
>creating aws_exporters-1.0.0+ts1.coldasyou/aws_exporters.egg-info
>copying files to aws_exporters-1.0.0+ts1.coldasyou...
>copying setup.py -> aws_exporters-1.0.0+ts1.coldasyou
>:
>* Building wheel from sdist
>* Creating isolated environment: venv+pip...
>* Installing packages in isolated environment:
>  - setuptools >= 40.8.0
>* Getting build dependencies for wheel...
>running egg_info
>writing aws_exporters.egg-info/PKG-INFO
>:
>* Building wheel...
>running bdist_wheel
>running build
>installing to build/bdist.linux-x86_64/wheel
>running install
>running install_egg_info
>running egg_info
>writing aws_exporters.egg-info/PKG-INFO
>:
>adding 'aws_exporters-1.0.0+ts1.coldasyou.dist-info/METADATA'
>adding 'aws_exporters-1.0.0+ts1.coldasyou.dist-info/WHEEL'
>adding 'aws_exporters-1.0.0+ts1.coldasyou.dist-info/entry_points.txt'
>adding 'aws_exporters-1.0.0+ts1.coldasyou.dist-info/top_level.txt'
>adding 'aws_exporters-1.0.0+ts1.coldasyou.dist-info/RECORD'
>removing build/bdist.linux-x86_64/wheel
>Successfully built aws_exporters-1.0.0+ts1.coldasyou.tar.gz and aws_exporters-1.0.0+ts1.coldasyou-py3-none-any.whl
>
>
>Processing /path/to/your/project/aws-exporters
>  Preparing metadata (setup.py) ... done
>Collecting boto3
>  Downloading boto3-1.35.6-py3-none-any.whl (139 kB)
>     |████████████████████████████████| 139 kB 2.5 MB/s            
>Collecting Flask
>  Using cached flask-3.0.3-py3-none-any.whl (101 kB)
>Collecting pytz
>  Using cached pytz-2024.1-py2.py3-none-any.whl (505 kB)
>Collecting botocore<1.36.0,>=1.35.6
>  Downloading botocore-1.35.6-py3-none-any.whl (12.5 MB)
>     |████████████████████████████████| 12.5 MB 5.3 MB/s
>:
>Using legacy 'setup.py install' for aws-exporters, since package 'wheel' is not installed.
>Installing collected packages: six, urllib3, python-dateutil, jmespath, MarkupSafe, botocore, Werkzeug, s3transfer, Jinja2, itsdangerous, click, blinker, pytz, Flask, boto3, aws-exporters
>    Running setup.py install for aws-exporters ... done
>Successfully installed Flask-3.0.3 Jinja2-3.1.4 MarkupSafe-2.1.5 Werkzeug-3.0.4 aws-exporters-1.0.0+ts1.coldasyou blinker-1.8.2 boto3-1.35.6 botocore-1.35.6 click-8.1.7 itsdangerous-2.2.0 jmespath-1.0.1 python-dateutil-2.9.0.post0 pytz-2024.1 s3transfer-0.10.2 six-1.16.0 urllib3-1.26.19
>WARNING: You are using pip version 21.3.1; however, version 24.2 is available.
>You should consider upgrading via the '/path/to/your/project/aws-exporters/awsvenv/bin/python3 -m pip install --upgrade pip' command.
>```

</details>

<br>

```bash session
### Check the result of Install
(Option) # pip show aws-exporters ; pip list | egrep aws-exporters
(Option) # organizations-exporter
```

<details>

<summary>📖An example of output</summary>

>```console
>Name: aws-exporters
>Version: 1.0.0+ts1.coldasyou
>Summary: A set of tools for exporting AWS information
>Home-page: https://github.com/Hideki-Morita/aws-native-observability-exporters
>Author: Hideki.M
>Author-email: Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==
>License: UNKNOWN
>Location: /path/to/your/project/aws-exporters
>Requires: boto3, Flask, pytz
>Required-by: 
>aws-exporters      1.0.0+ts1.coldasyou /path/to/your/project/aws-exporters
>WARNING: You are using pip version 21.3.1; however, version 24.2 is available.
>You should consider upgrading via the '/path/to/your/project/aws-exporters/awsvenv/bin/python3 -m pip install --upgrade pip' command.
>
>
>usage: organizations-exporter [-h] --mgmt-account-id MGMT_ACCOUNT_ID --permission-set-name PERMISSION_SET_NAME --sso-region SSO_REGION [--port PORT]
>                              [--cache-expiry CACHE_EXPIRY] [--access-token ACCESS_TOKEN]
>organizations-exporter: error: the following arguments are required: --mgmt-account-id, --permission-set-name, --sso-region
>```

</details>

<br>

The finall directory structure is like this!

>```console
>.
>├── aws_exporters
>│   ├── aws_utils
>│   │   ├── __init__.py
>│   │   └── aws_utils.py
>│   ├── freetier_usage_exporter.py
>│   ├── identity_center_exporter.py
>│   ├── multi_acc_iam_exporter.py
>│   └── organizations_exporter.py
>├── aws_exporters.egg-info
>├── awsvenv
>│   ├── bin
>│   │   ├── activate
>│   │   ├── freetier-usage-exporter
>│   │   ├── identity-center-exporter
>│   │   ├── multi-acc-iam-exporter
>│   │   ├── organizations-exporter
>├── build
>├── dist
>└── setup.py
>```

---

<br>

#### 🐾 3. Deactivate the Virtual Environment

<br>

When you're done working on the project, deactivate the virtual environment:

```bash session
# deactivate
```

---

<br>

#### 🐾 4. (Option) Uninstall the Package

<br>

```bash session
# pip uninstall aws-exporters
```

---

<br>

## 🪩 Usage

<br>

💡 Each script can be executed as a standalone tool or as a service via Flask. Below is a brief overview of each exporter.

|options:||
|---|---|
|`-h, --help`|show this help message and exit.|
|**`--mgmt-account-id`** _MGMT_ACCOUNT_ID_|Management account ID.|
|**`--permission-set-name`** _PERMISSION_SET_NAME_|Name of the permission set to assume in the management account.|
|**`--sso-region`** _SSO_REGION_|AWS SSO region.|
|`--port` _PORT_|Port to run the Flask app on.|
|`--cache-expiry` _CACHE_EXPIRY_|Cache expiry time in seconds.|
|`--access-token` _ACCESS_TOKEN_|Valid access token.|

---

<br>

### ☻ 🔴AWS Organizations Exporter

<img src="./assets/AWS-Organizations.png" alt="image" width="60" height="60"> 

```bash session
# organizations_exporter --mgmt-account-id <management_account_id> --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--access-token <access_token>]
```

e.g.,

```bash session
# nohup organizations_exporter --mgmt-account-id 121389041924 --permission-set-name AWS-OBS-ReadOnly-ALLTOOWELL --sso-region us-east-1 &
```

>```console
>[1] 4422
>appending output to nohup.out 
>
>
>### In the nohup file looks like this
> * Serving Flask app 'organizations_exporter'
> * Debug mode: off
>2024-04-19 21:34:45,631 - werkzeug - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
> * Running on all addresses (0.0.0.0)
> * Running on http://127.0.0.1:7723
> * Running on http://10.0.1.4:7723
>2024-04-1905 21:34:45,631 - werkzeug - INFO - Press CTRL+C to quit
>```

---

<br>

### ☻ 🔴AWS Identity Center Exporter

<img src="./assets/AWS-Single-Sign-On.png" alt="image" width="60" height="60">

```bash session
# identity_center_exporter --mgmt-account-id <management_account_id> --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--access-token <access_token>]
```

---

<br>

### ☻ 🔴AWS Multi-Account IAM Exporter

<img src="./assets/AWS-Identity-and-Access-Management.png" alt="image" width="60" height="60">

```bash session
# multi_acc_iam_exporter --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--access-token <access_token>]
```

---

<br>

### ☻ 🟢AWS Free Tier Usage Exporter

<img src="./assets/Arch-Category_Cloud-Financial-Management.png" alt="image" width="60" height="60">

```bash session
# freetier_usage_expoter --mgmt-account-id <management_account_id> --permission-set-name <permission_set_name> --sso-region <sso_region> [--port <port>] [--cache-expiry <cache_expiry>] [--access-token <access_token>]
```

---

<br>

## 🪩 API Documentation

<br>

---

<br>

### ☻ 🔴Organizations Exporter API

|||
|---|---|
|Base URL| http://localhost:[port]/<mark>**organization**</mark> |
|Sub URL | http://localhost:[port]/<mark>**organization**</mark>/<mark>**policies**</mark> |
|Sub URL | http://localhost:[port]/<mark>**organization**</mark>/<mark>**access-report**</mark> |
|Port (default: <mark>**7723**</mark>)|You can specify a different port using the `--port` argument when running the Flask app.|
|HTTP Method|**GET**|
|Query Parameters|None|
|Default Cache Period|60 minutes(3600 seconds)|
|Status Codes|- **200 OK**: Request succeeded, and the Organizations structure details are returned.<br>- **4xx Client Error**: There was an error with the request.<br>- **5xx Server Error**: There was an error on the server.|

---

<br>

#### ✰ Response Syntax

<br>

|/organization|
|---|

<details>

<summary>📖Expected Output</summary>

```json
{
  // As Root
  "organizations": [
    {
      "Id": "string",
      "Arn": "string",
      "Name": "string",
      "PolicyTypes": [
        {
          "Type": "string",
          "Status": "string"
        }
      ],
      "Accounts": [
        {
          "Id": "string",
          "Arn": "string",
          "Email": "string",
          "Name": "string",
          "Status": "string",
          "JoinedMethod": "string",
          "JoinedTimestamp": "string"
        }
      ],
      // As Level 1
      "OrganizationalUnits": [
        {
          "Id": "string",
          "Arn": "string",
          "Name": "string",
          "Accounts": [
            {
              "Id": "string",
              "Arn": "string",
              "Email": "string",
              "Name": "string",
              "Status": "string",
              "JoinedMethod": "string",
              "JoinedTimestamp": "string"
            }
          ],
          "OrganizationalUnits": [
            {
              "Id": "string",
              "Arn": "string",
              "Name": "string",
              "Accounts": [
                {
                  "Id": "string",
                  "Arn": "string",
                  "Email": "string",
                  "Name": "string",
                  "Status": "string",
                  "JoinedMethod": "string",
                  "JoinedTimestamp": "string"
                }
              ],
              // As Level 2
              "OrganizationalUnits": []
            }
          ]
        }
      ]
    }
  ]
}
```

</details>

<br>

|/organization/access-report|
|---|

<details>

<summary>📖Expected Output</summary>

```json
{
  "AccessDetails": [
    {
      "ServiceName": "string",
      "ServiceNamespace": "string",
      "TotalAuthenticatedEntities": integer,
      "EntityPath": "string",
      "LastAuthenticatedTime": "string",
      "Region": "string"
    }
  ],
  "IsTruncated": boolean,
  "JobCompletionDate": "string",
  "JobCreationDate": "string",
  "JobStatus": "string",
  "Marker": "string",
  "NumberOfServicesAccessible": integer,
  "NumberOfServicesNotAccessed": integer,
  "ResponseMetadata": {
    "HTTPHeaders": {
      "content-length": "string",
      "content-type": "string",
      "date": "string",
      "x-amzn-requestid": "string"
    },
    "HTTPStatusCode": integer,
    "RequestId": "string",
    "RetryAttempts": integer
  }
}
```

</details>

---

<br>

### ☻ 🔴Identity Center Exporter API

|||
|---|---|
|Base URL| http://localhost:[port]/<mark>**identity-center**</mark> |
|Sub URL | http://localhost:[port]/<mark>**identity-center**</mark>/<mark>**permsets**</mark> |
|Port (default: <mark>**11121**</mark>)|You can specify a different port using the `--port` argument when running the Flask app.|
|HTTP Method|**GET**|
|Query Parameters|None|
|Default Cache Period|60 minutes(3600 seconds)|
|Status Codes|- **200 OK**: Request succeeded, and the workforce users/group and permissionSets details are returned.<br>- **4xx Client Error**: There was an error with the request.<br>- **5xx Server Error**: There was an error on the server.|

---

<br>

#### ✰ Response Syntax

<br>

|/identity-center|
|---|

<details>

<summary>📖Expected Output</summary>

```json
{
  "identity_center": [
    {
      "CreatedDate": "string",
      "IdentityStoreId": "string",
      "InstanceArn": "string",
      "Name": "string",
      "OwnerAccountId": "string",
      "Status": "string",
      "Users": [
        {
          "UserName": "string",
          "UserId": "string",
          "Name": {
            "FamilyName": "string",
            "GivenName": "string"
          },
          "DisplayName": "string",
          "Emails": [
            {
              "Value": "string",
              "Type": "string",
              "Primary": true
            }
          ],
          "IdentityStoreId": "string",
          "JoinedGroup": [
            {
              "GroupId": "string",
              "DisplayName": "string",
              "Description": "string",
              "IdentityStoreId": "string"
            }
          ],
          "AccountAssignments": [
            {
              "AccountId": "string",
              "PrincipalId": "string",
              "PrincipalType": "string",
              "PermissionSetArn": "string",
              "PermissionSet": {
                "Name": "string",
                "PermissionSetArn": "string",
                "CreatedDate": "string",
                "SessionDuration": "string"
              }
            }
          ]
        }
        // Additional user entries go here
      ]
    }
    // Additional instance entries go here
  ]
}
```

</details>

<br>

|/identity-center/permsets|
|---|

<details>

<summary>📖Expected Output</summary>

```json
{
  "PermissionSets": [
    {
      "AttachedManagedPolicies": [
        {
          "Arn": "string",
          "Name": "string"
        },
        {
          "Arn": "string",
          "Name": "string"
        }
      ],
      "CreatedDate": "string",
      "CustomerManagedPolicyReferences": [
        {
          "Name": "string",
          "Path": "string"
        }
      ],
      "Description": "string",
      "InlinePolicy": [
        {
          "None": "string"
        }
      ],
      "Name": "string",
      "PermissionSetArn": "string",
      "PermissionsBoundary": [
        {
          "None": "string"
        }
      ],
      "SessionDuration": "string"
    },
    // And so on
  ]
}
```

</details>

---

<br>

### ☻ 🔴Multi-Account IAM Exporter API

|||
|---|---|
|Base URL| http://localhost:[port]/<mark>**multi-account-auth**</mark>/[Query] |
|Port (default: <mark>**1989**</mark>)|You can specify a different port using the `--port` argument when running the Flask app.|
|HTTP Method|**GET**|
|Query Parameters|**filter_type**: <mark>(Required)</mark> One of the following values:<br> - **`User`**, **`Group`**, **`Role`**, **`LocalManagedPolicy`**, **`AWSManagedPolicy`**|
|Default Cache Period|5 minutes(300 seconds)|
|Status Codes|- **200 OK**: Request succeeded, and the IAM details are returned.<br>- **4xx Client Error**: There was an error with the request.<br>- **5xx Server Error**: There was an error on the server.|

---

<br>

#### ✰ Response Syntax

<br>

|/multi-account-auth/Role|
|---|

<details>

<summary>📖Expected Output</summary>

```json
{
  "AccountID": "string",
  "GroupDetailList": [
    {}
  ],
  "IsTruncated": false,
  "Marker": "string",
  "Policies": [],
  "ResponseMetadata": {
    "HTTPHeaders": {
      "content-length": "string",
      "content-type": "string",
      "date": "string",
      "x-amzn-requestid": "string"
    },
    "HTTPStatusCode": 200,
    "RequestId": "string",
    "RetryAttempts": 0
  },
  "RoleDetailList": [
    {
      "AccountID": "string",
      "Arn": "string",
      "AssumeRolePolicyDocument": {
        "Statement": [
          {
            "Action": [
              "string"
            ],
            "Condition": {
              "StringEquals": {
                "SAML:aud": "string"
              }
            },
            "Effect": "Allow",
            "Principal": {
              "Federated": "string"
            }
          }
        ],
        "Version": "string"
      },
      "AttachedManagedPolicies": [
        {
          "PolicyArn": "string",
          "PolicyName": "string"
        }
      ],
      "CreateDate": "string",
      "InstanceProfileList": [],
      "Path": "string",
      "PermissionsBoundary": {
        "PermissionsBoundaryArn": "string",
        "PermissionsBoundaryType": "string"
      },
      "RoleId": "string",
      "RoleLastUsed": {
        "LastUsedDate": "string",
        "Region": "string"
      },
      "RoleName": "string",
      "RolePolicyList": [],
      "Tags": [
        {
          "Key": "string",
          "Value": "string"
        }
      ]
    }
  ],
  "UserDetailList": [
    {}
  ]
}
```

</details>

---

<br>

### ☻ 🟢Free Tier Usage Exporter API

|||
|---|---|
|Base URL| http://localhost:[port]/<mark>**freetier**</mark> |
|Sub URL | http://localhost:[port]/<mark>**freetier**</mark>/<mark>**cost-explorer**</mark>?[Query] |
|Port (default: <mark>**4921**</mark>)|You can specify a different port using the `--port` argument when running the Flask app.|
|HTTP Method|**GET**|
|Query Parameters|- **`usage_types`**: <mark>(Required)</mark> Comma-separated list of usage types<br> (e.g., `USE1-DataScanned-Bytes,USW2-DataScanned-Bytes`)<br>- `time_periods`: (Optional) Start and end date in `YYYY-MM-DD,YYYY-MM-DD` format|
|Default Cache Period|30 minutes(1800 seconds)|
|Status Codes|- **200 OK**: Request succeeded, and the Free Tier usages are returned.<br>- **4xx Client Error**: There was an error with the request.<br>- **5xx Server Error**: There was an error on the server.|

---

<br>

#### ✰ Response Syntax

<br>

|/freetier|
|---|

<details>

<summary>📖Expected Output</summary>

```json
{
  "freeTierUsages": [
    {
      "actualUsageAmount": "string",
      "description": "string",
      "forecastedUsageAmount": "string",
      "freeTierType": "string",
      "limit": "string",
      "operation": "string",
      "region": "string",
      "service": "string",
      "unit": "string",
      "usageType": "string"
    },
    {
      "actualUsageAmount": "string",
      "description": "string",
      "forecastedUsageAmount": "string",
      "freeTierType": "string",
      "limit": "string",
      "operation": "string",
      "region": "string",
      "service": "string",
      "unit": "string",
      "usageType": "string"
    }
  ]
}
```

</details>

---

<br>

## 🪩 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---