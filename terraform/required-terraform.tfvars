# cloudmapper
cloudmapper_account_name = "mycompany"
cloudmapper_setup_bucket_name = "mycompany-cloudmapper"
cloudmapper_setup_iam_user = "cloudmapper"
cloudmapper_allow_ses_recipient = "*@mycompany.com"

cloudmapper_cidr_range_1 = "10.1.0.0/20"
cloudmapper_cidr_range_1_description = "Legacy DEV, STAGE, PROD us-west-1 VPC"

cloudmapper_cidr_range_2 = "10.2.1.0/20"
cloudmapper_cidr_range_2_description = "DEV us-west-2 VPC"

cloudmapper_cidr_range_3 = "10.3.1.0/20"
cloudmapper_cidr_range_3_description = "PROD us-west-2 VPC"

# Requisite AWS-managed IAM policies
cloudmapper_security_audit_policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
cloudmapper_view_only_access_policy_arn = "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"

