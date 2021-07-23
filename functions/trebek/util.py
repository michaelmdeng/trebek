import asyncio
import logging


async def wait_until(aws, predicate, timeout=None):
    """
    Run awaitable objects in aws concurrently and block until the first one
    that satisifies the predicate.

    aws - Non-empty iterable of awaitable objects
    predicate - Function or lambda that takes a Task as input and returns a boolean
    timeout - maximum number of seconds to wait
    """

    if not aws:
        return None

    dones, pendings = await asyncio.wait(
        aws, return_when=asyncio.FIRST_COMPLETED, timeout=timeout
    )

    for done in dones:
        logging.debug("Completed awaitable %s", done)
        if not predicate(done):
            logging.debug("Awaitable %s did not satisfy predicate", done)
            continue
        else:
            logging.debug("Awaitable %s satisfied predicate", done)
            for pending in pendings:
                logging.debug("Killing pending awaitables %s", pending)
                pending.cancel()
            return done.result()

    return await wait_until(pendings, predicate, timeout=None)
