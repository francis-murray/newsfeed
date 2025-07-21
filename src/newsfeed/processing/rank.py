# Ranking logic
from newsfeed.ingestion.event import Event

def sort_events_by_date(events: list[Event]) -> list[Event]:
    """Sorts a list of Event objects by their publication date in descending order.

    Args:
        events (list[Event]): A list of Event instances to be sorted.

    Returns:
        list[Event]: The list of events sorted by 'published_at', with the most recent first.
    """
    return sorted(events, key=lambda event: event.published_at, reverse=True)