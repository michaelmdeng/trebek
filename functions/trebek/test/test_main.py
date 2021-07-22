from unittest.mock import MagicMock, PropertyMock

import pytest
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequestKeyError

import main
import model
from test import test_util


class TestParseRequest:
    @pytest.fixture
    def success_request(self):
        req = MagicMock()
        type(req).form = PropertyMock(
            return_value=ImmutableMultiDict([("callFrom", "from"), ("callTo", "to")])
        )
        return req

    @pytest.fixture
    def fail_request(self):
        req = MagicMock()
        type(req).form = PropertyMock(return_value=ImmutableMultiDict([("foo", "bar")]))
        return req

    def test_succeeds_with_good_request(self, success_request):
        res = main.parse_request(success_request)
        assert isinstance(res, model.ForwardingRequest)

    def test_extract_data_from_form_data(self, success_request):
        res = main.parse_request(success_request)
        assert res.numberFrom == "from"
        assert res.numberTo == "to"

    def test_fails_with_bad_request(self, fail_request):
        with pytest.raises(BadRequestKeyError):
            main.parse_request(fail_request)


class TestGetForwardResponse:
    @pytest.mark.asyncio
    async def test_return_success(self):
        main.get_jeopardy_info_tasks = MagicMock(
            return_value=[
                test_util.async_result(None),
                test_util.async_exc(Exception("foo")),
                test_util.async_result(
                    model.JeopardyScheduleConfig(
                        name="", phoneNumber="", calendarId="", onShift=False
                    )
                ),
            ]
        )

        await main.get_forward_response(
            model.ForwardingRequest(numberFrom="", numberTo="")
        )

    async def test_return_first_successful_jeopardy_config(self):
        main.get_jeopardy_info_tasks = MagicMock(
            return_value=[
                test_util.async_result(
                    model.JeopardyScheduleConfig(
                        name="foo", phoneNumber="", calendarId="", onShift=False
                    )
                ),
                test_util.async_result(
                    model.JeopardyScheduleConfig(
                        name="bar", phoneNumber="", calendarId="", onShift=False
                    )
                ),
            ]
        )

        res = await main.get_forward_response(
            model.ForwardingRequest(numberFrom="", numberTo="")
        )
        assert res.name == "foo"

    @pytest.mark.asyncio
    async def test_raise_exception_if_no_jeopardy_config(self):
        main.get_jeopardy_info_tasks = MagicMock(
            return_value=[
                test_util.async_result(None),
                test_util.async_exc(Exception("foo")),
            ]
        )

        with pytest.raises(model.NoJeopardyChiefException):
            await main.get_forward_response(
                model.ForwardingRequest(numberFrom="", numberTo="")
            )
