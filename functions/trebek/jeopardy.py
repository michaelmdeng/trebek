"""
Helpers for working with Jeopardy shifts on a calendar.
"""

from dataclasses import dataclass
import logging


@dataclass
class JeopardyScheduleConfig:
    name: str
    phoneNumber: str
    calendarId: str
    onShift: bool


def is_jeop_chief_shift(event):
    return event["summary"] == "Jeop Chief"


def is_em_shift(event):
    return event["summary"] != "Jeop Chief"


async def jeopardy_info(gcal_client, schedule_config, call_time):
    """
    Check jeopardy info for the given schedule and time. If the calendar
    contains a valid jeopardy shift, returns JeopardyScheduleConfig, else
    returns None.
    """

    calendar_id = schedule_config["calendarId"]
    logging.info("Checking calendar events for %s", schedule_config["name"])
    events = await gcal_client.get_events_async(calendar_id, call_time)
    if any(event for event in events if is_jeop_chief_shift(event)):
        logging.info(
            "Detected Jeopardy Chief event for %s, forwarding call to %s",
            schedule_config["name"],
            schedule_config["phoneNumber"],
        )

        on_shift = any(event for event in events if is_em_shift(event))
        logging.info("Detected work shift for %s", schedule_config["name"])

        return JeopardyScheduleConfig(
            name=schedule_config["name"],
            phoneNumber=schedule_config["phoneNumber"],
            calendarId=schedule_config["calendarId"],
            onShift=on_shift,
        )
    else:
        return None
