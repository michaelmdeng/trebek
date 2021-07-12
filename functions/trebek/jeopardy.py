"""
Helpers for working with Jeopardy shifts on a calendar.
"""


def is_jeop_chief_shift(event):
    return event["summary"] == "Jeop Chief"


def is_em_shift(event):
    return event["summary"] != "Jeop Chief"
