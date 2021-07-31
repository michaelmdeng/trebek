resource "google_secret_manager_secret" "twilio_account_sid" {
  secret_id = "TWILIO_ACCOUNT_SID"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "twilio_api_key" {
  secret_id = "TWILIO_API_KEY"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "twilio_api_secret" {
  secret_id = "TWILIO_API_SECRET"

  replication {
    automatic = true
  }
}

data "google_secret_manager_secret_version" "twilio_account_sid_value" {
  secret = google_secret_manager_secret.twilio_account_sid.secret_id
}

data "google_secret_manager_secret_version" "twilio_api_key_value" {
  secret = google_secret_manager_secret.twilio_api_key.secret_id
}

data "google_secret_manager_secret_version" "twilio_api_secret_value" {
  secret = google_secret_manager_secret.twilio_api_secret.secret_id
}
