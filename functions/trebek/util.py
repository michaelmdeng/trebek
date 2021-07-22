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

    done, pending = await asyncio.wait(
        aws, return_when=asyncio.FIRST_COMPLETED, timeout=timeout
    )

    for completed_task in done:
        task_name = completed_task.get_name()
        logging.debug("Completed task %s", task_name)
        if not predicate(completed_task):
            logging.debug("Task %s did not satisfy predicate", task_name)
            continue
        else:
            logging.debug("Task %s satisfied predicate", task_name)
            for pending_task in pending:
                logging.debug("Killing pending task %s", pending_task.get_name())
                pending_task.cancel()
            return completed_task.result()

    return await wait_until(pending, predicate, timeout=None)
