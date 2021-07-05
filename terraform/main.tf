resource "google_storage_bucket" "trebek_artifacts_bucket" {
  name = "gcf-sources-77550555524-us-west2"
  location = "us-west2"

  cors {
    method = ["GET"]
    origin = [
      "https://*.cloud.google.com",
      "https://*.corp.google.com",
      "https://*.corp.google.com:*"
    ]
  }
}

data "google_storage_bucket_object" "trebek_archive" {
  name   = "trebek-f83d62db-e255-4eaf-930e-39c7b039bbfe/version-3/function-source.zip"
  bucket = google_storage_bucket.trebek_artifacts_bucket.name
}

resource "google_service_account" "trebek_service_account" {
  account_id   = "trebek-service-account"
  display_name = "Service Account for Trebek"
}

resource "google_cloudfunctions_function" "trebek" {
  name        = "trebek"
  description = "Cloud function for trebek"
  runtime     = "python39"

  source_archive_bucket = google_storage_bucket.trebek_artifacts_bucket.name
  source_archive_object = data.google_storage_bucket_object.trebek_archive.name

  available_memory_mb   = 128
  trigger_http          = true
  timeout               = 60
  entry_point           = "trebek"

  service_account_email = google_service_account.trebek_service_account.email

  timeouts {}

  labels = {
    "deployment-tool" = "cli-gcloud"
  }
}
