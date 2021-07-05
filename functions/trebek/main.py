from datetime import datetime
import logging

import flask

import gcal
import config


def trebek(request):
    try:
        form_data = request.form
        call_from = form_data["callFrom"]
        call_to = form_data["callTo"]
        call_time = datetime.now()

        forward_number = get_forward_number(call_from, call_to, call_time)

        return flask.make_response(flask.jsonify({"forwardTo": forward_number}), 200)
    except Exception as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 500)


def get_forward_number(call_from, call_to, call_time):
    logging.info("Received call from %s to %s at %s", call_from, call_to, call_time)

    client = gcal.GCalClient()
    conf = config.TrebekConfig().config

    for person in conf["scheduleConfig"]:
        calendar_id = person["calendarId"]
        logging.info(
            "Checking calendar events for %s from %s", person["name"], calendar_id
        )
        events = client.get_events(calendar_id)
        if any([event for event in events if event["summary"] == "Jeop Chief"]):
            logging.info(
                "Detected Jeopardy Chief event for %s, forwarding call to %s",
                person["name"],
                person["phoneNumber"],
            )

            return person["phoneNumber"]

    default_number = conf["defaultPhoneNumber"]
    logging.warning(
        "Did not detect any Jeopardy Chief shifts for any members, forwarding call to default: %s",
        default_number,
    )

    return default_number
