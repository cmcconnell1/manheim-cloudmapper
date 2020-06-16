terraform {
  required_version = ">= 0.11.7"

  backend "s3" {
    bucket         = "mycompany-terraform-state"
    encrypt        = "true"
    region         = "us-west-2"
    dynamodb_table = "mycompany-terraform-locks"
    key            = "dev-usw2/cloudmapper-tf-setup/terraform.tfstate"
  }
}
