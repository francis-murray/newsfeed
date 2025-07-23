import pytest
from datetime import datetime
from newsfeed.ingestion.event import Event
from newsfeed.processing.aggregate import fetch_and_aggregate_events
from newsfeed.processing.filter import keyword_based_filter


def test_fetch_and_aggregate_events(mocker):
    """Test that fetch_and_aggregate_events properly aggregates events from different sources."""
    # Mock reddit.fetch to return some events
    reddit_events = [
        Event("r1", "reddit", "Reddit Post 1", datetime(2025, 1, 1)),
        Event("r2", "reddit", "Reddit Post 2", datetime(2025, 1, 2))
    ]
    mock_reddit_fetch = mocker.patch("newsfeed.processing.aggregate.reddit.fetch")
    mock_reddit_fetch.return_value = reddit_events
    
    # Mock rss.fetch to return some events
    rss_events = [
        Event("rss1", "rss", "RSS Article 1", datetime(2025, 1, 3)),
    ]
    mock_rss_fetch = mocker.patch("newsfeed.processing.aggregate.rss.fetch")
    mock_rss_fetch.return_value = rss_events
    
    # Test with mixed source types
    sources_config = [
        {"type": "reddit", "name": "test_reddit"},
        {"type": "rss", "name": "test_rss"},
        {"type": "unknown", "name": "test_unknown"}  # Should be ignored
    ]
    
    result = fetch_and_aggregate_events(sources_config)
    
    assert len(result) == 3  # 2 reddit + 1 rss + 0 unknown
    assert result[0].id == "r1"
    assert result[1].id == "r2" 
    assert result[2].id == "rss1"


def test_keyword_based_filter():
    """Test that keyword_based_filter correctly filters events by keywords."""
    events = [
        Event("id1", "test", "Security breach detected", datetime(2025, 1, 1), "Critical vulnerability found"),
        Event("id2", "test", "Weather update", datetime(2025, 1, 2), "Sunny day expected"),
        Event("id3", "test", "System outage", datetime(2025, 1, 3), None),  # Test None body
        Event("id4", "test", "Regular update", datetime(2025, 1, 4), "Normal operations")
    ]
    
    keywords = ["security", "breach", "outage", "vulnerability"]
    
    filtered_events_with_counts = keyword_based_filter(events, keywords)
    
    assert len(filtered_events_with_counts) == 2  # Events id1 and id3 should match the keywords
    assert filtered_events_with_counts[0]['event'].id == "id1"  # Has "security" and "breach" in title, "vulnerability" in body
    assert filtered_events_with_counts[1]['event'].id == "id3"  # Has "outage" in title
