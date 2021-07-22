from collections import namedtuple
from datetime import datetime
import logging

from google.cloud import datastore

DATASTORE_CLIENT = None

ForwardingInfo = namedtuple(
    "ForwardingInfo",
    [
        "name",  # name of the person to forward to
        "forwardTo",  # phone number of the person to forward to
        "onShift",  # whether the person forwarding to is on shift
    ],
)


class ForwardingStatusContext:
    def __init__(self, data):
        self._id = None
        self._status = ForwardingStatus.from_data(data)

    def __enter__(self):
        self._status = self._status._replace(
            id=self._id,
            status=ForwardingStatus.START_STATUS,
            startTime=datetime.utcnow(),
        )
        self._id = self._status.save().id

    def __exit__(self, type, exc, traceback):
        if type is None:
            self._status = self._status._replace(
                id=self._id,
                status=ForwardingStatus.SUCCESS_STATUS,
                endTime=datetime.utcnow(),
            )
            self._id = self._status.save().id
            return True
        else:
            self._status = self._status._replace(
                id=self._id,
                status=ForwardingStatus.ERROR_STATUS,
                endTime=datetime.utcnow(),
                error=exc.__str__(),
            )
            self._id = self._status.save().id
            return False


class ForwardingStatus(
    namedtuple(
        "ForwardingStatus",
        ["id", "requestData", "startTime", "endTime", "status", "error"],
    )
):
    """
    Describes status of a call-forwarding operation. Persisted to Google Cloud
    Datastore using save(). Implements context manager to enable saving and
    updating the operation status on start, completion, or error.
    """

    START_STATUS = "START"
    SUCCESS_STATUS = "SUCCESS"
    ERROR_STATUS = "ERROR"

    @staticmethod
    def from_data(form_data):
        return ForwardingStatus(None, form_data, None, None, None, None)

    def save(self):
        global DATASTORE_CLIENT
        if DATASTORE_CLIENT is None:
            DATASTORE_CLIENT = datastore.Client()
        client = DATASTORE_CLIENT

        if self.id is not None:
            key = client.key("ForwardingStatus", self.id)
        else:
            key = client.key("ForwardingStatus")

        entity = datastore.Entity(key)
        entity.update(self._asdict())

        logging.debug("Saving ForwardingStatus to Datastore: %s", entity)
        client.put(entity)
        return entity
