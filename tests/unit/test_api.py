# Test the FastAPI app using TestClient 
# Documentation: https://fastapi.tiangolo.com/tutorial/testing/

import pytest
from fastapi.testclient import TestClient
from newsfeed.api.server import app

client = TestClient(app)

@pytest.fixture
def sample_unranked_events_data():
    """Sample events data for testing."""
    return [
        {
            "id": "test001",
            "source": "Ars Technica",
            "title": "SharePoint vulnerability with 9.8 severity rating",
            "body": "A major vulneratibily has been detected in the system",
            "published_at": "2025-01-15T10:30:00Z"
        },
        {
            "id": "test002", 
            "source": "reddit",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-07-22T11:00:00Z"
        },
        {
            "id": "test003", 
            "source": "Tom's Hardware",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-07-22T03:00:00"
        },
        {
            "id": "test004", 
            "source": "unknown source",
            "title": "The weather is sunny",
            "body": None,
            "published_at": "2025-01-15T11:00:00Z"
        }
    ]


def test_root_endpoint():
    """Test that the root endpoint returns Hello World message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_ingest_endpoint(sample_unranked_events_data):
    """Test that the ingest endpoint accepts events and returns ACK."""
    response = client.post(
        "/ingest/",
        headers={"Content-Type": "application/json"},
        json=sample_unranked_events_data,
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "ACK",
        "status": "successful exit"
    }
    

def test_retrieve_endpoint_with_sorted_events(sample_unranked_events_data):
    """Test the retrieve endpoint returns filtered and sorted events."""
    # First ingest the events
    ingest_response = client.post(
        "/ingest/",
        headers={"Content-Type": "application/json"},
        json=sample_unranked_events_data,
    )
    assert ingest_response.status_code == 200
    
    # Now retrieve and verify the sorted events
    response = client.get("/retrieve", headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "test002", 
            "source": "reddit",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-07-22T11:00:00Z"
        },
        {
            "id": "test003", 
            "source": "Tom's Hardware",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-07-22T03:00:00"
        },
        {
            "id": "test001",
            "source": "Ars Technica",
            "title": "SharePoint vulnerability with 9.8 severity rating",
            "body": "A major vulneratibily has been detected in the system",
            "published_at": "2025-01-15T10:30:00Z"
        },
    ]