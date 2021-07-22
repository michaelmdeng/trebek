import asyncio


def async_result(result):
    f = asyncio.Future()
    f.set_result(result)
    return f
