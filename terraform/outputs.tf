output "cloudmapper_tf_setup_user_secret_key" {
  value = "${aws_iam_access_key.cloudmapper-user-creds.secret}"
  sensitive = true
}

output "cloudmapper_tf_setup_user_access_id" {
  value = "${aws_iam_access_key.cloudmapper-user-creds.id}"
  sensitive = true
}

output "cloudmapper_tf_setup_bucket_arn" {
  value = "${aws_s3_bucket.cloudmapper-data.arn}"
}

output "cloudmapper_tf_setup_bucket_name" {
  value = "${aws_s3_bucket.cloudmapper-data.id}"
}
