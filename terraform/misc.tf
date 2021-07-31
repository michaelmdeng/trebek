terraform {
  required_providers {
    twilio = {
      source  = "RJPearson94/twilio"
      version = ">= 0.2.1"
    }
  }

  backend "gcs" {
    bucket = "trebek-terraform"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = "trebek"
  region  = "us-west2"
  zone    = "us-west2-a"
}

resource "google_project_service" "iam_service" {
  project = "trebek"
  service = "iam.googleapis.com"

  timeouts {
    create = "15m"
    update = "15m"
  }
}

resource "google_project_service" "functions_service" {
  project = "trebek"
  service = "cloudfunctions.googleapis.com"

  timeouts {
    create = "15m"
    update = "15m"
  }
}

resource "google_project_service" "build_service" {
  project = "trebek"
  service = "cloudbuild.googleapis.com"

  timeouts {
    create = "15m"
    update = "15m"
  }
}

resource "google_project_service" "secret_manager_service" {
  project = "trebek"
  service = "secretmanager.googleapis.com"

  timeouts {
    create = "15m"
    update = "15m"
  }
}

provider "twilio" {
  account_sid = data.google_secret_manager_secret_version.twilio_account_sid_value.secret_data
  api_key = data.google_secret_manager_secret_version.twilio_api_key_value.secret_data
  api_secret = data.google_secret_manager_secret_version.twilio_api_secret_value.secret_data
}
