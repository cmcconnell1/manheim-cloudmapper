variable "cloudmapper_account_name" {
  type = "string"
}

variable "cloudmapper_allow_ses_recipient" {
  type = "string"
}

variable "cloudmapper_setup_bucket_name" {
  type = "string"
}

variable "cloudmapper_setup_iam_user" {
  type = "string"
}

variable "cloudmapper_security_audit_policy_arn" {
  type        = "string"
  description = "existing AWS-managed securityaudit policy arn"
}

variable "cloudmapper_view_only_access_policy_arn" {
  type        = "string"
  description = "existing AWS-managed viewonlyaccess policy arn"
}

variable "cloudmapper_cidr_range_1" {
  type        = "string"
  description = "First CIDR range"
}

variable "cloudmapper_cidr_range_1_description" {
  type        = "string"
}

variable "cloudmapper_cidr_range_2" {
  type        = "string"
  description = "Second CIDR range"
}

variable "cloudmapper_cidr_range_2_description" {
  type        = "string"
}

variable "cloudmapper_cidr_range_3" {
  type        = "string"
  description = "Third CIDR range"
}

variable "cloudmapper_cidr_range_3_description" {
  type        = "string"
}
