from datetime import datetime, timedelta
import json
import logging

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

from secret import SecretsClient


class GCalClient:
    def __init__(self):
        self._google = None

    async def __aenter__(self):
        service_account_creds = json.loads(
            await SecretsClient().get("TREBEK_SERVICE_ACCOUNT_CREDENTIALS")
        )
        creds = ServiceAccountCreds(
            scopes=["https://www.googleapis.com/auth/calendar.events.readonly"],
            **service_account_creds
        )

        self._google = Aiogoogle(service_account_creds=creds)
        await self._google.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc, backtrace):
        if self._google and self._google._get_session():
            return await self._google.__aexit__(exc_type, exc, backtrace)

    async def get_events_async(self, cal_id="primary", event_time=datetime.utcnow()):
        cal = await self._google.discover("calendar", "v3")
        logging.debug("Checking calendar events for id: %s at: %s", cal_id, event_time)
        events_result = await self._google.as_service_account(
            cal.events.list(
                calendarId=cal_id,
                timeMin=(event_time - timedelta(minutes=1)).isoformat() + "Z",
                timeMax=(event_time + timedelta(minutes=1)).isoformat() + "Z",
                maxResults=2,
                singleEvents=True,
                orderBy="startTime",
            )
        )

        return events_result.get("items", [])
