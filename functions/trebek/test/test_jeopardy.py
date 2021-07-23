import asyncio
from unittest.mock import MagicMock

import pytest

import jeopardy
import model
from test import test_util


class TestJeopardyInfo:
    @pytest.fixture
    def gcal_client(self):
        client = MagicMock()
        client.get_events_async = MagicMock(
            return_value=test_util.async_result(["foo"])
        )

        return client

    @pytest.fixture
    def schedule_config(self):
        return model.ScheduleConfig(name="Test", phoneNumber="", calendarId="")

    @pytest.mark.asyncio
    async def test_detects_if_jeopardy(self, gcal_client, schedule_config):
        jeopardy.is_jeop_chief_shift = MagicMock(return_value=True)
        jeopardy.is_em_shift = MagicMock(return_value=False)

        res = await jeopardy.jeopardy_info(gcal_client, schedule_config, None)
        assert isinstance(res, model.JeopardyScheduleConfig)

    @pytest.mark.asyncio
    async def test_detects_jeopardy_and_on_shift(self, gcal_client, schedule_config):
        jeopardy.is_jeop_chief_shift = MagicMock(return_value=True)
        jeopardy.is_em_shift = MagicMock(return_value=True)

        res = await jeopardy.jeopardy_info(gcal_client, schedule_config, None)
        assert isinstance(res, model.JeopardyScheduleConfig)
        assert res.onShift

    @pytest.mark.asyncio
    async def test_detects_if_on_shift(self, gcal_client, schedule_config):
        jeopardy.is_jeop_chief_shift = MagicMock(return_value=False)
        jeopardy.is_em_shift = MagicMock(return_value=True)

        res = await jeopardy.jeopardy_info(gcal_client, schedule_config, None)
        assert res is None
