# FastAPI server definition
# /ingest endpoint (Ingest raw events)
# /retrieve endpoint (Retrieve filtered events)

from fastapi import FastAPI, status
from newsfeed.ingestion.event import Event
from newsfeed.config.loader import load_keywords_config
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.processing.rank import rank_events
from newsfeed.utils.logging_config import setup_logging
import pprint
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Newsfeed API",
    description="Real-time newsfeed system for IT-related news aggregation",
)

# In-memory storage for events (cleared and overwritten on each new ingestion)
stored_events: list[Event] = []

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

    # Load keyword configuration from YAML file
    keywords_config = load_keywords_config()
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']

    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords
    
    filtered_events_with_counts = keyword_based_filter(raw_events, all_keywords)
    sorted_events_with_score = rank_events(filtered_events_with_counts, 
                                        high_priority_keywords,
                                        medium_priority_keywords,
                                        low_priority_keywords)
    logger.debug(f"Relevant events ranked by score:\n{pprint.pformat(sorted_events_with_score, indent=2, width=80)}")

    sorted_filtered_events = [event_with_score["event"] for event_with_score in sorted_events_with_score]

    stored_events.clear() # Replaces memory on each ingest
    stored_events.extend(sorted_filtered_events)
    
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
    logger.info(f"Number of stored events: {len(stored_events)}")
    logger.debug(f"Stored events details:\n{pprint.pformat(stored_events, indent=2, width=80)}")

    return stored_events

