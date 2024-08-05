from datetime import datetime, timedelta

import pytz


def get_current_timestamp(timedelta_value: timedelta = timedelta(seconds=0)):
    """
    Use this when we need dynamic default parameters
    If you use e.g. datetime.utcnow() as a default parameter, it will be evaluated at runtime and from then on
    will be a static default value. That's probably not what you want.
    This Depends will generate a new current timestamp each time it's called
    """

    def factory() -> datetime:
        return datetime.utcnow() + timedelta_value

    return factory


def get_current_timezone_timestamp(timedelta_value: timedelta = timedelta(seconds=0)):
    def factory() -> datetime:
        return datetime.now(tz=pytz.utc) + timedelta_value

    return factory

