# RSS ingestion logic

import requests
import feedparser
from newsfeed.ingestion.event import Event


def fetch(source_config) -> list[Event]:
    """Fetches entries from a rss feed and returns a list of Event objects."""
    response = requests.get(source_config['url'])
    parsed_feed = feedparser.parse(response.content)
    limit = source_config.get("limit", 5)

    events = []
    for entry in parsed_feed['entries'][:limit]:
        # Different RSS feeds use different keys for their article content (e.g. content, 
        # dc_content, description, ...), so try common content fields in order of preference
        content = None

        # 1. Standard <content:encoded>
        if 'content' in entry:
            content_list = entry.get('content')
            if isinstance(content_list, list) and len(content_list) > 0:
                content = content_list[0].get('value')  # using dict .get here

        # 2. <dc:content> (used by Tom's Hardware)
        if not content:
            content = entry.get('dc_content')

        # 3. <description>
        if not content:
            content = entry.get('description')

        events.append(
            Event(
                id=entry.get("id"),
                source=source_config["name"],
                title=entry.get("title"),
                body=content,
                published_at=entry.get("published")
            )
        )

    return events    