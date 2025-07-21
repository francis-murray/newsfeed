# Filtering logic

from newsfeed.ingestion.event import Event
import string


def keyword_based_filter(all_events : list[Event], keywords : list[str]) -> list[Event]:
    """Filter events based on presence of specified keywords in title or body.

    Args:
        all_events (list[Event]):  The list of Event instances to be filtered.
        keywords (list[str]):A list of target keywords used for filtering.

    Returns:
        list[Event]: A list of Event objects whose title or body contains at least one keyword.
    """
    keywords_set = set(keyword for keyword in keywords)

    filtered_events = []
    for event in all_events:
        count_in_title = 0 
        count_in_body = 0
        for word in event.title.split():
            cleaned_word = word.strip(string.punctuation).lower()
            if cleaned_word in keywords_set:
                count_in_title += 1
        if event.body: # Check if body is not None before splitting
            for word in event.body.split():
                cleaned_word = word.strip(string.punctuation).lower()
                if cleaned_word in keywords_set:
                    count_in_body += 1
        if count_in_title or count_in_body:
            filtered_events.append(event)
    return filtered_events