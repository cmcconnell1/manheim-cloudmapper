
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "cloudmapper-data" {
  bucket = "${var.cloudmapper_setup_bucket_name}"
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "cloudmapper-data-private" {
  bucket = "${aws_s3_bucket.cloudmapper-data.id}"

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_iam_user" "cloudmapper-user" {
  name = "${var.cloudmapper_setup_iam_user}"
}

resource "aws_iam_policy" "s3-cloudmapper-iam-access-policy" {
  name        = "cloudmapper-iam-access-policy"
  description = "Policy to allow cloudmapper user requisite access to S3 and SES"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Effect": "Allow",
          "Action": [
              "s3:GetObject",
              "s3:DeleteObject",
              "s3:PutObject",
              "s3:AbortMultipartUpload",
              "s3:ListMultipartUploadParts"
          ],
          "Resource": [
              "${aws_s3_bucket.cloudmapper-data.arn}/*"
          ]
      },
      {
          "Effect": "Allow",
          "Action": [
              "s3:ListBucket"
          ],
          "Resource": [
              "${aws_s3_bucket.cloudmapper-data.arn}"
          ]
      },
      {
      "Effect":"Allow",
      "Action":[
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource":"*",
      "Condition":{
        "ForAllValues:StringLike":{
          "ses:Recipients":[
            "${var.cloudmapper_allow_ses_recipient}"
          ]
        }
      }
      }
  ]
}
EOF
}

resource "aws_iam_user_policy_attachment" "attach-cloudmapperbucket" {
  user       = "${aws_iam_user.cloudmapper-user.name}"
  policy_arn = "${aws_iam_policy.s3-cloudmapper-iam-access-policy.arn}"
}

resource "aws_iam_access_key" "cloudmapper-user-creds" {
  user    = "${aws_iam_user.cloudmapper-user.name}"
}

# attach AWS managed securityaudit policy to our cloudmapper-user
resource "aws_iam_user_policy_attachment" "attach-securityaudit" {
  user       = "${aws_iam_user.cloudmapper-user.name}"
  policy_arn = "${var.cloudmapper_security_audit_policy_arn}"
}

data "template_file" "configdotjson" {
  template = "${file("${path.module}/templates/config.json.tpl")}"

  vars {
    cloudmapper_account_id                = "${data.aws_caller_identity.current.account_id}"
    cloudmapper_account_name              = "${var.cloudmapper_account_name}"

    cloudmapper_cidr_range_1              = "${var.cloudmapper_cidr_range_1}"
    cloud_mapper_cidr_range_1_description = "${var.cloudmapper_cidr_range_1_description}"

    cloudmapper_cidr_range_2              = "${var.cloudmapper_cidr_range_2}"
    cloud_mapper_cidr_range_2_description = "${var.cloudmapper_cidr_range_2_description}"

    cloudmapper_cidr_range_3              = "${var.cloudmapper_cidr_range_3}"
    cloud_mapper_cidr_range_3_description = "${var.cloudmapper_cidr_range_3_description}"
  }
}

# create a valid yaml file from our rendered template_file
resource "local_file" "configdotjson" {
  content  = "${data.template_file.configdotjson.rendered}"
  filename = "files/config.json"
  #depends_on = ["data.template_file.configdotjson"]
}

resource "aws_s3_bucket_object" "configdotjson" {
  bucket = "${var.cloudmapper_setup_bucket_name}"
  source = "files/config.json"
  key = "config.json"

  # The filemd5() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
  # etag = "${md5(file("path/to/file"))}"
  #etag = "${filemd5("files/config.json")}"
  depends_on = ["local_file.configdotjson", "aws_s3_bucket.cloudmapper-data"]
}
