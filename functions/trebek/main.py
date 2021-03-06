import asyncio
import contextlib
from dataclasses import asdict
from datetime import datetime
import logging

import flask
import werkzeug.exceptions

from gcal import GCalClient
from config import ConfigClient
import jeopardy
import model
import util


logging.basicConfig(level=logging.INFO)


def trebek(request):
    form_data = request.form
    logging.info("Received request with data: %s", form_data)

    try:
        with model.ForwardingStatusContext(request):
            forward_request = parse_request(request)

            forward_info = asyncio.run(get_forward_response(forward_request))
            return flask.make_response(flask.jsonify(asdict(forward_info)), 200)
    except werkzeug.exceptions.BadRequestKeyError as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 400)
    except Exception as e:
        logging.exception(e)
        return flask.make_response(flask.jsonify({"error": e.__str__()}), 500)


def parse_request(request):
    form_data = request.form

    request = model.ForwardingRequest(
        numberFrom=form_data["callFrom"],
        numberTo=form_data["callTo"],
        requestTime=datetime.utcnow(),
    )
    logging.info("Received forwarding request: %s", request)

    return request


def get_jeopardy_info_tasks(client, forward_request, schedule_configs):
    return [
        jeopardy.jeopardy_info(
            client,
            schedule_config,
            forward_request.requestTime,
        )
        for schedule_config in schedule_configs
    ]


async def get_forward_response(forward_request):
    """
    Retrieves the Jeopardy oncall number to forward to.

    Based on checking the relevant Google Calendar instances to see who is
    currently on shift.
    """

    async with contextlib.AsyncExitStack() as stack:
        client, conf = await asyncio.gather(
            stack.enter_async_context(GCalClient()),
            stack.enter_async_context(ConfigClient()),
        )
        tasks = get_jeopardy_info_tasks(
            client,
            forward_request,
            [
                model.ScheduleConfig(**schedule_config)
                for schedule_config in conf["scheduleConfig"]
            ],
        )
        jeopardy_config = await util.wait_until(
            tasks, lambda task: task.exception() is None and task.result() is not None
        )

        if jeopardy_config is None:
            raise model.NoJeopardyChiefException("No Jeopardy Chief found.")
        else:
            return generate_response(jeopardy_config)


def generate_response(jeopardy_config):
    return model.ForwardingResponse(
        name=jeopardy_config.name,
        forwardTo=jeopardy_config.phoneNumber,
        onShift=jeopardy_config.onShift,
    )
