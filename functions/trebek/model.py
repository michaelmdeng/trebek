from collections import namedtuple

ForwardingInfo = namedtuple(
    "ForwardingInfo",
    [
        "name",  # name of the person to forward to
        "forwardTo",  # phone number of the person to forward to
        "onShift",  # whether the person forwarding to is on shift
    ],
)
