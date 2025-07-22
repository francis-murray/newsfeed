# Test the FastAPI app using TestClient 
# Documentation: https://fastapi.tiangolo.com/tutorial/testing/

from fastapi.testclient import TestClient
from newsfeed.api.server import app

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns Hello World message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_ingest_endpoint():
    """Test that the ingest endpoint accepts events and returns ACK."""
    unsorted_events_data = [
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
            "published_at": "2025-03-15T11:00:00Z"
        },
        {
            "id": "test003", 
            "source": "Tom's Hardware",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-02-15T11:00:00Z"
        },
        {
            "id": "test004", 
            "source": "unknown source",
            "title": "The weather is sunny",
            "body": None,
            "published_at": "2025-01-15T11:00:00Z"
        }
    ]
    response = client.post(
        "/ingest/",
        headers={"Content-Type": "application/json"},
        json=unsorted_events_data,
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "ACK",
        "status": "successful exit"
    }
    

def test_retrieve_endpoint_with_sorted_events():
    """Test the retrieve endpoint returns filtered and sorted events."""
    response = client.get("/retrieve", headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "test002", 
            "source": "reddit",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-03-15T11:00:00Z"
        },
        {
            "id": "test003", 
            "source": "Tom's Hardware",
            "title": "System outage affecting users",
            "body": None,
            "published_at": "2025-02-15T11:00:00Z"
        },
        {
            "id": "test001",
            "source": "Ars Technica",
            "title": "SharePoint vulnerability with 9.8 severity rating",
            "body": "A major vulneratibily has been detected in the system",
            "published_at": "2025-01-15T10:30:00Z"
        },
    ]