# Aggregating logic

from newsfeed.ingestion import reddit, rss
from newsfeed.ingestion.event import Event


def fetch_and_aggregate_events(sources_config: list) -> list[Event]:
    """Fetch events from all sources in config and aggregate them.

    Args:
        sources_config (list): A list of dictionaries, each defining a source to fetch events from.

    Returns:
        list[Event]: A combined list of Event objects fetched from all specified sources.
    """
    all_events = []
    for source_config in sources_config:
        if source_config["type"] == "reddit":
            source_events = reddit.fetch(source_config)
        elif source_config["type"] == "rss":
            source_events = rss.fetch(source_config)
        else:
            source_events = []
        all_events.extend(source_events)

    return all_events