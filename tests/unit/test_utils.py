import pytest
from newsfeed.utils.helpers import convert_ts_to_dt

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
    ]
)
def test_convert_ts_to_dt(timestamp, iana_timezone, expected):
    """
    Test the convert_ts_to_dt function to ensure it correctly converts
    UNIX timestamps to timezone-aware datetime objects.
    """
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

