# Trebek

Trebek is a service to manage jeopardy scheduling for UCSF EM residents.

It consists of a Google Cloud Function that receives call events from Twilio and
queries Google Calendar to determine where to forward the call to.

## Development

Install dependencies (preferably in a virtualenv):

```bash
pip install -r requirements.txt
```

## Infrastructure

Resources are managed by Terraform.

To initialize, set environment variables to authenticate the Twilio provider:

```bash
export TWILIO_ACCOUNT_SID="..."
export TWILIO_API_KEY="..."
export TWILIO_API_SECRET="..."
```

Ensure you're in the `terraform/` sub-directory:

```bash
cd terraform
```

Then, run Terraform updates as normal:

```bash
terraform plan
terraform apply
```
