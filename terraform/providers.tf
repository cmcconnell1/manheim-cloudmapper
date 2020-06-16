provider "aws" {
  version = ">= 1.22.0"
  region  = "us-west-2"
  alias = "west2"
}

# additional provider for cross-region vpc peering
provider "aws" {
  version = ">= 1.22.0"
  region  = "us-west-1"
  alias = "west1"
}

provider "local" {
  version = ">= 1.1"
}

provider "null" {
  version = ">= 2.0"
}

provider "template" {
  version = ">= 2.0"
}

provider "kubernetes" {
  version = ">= 1.5.2"
}
