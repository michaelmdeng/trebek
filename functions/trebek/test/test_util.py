import asyncio

import pytest

import util


def async_result(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


def async_exc(exc):
    f = asyncio.Future()
    f.set_exception(exc)
    return f


class TestWaitUntil:
    @pytest.mark.asyncio
    async def test_returns_none_if_no_tasks(self):
        assert (await util.wait_until([], lambda t: True) is None)

    @pytest.mark.asyncio
    async def test_returns_first_successful_task(self):
        aws = [
            async_result("foo"),
            async_exc(Exception("bar")),
            async_result("bar"),
        ]
        assert (
            await util.wait_until(
                aws, lambda t: t.exception() is None and t.result() == "bar"
            )
            == "bar"
        )

    @pytest.mark.asyncio
    async def test_returns_none_if_none_satisfy(self):
        aws = [
            async_result("foo"),
            async_exc(Exception("bar")),
            async_result("bar"),
        ]
        assert await util.wait_until(aws, lambda _: False) is None
