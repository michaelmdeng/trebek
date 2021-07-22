from datetime import datetime
import logging

import flask
import werkzeug.exceptions

import gcal
import config
import jeopardy
from model import ForwardingInfo, ForwardingStatusContext


logging.basicConfig(level=logging.INFO)


def trebek(request):
    form_data = request.form
    logging.info("Received request with data: %s", form_data)

    try:
        with ForwardingStatusContext(form_data):
            call_from = form_data["callFrom"]
            call_to = form_data["callTo"]
            call_time = datetime.utcnow()

            forward_info = get_forward_info(call_from, call_to, call_time)
            return flask.make_response(flask.jsonify(forward_info._asdict()), 200)
    except werkzeug.exceptions.BadRequestKeyError as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 400)
    except Exception as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 500)


def get_forward_info(call_from, call_to, call_time):
    """
    Retrieves the Jeopardy oncall number to forward to.

    Based on checking the relevant Google Calendar instances to see who is
    currently on shift.
    """

    logging.info("Received call from %s to %s at %s", call_from, call_to, call_time)

    client = gcal.GCalClient()
    conf = config.TrebekConfig().config

    for person in conf["scheduleConfig"]:
        calendar_id = person["calendarId"]
        logging.info(
            "Checking calendar events for %s from %s", person["name"], calendar_id
        )
        events = client.get_events(calendar_id, call_time)
        if any(event for event in events if jeopardy.is_jeop_chief_shift(event)):
            logging.info(
                "Detected Jeopardy Chief event for %s, forwarding call to %s",
                person["name"],
                person["phoneNumber"],
            )

            on_shift = any(event for event in events if jeopardy.is_em_shift(event))
            logging.info("Detected work shift for %s", person["name"])

            return ForwardingInfo(person["name"], person["phoneNumber"], on_shift)

    default_number = conf["defaultPhoneNumber"]
    default_name = conf["defaultName"]
    logging.warning(
        "Did not detect any Jeopardy Chief shifts for any members, forwarding call to default: %s",
        default_number,
    )

    return ForwardingInfo(default_name, default_number, False)
