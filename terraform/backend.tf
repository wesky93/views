terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "views"

    workspaces {
      prefix = "views_"
    }
  }
}
