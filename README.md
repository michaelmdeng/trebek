# Trebek

Trebek is a service to manage jeopardy scheduling for UCSF EM residents.

It consists of a Google Cloud Function that receives call events from Twilio and
queries Google Calendar to determine where to forward the call to.
