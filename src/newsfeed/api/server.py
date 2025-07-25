# FastAPI server definition
# /ingest endpoint (Ingest raw events)
# /retrieve endpoint (Retrieve filtered events)

from fastapi import FastAPI, status
from newsfeed.ingestion.event import Event
from newsfeed.ingestion.store import store
from newsfeed.config.loader import load_keywords_config
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.utils.logging_config import setup_logging
import pprint
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Newsfeed API",
    description="Real-time newsfeed system for IT-related news aggregation",
)

@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        dict[str, str]: A simple welcome message to verify the API is reachable.
    """
    logger.info('API Root endpoint called')
    return {"message": "Hello World"}


@app.post("/ingest", status_code=status.HTTP_200_OK)
async def ingest(raw_events: list[Event]) -> dict[str, str]:
    """
    Ingest a batch of raw events, filter and sort them, and store the result in memory.
    
    Accept a single call delivering a JSON array (or stream) of event objects. 
    Each object must contain the keys:
        - id (string, unique)
        - source (string, e.g. “reddit” or “ars-technica”)
        - title (string)
        - body (string, optional)
        - published_at (ISO-8601/RFC 3339 timestamp, UTC)

    Args:
        raw_events (list[Event]): A list of raw event objects to ingest.

    Returns:
        dict[str, str]: The call returns an acknowledgment (HTTP 200 / successful exit status / ACK message).
    """
    logger.info('API /ingest endpoint called')
    logger.info(f"Number of raw events to ingest: {len(raw_events)}")
    logger.debug(f"Event details:\n{pprint.pformat(raw_events, indent=2, width=80)}")
    
    skipped_ids = []
    accepted_events = []
    batch_seen_ids_set = set()
    for event in raw_events:
        # check for duplicate ids in current batch
        if event.id in batch_seen_ids_set:
            logger.warning(f"Duplicate ID in batch: {event.id}. Skipping it.")
            skipped_ids.append(event.id)
            continue
        # check for duplicate ids in store
        if store.has_event(event.id):
            logger.warning(f"Event with id {event.id} already exists in store. Skipping it.")
            skipped_ids.append(event.id)
            continue
        accepted_events.append(event)
        print(f"Accepted event id: {event.id}")
        batch_seen_ids_set.add(event.id)

    # Load keyword configuration from YAML file
    keywords_config = load_keywords_config()
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']
    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords
    
    filtered_events_with_counts = keyword_based_filter(accepted_events, all_keywords)
    print(f"Number of filtered events: {len(filtered_events_with_counts)}")
    store.add_events(filtered_events_with_counts)
    
    return {"message": "ACK", "status": "successful exit"}


@app.get("/retrieve")
def retrieve() -> list[Event]:
    """
    Retrieve the current batch of filtered and ranked events.

    Provide a synchronous call that returns only the events your system decided to keep, in 
    the same JSON shape as above, sorted according to your default ranking (importance × recency). 
    This call must be deterministic for a given ingestion batch so our tests can assert exact
    membership and ordering.

    
    Returns:
        list[Event]: The call returns the stored events.
    """
    logger.info('API /retrieve endpoint called')

    sorted_events_with_score = store.get_sorted_events()

    logger.debug(f"Relevant events ranked by score:\n{pprint.pformat(sorted_events_with_score, indent=2, width=80)}")

    sorted_filtered_events = [event_with_score["event"] for event_with_score in sorted_events_with_score]
    logger.debug(f"Number of stored events: {store.get_event_count()}")
    logger.info(f"Number of returned events: {len(sorted_filtered_events)}")
    logger.debug(f"Returned sorted filtered events details:\n{pprint.pformat(sorted_filtered_events, indent=2, width=80)}")

    return sorted_filtered_events

