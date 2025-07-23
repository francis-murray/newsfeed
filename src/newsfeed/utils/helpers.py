# Helper functions

from datetime import datetime
from zoneinfo import ZoneInfo
import time

def convert_ts_to_dt(timestamp, iana_timezone="UTC"):
    """
    Convert a POSIX timestamp to a timezone-aware datetime object.

    Parameters:
        timestamp (float): The POSIX timestamp (seconds since Unix epoch).
        iana_timezone (str): IANA timezone string. Defaults to "UTC".

    Returns:
        datetime: A timezone-aware datetime object representing the given timestamp
                  in the specified timezone.

    References:
        - https://docs.python.org/3/library/datetime.html#datetime.datetime.fromtimestamp
        - https://docs.python.org/3/library/zoneinfo.html#using-zoneinfo
    """
    return datetime.fromtimestamp(timestamp, tz=ZoneInfo(iana_timezone))
    

def convert_structtime_to_dt(structtime: time.struct_time, iana_timezone="UTC"):
    """Convert a time.struct_time object to a timezone-aware datetime object.

    Args:
        structtime (time.struct_time): The struct_time to convert. 
            e.g. time.struct_time(tm_year=2025, tm_mon=7, tm_mday=21, tm_hour=16,
            tm_min=25, tm_sec=47, tm_wday=0, tm_yday=202, tm_isdst=0)
        iana_timezone (str, optional): IANA timezone string. Defaults to "UTC".

    Returns:
        datetime: A timezone-aware datetime object.

    References:
        - https://docs.python.org/3/library/datetime.html#datetime-objects
        - https://docs.python.org/3/library/zoneinfo.html#using-zoneinfo
    """
    # Extract (year, month, day, hour, minute, second) from struct_time (e.g. (2025, 7, 21, 16, 25, 47))
    date_tuple = structtime[:6]

    # Unpack date_tuple into datetime constructor (e.g. 2025-07-21 16:25:47)
    dt_no_tz = datetime(*date_tuple)

    # Attach timezone info (e.g. 2025-07-21 16:25:47+00:00 for UTC)
    dt_with_tz = dt_no_tz.replace(tzinfo=ZoneInfo(iana_timezone))
    
    return dt_with_tz
    