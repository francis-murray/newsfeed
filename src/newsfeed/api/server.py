# FastAPI server definition
# /ingest endpoint (Ingest raw events)
# /retrieve endpoint (Retrieve filtered events)

from fastapi import FastAPI, status
from newsfeed.ingestion.event import Event
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.processing.rank import sort_events_by_date

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
    keywords = ["outage", "breach", "vulnerability", "exploit", "incident", "security",
                "cybersecurity", "critical", "down", "downtime", "emergency", "breaking", "bug", 
                "disruption", "patch", "ransomware", "zero-day", "mitigation", "CVE"]
    
    filtered_events = keyword_based_filter(raw_events, keywords)
    sorted_filtered_events = sort_events_by_date(filtered_events)
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
    return stored_events

