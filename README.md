manheim-cloudmapper
=================

[![TravisCI build badge](https://api.travis-ci.org/manheim/manheim-cloudmapper.png?branch=master)](https://travis-ci.org/manheim/manheim-cloudmapper)

[![Docker Hub Build Status](https://img.shields.io/docker/cloud/build/manheim/manheim-cloudmapper.svg)](https://hub.docker.com/r/manheim/manheim-cloudmapper)

Manheim's Cloudmapper Docker image

This project provides a Docker image for managing Manheim's cloudmapper automation. This project/repository is intended to be used (via the generated Docker image) alongside a terraform module which runs the Docker image in AWS ECS on a schedulued cycle.

* TravisCI Builds: <https://travis-ci.org/manheim/manheim-cloudmapper>
* Docker image: <https://hub.docker.com/r/manheim/manheim-cloudmapper>

For documentation on the upstream cloudmapper project, please see <https://github.com/duo-labs/cloudmapper>

Introduction and Goals
----------------------

Cloudmapper is a tool designed to help analyze AWS environments. Cloudmapper contains a `public` command which is used to find public hosts and port ranges. (More details [here](https://summitroute.com/blog/2018/06/13/cloudmapper_public/).). The purpose of this repository is to run Cloudmapper remotely (on AWS) and use the `public` command to find any AWS resources which have publicly accessible ports. Alerts will then be generated and sent to PagerDuty.

Main Components
---------------

**PagerDuty Alert:** A PagerDuty alert will be generated when a public port is found that is not listed in the `OK_PORTS` environment varbiable. (See Installation and Usage section)

**AWS SES Email:** An SES (simple email service) email is generated and sent to AWS account owners with the cloudmapper audit findings. These findings contain the public port information as well as AWS account specific information (resource counts,  audit findings, etc.). This feature is disabled by default and requires AWS SES setup to function properly. 


Installation and Usage
----------------------

### Deploy Prerequsite AWS Infrastructure
##### Optional: Terraform IAC Prerequisite Deployment:
- Deploy requisite AWS S3 bucket, IAM creds, policies, etc. with Terraform 
  - (tested/validated with Terraform v0.11.14)
  - Simply update the requisite Terraform vars file as needed and then:
    ```console
    cd terraform
    terraform plan
    terraform apply
    ```
  - Note: if using Terraform, after executing the above commands, get your new AWS users KEY and ID:
    ```console
    terraform show | grep 'cloudmapper_tf_setup_user'
    cloudmapper_tf_setup_user_access_id = XXXXXXXXXXXXXXXXXXX
    cloudmapper_tf_setup_user_secret_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXX 
    ```
    - These values should must be included in your `env` file. See below for possible methods to keep this secure.
  - Additional Options
    - use git-crypt to protect sensitive info such as your env files (i.e.: see the `cloudmapper.secret` file).  This file must be updated with the AWS users credentials.

##### Or Use An Alternate Method 
If not using Terraform, use an alternative to provision the requisite AWS infrastructure and IAM credentials per your teams tools, etc.
Note that the infrastructure must exist (S3 bucket, cloud user, IAM cred's, and permissions, creating a requisite config.json file and copying it to the S3 bucket, etc.) prior to running cloudmapper.


**WARNING:** This project is NOT a Python package, this is a Docker image which contains cloudmapper code from [duo-labs](https://github.com/duo-labs/cloudmapper) as well as custom python code to support PagerDuty Alerting and AWS SES notifications.

### Run Docker image
To use the docker image, execute a `docker run` command  on the `manheim/manheim-cloudmapper` image. Environment variables are required for the docker container to execute. The recommended way to set the environment variables is with the `--env-file` flag.
```
docker run --env-file <env_file> manheim/manheim-cloudmapper:<tag>
```

##### env-file example 
- (Note: see cloudmapper.secret file for required ENV vars):
- The docker image will fail to complete a successful run, and therefore won't send the report if the expected variables are not found.
```
S3_BUCKET=aws-account-us-east-1-cloudmapper
ACCOUNT=aws-account
DATADOG_API_KEY=abc123456
...
```

**Environment Varaibles**

| Name            | Description                                                                                                                                     | Example          |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| S3_BUCKET       | AWS S3 bucket name where config.json file for cloudmapper is expected. This json file contains AWS account information for the cloudmapper run. | mybucket         |
| ACCOUNT         | Name of AWS account where Cloudmapper will be running                                                                                           | aws-company-prod |
| DATADOG_API_KEY | Datadog API key, for sending metrics                                                                                                            | abc123...        |
| PD_SERVICE_KEY  | PagerDuty Service Key (Events V1 integration) for alerting on critical thresholds crossed                                                       | xyz890...        |
| OK_PORTS        | A list of acceptable publicly accessible ports in string format                                                                                  | 80,443           |
| AWS_REGION      | AWS Region from which SES will send emails                                                                                                      | us-east-1        |
| SES_ENABLED     | string to enable/disable email notification via SES.                                                                                            | true             |
| SES_SENDER      | Email address of SES sender                                                                                                                     | foo@bar.com      |
| SES_RECIPIENT   | Email address of SES recipient                                                                                                                  | bar@foo.com      |

**AWS Authentication:**  
In addition to the environment variables above, the Docker container requires access to the AWS account in which cloudmapper will be run. Any method of boto3 AWS [authentication](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#credentials) is supported (environment varaibles, ~/.aws/credentials, ~/.aws/config, etc.)

When using environment varaibles, the following AWS Environment varaibles can be set in the env-file:
```
AWS_SESSION_TOKEN
AWS_DEFAULT_REGION
AWS_SECRET_ACCESS_KEY
AWS_ACCESS_KEY_ID
```

The following privilieges are required for the IAM user running cloudmapper:  
`arn:aws:iam::aws:policy/SecurityAudit`  
`arn:aws:iam::aws:policy/job-function/ViewOnlyAccess`

The permissions for the user/account running the docker image must allow remote downloading the config.json from the S3 bucket to the local filesystem: ./config.json
