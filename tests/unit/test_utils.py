import pytest
import time
from newsfeed.utils.helpers import convert_ts_to_dt, convert_structtime_to_dt

@pytest.mark.parametrize(
    # Expected values were converted using https://www.gaijin.at/en/tools/time-converter
    "timestamp, iana_timezone, expected",
    [
        (
            1752832872,
            "America/Los_Angeles",
            (2025, 7, 18, 3, 1, 12, "America/Los_Angeles")
        ),
        (
            1752832872,
            "Europe/Zurich",
            (2025, 7, 18, 12, 1, 12, "Europe/Zurich")
        ),
        (
            1752832872,
            "Europe/London",
            (2025, 7, 18, 11, 1, 12, "Europe/London")
        ),
        (
            1767225600,
            "Europe/Zurich",
            (2026, 1, 1, 1, 0, 0, "Europe/Zurich")
        ),
        (
            1752832872,
            "UTC",
            (2025, 7, 18, 10, 1, 12, "UTC")
        ),
        # Test default parameter (should default to UTC)
        (
            1752832872,
            None,  # No timezone specified - should use default
            (2025, 7, 18, 10, 1, 12, "UTC")
        ),
    ]
)
def test_convert_ts_to_dt(timestamp, iana_timezone, expected):
    """
    Test the convert_ts_to_dt function to ensure it correctly converts
    UNIX timestamps to timezone-aware datetime objects.
    """
    if iana_timezone is None:
        # Test default parameter behavior
        result = convert_ts_to_dt(timestamp=timestamp)
    else:
        result = convert_ts_to_dt(timestamp=timestamp, iana_timezone=iana_timezone)
    assert (
        result.year,
        result.month,
        result.day,
        result.hour,
        result.minute,
        result.second,
        result.tzinfo.key,
    ) == expected


def test_convert_structtime_to_dt_default_utc():
    """
    Test that convert_structtime_to_dt defaults to UTC when no timezone is specified.
    This ensures RSS feed dates are timezone-consistent with ranking calculations.
    """
    struct_time = time.struct_time((2025, 7, 18, 10, 1, 12, 0, 0, 0))
    result = convert_structtime_to_dt(struct_time)  # No timezone parameter
    
    # Should default to UTC
    expected = (2025, 7, 18, 10, 1, 12, "UTC")
    actual = (
        result.year,
        result.month,
        result.day,
        result.hour,
        result.minute,
        result.second,
        result.tzinfo.key,
    )
    assert actual == expected

