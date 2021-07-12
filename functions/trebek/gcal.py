from datetime import datetime, timedelta

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class GCalClient:
    def __init__(self):
        creds = None
        creds = Credentials.from_service_account_file("credentials.json")

        self._service = build("calendar", "v3", credentials=creds)

    def get_events(self, cal_id="primary", event_time=datetime.utcnow()):
        events_result = (
            self._service.events()
            .list(
                calendarId=cal_id,
                timeMin=(event_time - timedelta(minutes=1)).isoformat() + "Z",
                timeMax=(event_time + timedelta(minutes=1)).isoformat() + "Z",
                maxResults=2,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])
