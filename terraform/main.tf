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

resource "twilio_phone_number" "trebek_number" {
  account_sid         = "AC5bb6f2b2ef55fc87c7bea9e7c16c84ee"
  phone_number        = "+14153246262"
  status_callback_url = twilio_studio_flow.trebek_flow.webhook_url

  messaging {
    url = twilio_studio_flow.trebek_flow.webhook_url
  }
}

resource "twilio_studio_flow" "trebek_flow" {
  friendly_name  = "Trebek"
  status         = "published"
  commit_message = "Published Flow"
  validate       = true

  definition = jsonencode({
    "description": "Trebek",
    "states": [
      {
	"name": "Trigger",
	"type": "trigger",
	"transitions": [
	  {
	    "next": "SendCallMessage",
	    "event": "incomingMessage"
	  },
	  {
	    "next": "QueryForwardingNumber",
	    "event": "incomingCall"
	  },
	  {
	    "event": "incomingRequest"
	  }
	],
	"properties": {
	  "offset": {
	    "x": 340,
	    "y": 100
	  }
	}
      },
      {
	"name": "ForwardCall",
	"type": "connect-call-to",
	"transitions": [
	  {
	    "event": "callCompleted"
	  },
	  {
	    "event": "hangup"
	  }
	],
	"properties": {
	  "offset": {
	    "x": 140,
	    "y": 1630
	  },
	  "caller_id": "{{contact.channel.address}}",
	  "noun": "number",
	  "to": "{{widgets.QueryForwardingNumber.parsed.forwardTo}}",
	  "timeout": 30
	}
      },
      {
	"name": "QueryForwardingNumber",
	"type": "make-http-request",
	"transitions": [
	  {
	    "next": "SayCurrentChief",
	    "event": "success"
	  },
	  {
	    "next": "SayFailed",
	    "event": "failed"
	  }
	],
	"properties": {
	  "offset": {
	    "x": 480,
	    "y": 430
	  },
	  "method": "POST",
	  "content_type": "application/x-www-form-urlencoded;charset=utf-8",
	  "body": "{\n  \"to\": {{trigger.call.To}} ,\n  \"from\": {{trigger.call.From}} \n}",
	  "parameters": [
	    {
	      "value": "{{trigger.call.From}}",
	      "key": "callFrom"
	    },
	    {
	      "value": "{{trigger.call.To}}",
	      "key": "callTo"
	    }
	  ],
	  "url": google_cloudfunctions_function.trebek.https_trigger_url
	}
      },
      {
	"name": "SayCurrentChief",
	"type": "say-play",
	"transitions": [
	  {
	    "next": "SplitOnShift",
	    "event": "audioComplete"
	  }
	],
	"properties": {
	  "voice": "default",
	  "offset": {
	    "x": 60,
	    "y": 730
	  },
	  "loop": 1,
	  "say": "The current Jeopardy Chief is {{widgets.QueryForwardingNumber.parsed.name}}.\n\nForwarding your call now.",
	  "language": "en-US"
	}
      },
      {
	"name": "SayFailed",
	"type": "say-play",
	"transitions": [
	  {
	    "next": "ForwardCallBackup",
	    "event": "audioComplete"
	  }
	],
	"properties": {
	  "offset": {
	    "x": 670,
	    "y": 720
	  },
	  "loop": 1,
	  "say": "I could not determine the current Jeopardy Chief. Forwarding your call to Mindy Duong."
	}
      },
      {
	"name": "ForwardCallBackup",
	"type": "connect-call-to",
	"transitions": [
	  {
	    "event": "callCompleted"
	  },
	  {
	    "event": "hangup"
	  }
	],
	"properties": {
	  "offset": {
	    "x": 670,
	    "y": 1030
	  },
	  "caller_id": "{{contact.channel.address}}",
	  "noun": "number",
	  "to": "+18582055744",
	  "timeout": 30
	}
      },
      {
	"name": "SendCallMessage",
	"type": "send-message",
	"transitions": [
	  {
	    "event": "sent"
	  },
	  {
	    "event": "failed"
	  }
	],
	"properties": {
	  "offset": {
	    "x": -150,
	    "y": 410
	  },
	  "service": "{{trigger.message.InstanceSid}}",
	  "channel": "{{trigger.message.ChannelSid}}",
	  "from": "{{flow.channel.address}}",
	  "to": "{{contact.channel.address}}",
	  "body": "If you'd like to contact the current Jeopardy Chief, please call this number."
	}
      },
      {
	"name": "SayChiefShift",
	"type": "say-play",
	"transitions": [
	  {
	    "next": "ForwardCall",
	    "event": "audioComplete"
	  }
	],
	"properties": {
	  "offset": {
	    "x": 250,
	    "y": 1270
	  },
	  "loop": 1,
	  "say": "{{widgets.QueryForwardingNumber.parsed.name}} may be on shift, so you may need to call multiple times to reach them."
	}
      },
      {
	"name": "SplitOnShift",
	"type": "split-based-on",
	"transitions": [
	  {
	    "next": "ForwardCall",
	    "event": "noMatch"
	  },
	  {
	    "next": "SayChiefShift",
	    "event": "match",
	    "conditions": [
	      {
		"friendly_name": "If value equal_to true",
		"arguments": [
		  "{{widgets.QueryForwardingNumber.parsed.onShift}}"
		],
		"type": "equal_to",
		"value": "true"
	      }
	    ]
	  }
	],
	"properties": {
	  "input": "{{widgets.QueryForwardingNumber.parsed.onShift}}",
	  "offset": {
	    "x": 90,
	    "y": 1020
	  }
	}
      }
    ],
    "initial_state": "Trigger",
    "flags": {
      "allow_concurrent_calls": true
    }
  })
}
