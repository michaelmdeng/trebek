from dataclasses import asdict, dataclass, replace
from datetime import datetime
import logging

from google.cloud import datastore

DATASTORE_CLIENT = None


class NoJeopardyChiefException(Exception):
    pass


@dataclass
class ForwardingRequest:
    """
    Request to forward a call to the current Jeopardy chief.
    """

    numberFrom: str
    numberTo: str
    requestTime: datetime = datetime.utcnow()


@dataclass
class ScheduleConfig:
    """
    Scheduling config for a given person.
    """

    name: str
    phoneNumber: str
    calendarId: str
    enabled: str


@dataclass
class JeopardyScheduleConfig:
    """
    Scheduling config for a Jeopardy Chief.
    """

    name: str
    phoneNumber: str
    calendarId: str
    onShift: bool


@dataclass
class ForwardingResponse:
    """
    Response that indicates the current Jeopardy chief to forward the call to.
    """

    name: str
    forwardTo: str
    onShift: bool


@dataclass
class ForwardingStatus:
    """
    Status of a call-forwarding operation. Persisted to Google Cloud
    Datastore using save(). Implements context manager to enable saving and
    updating the operation status on start, completion, or error.
    """

    id: str
    requestData: str
    startTime: datetime
    endTime: datetime
    status: str
    error: str = ""

    START_STATUS = "START"
    SUCCESS_STATUS = "SUCCESS"
    ERROR_STATUS = "ERROR"

    @staticmethod
    def from_request(request):
        return ForwardingStatus(
            id=None, requestData=request.form, startTime=None, endTime=None, status=None
        )

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
        entity.update(asdict(self))

        logging.debug("Saving ForwardingStatus to Datastore: %s", entity)
        client.put(entity)
        return entity


class ForwardingStatusContext:
    def __init__(self, request):
        self._id = None
        self._status = ForwardingStatus.from_request(request)

    def __enter__(self):
        self._status = replace(
            self._status,
            id=self._id,
            status=ForwardingStatus.START_STATUS,
            startTime=datetime.utcnow(),
        )
        self._id = self._status.save().id

    def __exit__(self, type, exc, traceback):
        if type is None:
            self._status = replace(
                self._status,
                id=self._id,
                status=ForwardingStatus.SUCCESS_STATUS,
                endTime=datetime.utcnow(),
            )
            self._id = self._status.save().id
            return True
        else:
            self._status = replace(
                self._status,
                id=self._id,
                status=ForwardingStatus.ERROR_STATUS,
                endTime=datetime.utcnow(),
                error=exc.__str__(),
            )
            self._id = self._status.save().id
            return False
