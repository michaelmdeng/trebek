# Trebek

Trebek is a service to manage jeopardy scheduling for UCSF EM residents.

It consists of a Google Cloud Function that receives call events from Twilio and
queries Google Calendar to determine where to forward the call to.

## Infrastructure

Resources are managed by Terraform.

To initialize, set environment variables to authenticate the Twilio provider:

```bash
export TWILIO_ACCOUNT_SID="..."
export TWILIO_API_KEY="..."
export TWILIO_API_SECRET="..."
```

Then, run Terraform updates as normal:

```bash
terraform plan
terraform apply
```
