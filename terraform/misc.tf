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

  disable_dependent_services = true
}

resource "google_project_service" "functions_service" {
  project = "trebek"
  service = "cloudfunctions.googleapis.com"

  timeouts {
    create = "15m"
    update = "15m"
  }

  disable_dependent_services = true
}

resource "google_project_service" "build_service" {
  project = "trebek"
  service = "cloudbuild.googleapis.com"

  timeouts {
    create = "15m"
    update = "15m"
  }

  disable_dependent_services = true
}