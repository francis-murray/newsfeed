import pytest
from newsfeed.ingestion import reddit, rss
from newsfeed.ingestion.event import Event

def test_fetch_reddit(mocker):
    # Test flow: 
    #    1. Mock Reddit Posts 
    #    2. Mock Subreddit w/ mock Posts 
    #    3. Patch Reddit client containing mock Subreddit
    #    4. Patch datetime converter

    # 1. Mock individual Reddit posts
    mock_post_1 = mocker.Mock()
    mock_post_1.id = "abc123"
    mock_post_1.title = "Test Title 1"
    mock_post_1.selftext = "Test Body 1"
    mock_post_1.created_utc = 1752832872.0

    mock_post_2 = mocker.Mock()
    mock_post_2.id = "bcd234"
    mock_post_2.title = "Test Title 2"
    mock_post_2.selftext = "Test Body 2"
    mock_post_2.created_utc = 1767225600.0

    # 2. Mock subreddit that returns those posts from .new()
    mock_subreddit = mocker.Mock()
    mock_subreddit.new.return_value = [mock_post_1, mock_post_2]

    # 3. Patch the Reddit client in reddit.py so that .subreddit() returns our mock subreddit
    mock_reddit = mocker.patch("newsfeed.ingestion.reddit.reddit")
    mock_reddit.subreddit.return_value = mock_subreddit

    # 4. Patch helpers.convert_ts_to_dt to return mock timestamps
    # Use side_effect to return different timestamps for each post,
    # since fetch() calls convert_ts_to_dt once per post inside a loop.
    mock_helpers = mocker.patch("newsfeed.ingestion.reddit.helpers")
    mock_helpers.convert_ts_to_dt.side_effect = [
        (2025, 7, 18, 12, 1, 12, "Europe/Zurich"),  # for post 1
        (2026, 1, 1, 1, 0, 0, "Europe/Zurich")      # for post 2
    ]

    source_config = {"name": "Sysadmin", "subreddit_name": "sysadmin", "limit": 2}
    events = reddit.fetch(source_config)

    
    assert len(events) == 2
    for event in events:
        assert isinstance(event, Event)
    assert events[0].id == "abc123"
    assert events[0].source == "Sysadmin"
    assert events[0].title == "Test Title 1"
    assert events[0].body == "Test Body 1"
    assert events[0].published_at == (2025, 7, 18, 12, 1, 12, "Europe/Zurich")

    assert events[1].id == "bcd234"
    assert events[1].title == "Test Title 2"
    assert events[1].body == "Test Body 2"
    assert events[1].published_at == (2026, 1, 1, 1, 0, 0, "Europe/Zurich")


def test_fetch_rss(mocker):
    # Test flow: 
    #    1. Mock RSS entries 
    #    2. Mock feedparser.parse()
    #    3. Patch requests.get() to return fake content

    # 1. Mock individual RSS entries with various content formats
    entry_1 = {
        "id": "rss123",
        "title": "RSS Title 1",
        "content": [{"value": "Content 1"}],
        "published": "2024-12-01T10:00:00Z"
    }

    entry_2 = {
        "id": "rss456",
        "title": "RSS Title 2",
        "dc_content": "Content 2",
        "published": "2025-01-15T12:30:00Z"
    }

    entry_3 = {
        "id": "rss789",
        "title": "RSS Title 3",
        "description": "Content 3",
        "published": "2025-02-20T08:15:00Z"
    }

    # 2. Patch feedparser.parse to return mock entries
    mock_feedparser = mocker.patch("newsfeed.ingestion.rss.feedparser.parse")
    mock_feedparser.return_value = {"entries": [entry_1, entry_2, entry_3]}

    # 3. Patch requests.get to simulate HTTP response
    mock_response = mocker.Mock()
    mock_response.content = b"<fake xml>"
    mocker.patch("newsfeed.ingestion.rss.requests.get", return_value=mock_response)

    # Call the fetch function with mock config
    source_config = {
        "name": "MockRSS",
        "url": "https://example.com/rss",
        "limit": 3
    }

    events = rss.fetch(source_config)

    # Assert the results
    assert len(events) == 3

    assert isinstance(events[0], Event)
    assert events[0].id == "rss123"
    assert events[0].title == "RSS Title 1"
    assert events[0].body == "Content 1"
    assert events[0].published_at == "2024-12-01T10:00:00Z"

    assert events[1].id == "rss456"
    assert events[1].body == "Content 2"

    assert events[2].id == "rss789"
    assert events[2].body == "Content 3"