import asyncio
from datetime import datetime
import logging

import flask
import werkzeug.exceptions

import gcal
import config
import jeopardy
from model import ForwardingInfo, ForwardingStatusContext
import util


logging.basicConfig(level=logging.INFO)


def trebek(request):
    form_data = request.form
    logging.info("Received request with data: %s", form_data)

    try:
        with ForwardingStatusContext(form_data):
            call_from = form_data["callFrom"]
            call_to = form_data["callTo"]
            call_time = datetime.utcnow()

            forward_info = asyncio.run(get_forward_info(call_from, call_to, call_time))
            return flask.make_response(flask.jsonify(forward_info._asdict()), 200)
    except werkzeug.exceptions.BadRequestKeyError as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 400)
    except Exception as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 500)


async def get_forward_info(call_from, call_to, call_time):
    """
    Retrieves the Jeopardy oncall number to forward to.

    Based on checking the relevant Google Calendar instances to see who is
    currently on shift.
    """

    logging.info("Received call from %s to %s at %s", call_from, call_to, call_time)

    conf = config.TrebekConfig().config

    async with gcal.GCalClient() as client:
        tasks = [
            jeopardy.jeopardy_info(client, person, call_time)
            for person in conf["scheduleConfig"]
        ]
        jeopardy_config = await util.wait_until(
            tasks, lambda task: task.result() is not None
        )
        return ForwardingInfo(
            jeopardy_config.name, jeopardy_config.phoneNumber, jeopardy_config.onShift
        )
