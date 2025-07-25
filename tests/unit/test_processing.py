import pytest
import logging
import pprint

from datetime import datetime
from newsfeed.ingestion.event import Event
from newsfeed.ingestion.store import store
from newsfeed.processing.aggregate import fetch_and_aggregate_events
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.config.loader import load_keywords_config
from newsfeed.processing.score import score_events

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_events_1():
    """Sample events for testing filtering functionality."""
    events = [
        Event("id1", "test", "Security breach detected", datetime(2025, 1, 1), "Critical vulnerability found"),
        Event("id2", "test", "Weather update", datetime(2025, 1, 2), "Sunny day expected"),
        Event("id3", "test", "System outage", datetime(2025, 1, 3), None),  # Test None body
        Event("id4", "test", "Regular update", datetime(2025, 1, 4), "Normal operations")
    ]
    return events

@pytest.fixture
def sample_events_2():
    """Sample events for testing ranking functionality.
    All events have the same date, but different level of priority keywords in title"""

    events = [
        Event("id1", "test", "announcement", datetime(2025, 1, 1), None), # low priority keyword
        Event("id2", "test", "WARNING", datetime(2025, 1, 1), None), # mid priority keyword
        Event("id3", "test", "Ransomware", datetime(2025, 1, 1), None),  # high priority keyword
    ]
    return events


@pytest.fixture
def sample_events_3():
    """Sample events for testing ranking functionality.
    All events have the same date and keywords, but some kewords appear in the title vs body"""

    events = [
        Event("id1", "test", "no keyword here", datetime(2025, 1, 1), "outage"), # keyword in body
        Event("id2", "test", "outage", datetime(2025, 1, 1), "no keyword here"), # keyword in title
    ]
    return events


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


def test_keyword_based_filter(sample_events_1):
    """Test that keyword_based_filter correctly filters events by keywords."""
    keywords = ["security", "breach", "outage", "vulnerability"]
    
    filtered_events_with_counts = keyword_based_filter(sample_events_1, keywords)
    
    assert len(filtered_events_with_counts) == 2  # Events id1 and id3 should match the keywords
    assert filtered_events_with_counts[0]['event'].id == "id1"  # Has "security" and "breach" in title, "vulnerability" in body
    assert filtered_events_with_counts[1]['event'].id == "id3"  # Has "outage" in title


def test_keyword_based_filter_with_config_keywords(sample_events_1):
    """Test that keyword_based_filter correctly filters events by keywords with different priority levels."""

    keywords_config = load_keywords_config()
    
    # Load keyword configuration from YAML file
    keywords_config = load_keywords_config()
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']

    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords

    filtered_events_with_counts = keyword_based_filter(sample_events_1, all_keywords)
    
    assert len(filtered_events_with_counts) == 2  # Events id1 and id3 should match the keywords
    assert filtered_events_with_counts[0]['event'].id == "id1"  # Has "security" and "breach" in title, "vulnerability" in body
    assert filtered_events_with_counts[1]['event'].id == "id3"  # Has "outage" in title


def test_rank_events_based_on_recency(sample_events_1):
    """Test that events are correctly ranked by recency."""
    keywords_config = load_keywords_config()
    
    # Load keyword configuration from YAML file
    keywords_config = load_keywords_config()
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']

    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords

    filtered_events_with_counts = keyword_based_filter(sample_events_1, all_keywords)
    
    store.add_events(filtered_events_with_counts)
    sorted_events_with_score = store.get_sorted_events()

    assert len(sorted_events_with_score) == 2  # Events id1 and id3 should match the keywords
    assert sorted_events_with_score[0]['event'].id == "id1" # High priority keyword and more recent
    assert sorted_events_with_score[1]['event'].id == "id3" # High priority keyword 


def test_rank_events_based_on_priority_kw(sample_events_2):
    """Test that events are correctly ranked by priority."""
    keywords_config = load_keywords_config()
    
    # Load keyword configuration from YAML file
    keywords_config = load_keywords_config()
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']

    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords

    filtered_events_with_counts = keyword_based_filter(sample_events_2, all_keywords)
    store.add_events(filtered_events_with_counts)
    sorted_events_with_score = store.get_sorted_events()
    
    assert len(sorted_events_with_score) == 3  # All events should match the keywords

    # the order of the events should be inverted from the original order
    assert sorted_events_with_score[0]['event'].id == "id3" # High priority keyword
    assert sorted_events_with_score[1]['event'].id == "id2" # Mid priority keyword 
    assert sorted_events_with_score[2]['event'].id == "id1" # Low priority keyword 


def test_rank_events_based_on_kw_presence_in_title_vs_body(sample_events_3):
    """Test that events are correctly ranked by keyword presence in title vs body."""
    keywords_config = load_keywords_config()
    
    # Load keyword configuration from YAML file
    keywords_config = load_keywords_config()
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']
    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords

    filtered_events_with_counts = keyword_based_filter(sample_events_3, all_keywords)
    store.add_events(filtered_events_with_counts)
    sorted_events_with_score = store.get_sorted_events()

    logger.debug(f"Event details:\n{pprint.pformat(sorted_events_with_score, indent=2, width=80)}")


    assert len(sorted_events_with_score) == 2  # Both events should match the keywords

    # the order of the events should be inverted from the original order
    assert sorted_events_with_score[0]['event'].id == "id2" # keyword in title
    assert sorted_events_with_score[1]['event'].id == "id1" # keyword in body 
