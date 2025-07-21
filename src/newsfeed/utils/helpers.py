# Helper functions

from datetime import datetime
from zoneinfo import ZoneInfo

def convert_ts_to_dt(timestamp, iana_timezone="America/Los_Angeles"):
    """
    Convert a POSIX timestamp to a timezone-aware datetime object.

    Parameters:
        timestamp (float): The POSIX timestamp (seconds since Unix epoch).
        iana_timezone (str): IANA timezone string. Defaults to "America/Los_Angeles".

    Returns:
        datetime: A timezone-aware datetime object representing the given timestamp
                  in the specified timezone.

    References:
        - https://docs.python.org/3/library/datetime.html#datetime.datetime.fromtimestamp
        - https://docs.python.org/3/library/zoneinfo.html#using-zoneinfo
    """
    return datetime.fromtimestamp(timestamp, tz=ZoneInfo(iana_timezone))
    