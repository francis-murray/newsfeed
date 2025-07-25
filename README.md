# Newsfeed

A real-time newsfeed application that aggregates IT-related news from selected RSS feeds and Reddit subreddits. It filters and ranks the content to display the most relevant items for IT professionals, helping them quickly identify critical updates such as cybersecurity incidents, software issues, and major disruptions.

## Features

- Multi-source news ingestion (RSS feeds, Reddit subreddits)
- Keyword-based filtering for IT-relevant content
- Priority-based scoring system (high/medium/low importance keywords)
- Time-decay scoring for recency, prioritizing newer items
- REST API for automated evaluation and testing
- Command-line interface for interactive use
- Comprehensive logging and configuration management

## Prerequisites

- Python 3.12 or higher
- uv package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd newsfeed
```

2. Install dependencies using uv:
```bash
uv sync
```


## Configuration

### Environment Variables

Create a `.env` file in the project root with your Reddit API credentials:

```bash
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name
```

To get Reddit API credentials:
1. Visit https://www.reddit.com/prefs/apps
2. Create a new application
3. Copy the client ID, secret, and app name

### News Sources

The system is configured with IT-focused sources in `src/newsfeed/config/sources_config.yaml`:

```yaml
- name: "Sysadmin"
  type: "reddit"
  subreddit_name: "sysadmin"
  limit: 10

- name: "Ars Technica"
  type: "rss"
  url: "https://feeds.arstechnica.com/arstechnica/index"
  limit: 10

- name: "Tom's Hardware"
  type: "rss"
  url: "https://www.tomshardware.com/feeds.xml"
  limit: 10
```

You can modify this file to add or remove sources as needed.

### Keywords

The filtering system uses keywords in `src/newsfeed/config/keywords_config.yaml` to identify IT-relevant content:

```yaml
high_priority_keywords:
  - "outage"
  - "breach" 
  - "critical"
  - "ransomware"
  # ... and more critical incident keywords

medium_priority_keywords:
  - "patch"
  - "security"
  - "alert"
  - "maintenance"
  # ... and more operational keywords

low_priority_keywords:
  - "announcement"
  - "feature"
  - "release"
  # ... and more general information keywords
```

You can modify this file to add or remove keywords for each category as needed to customize filtering for your specific IT environment.


## Usage

### Command Line Interface

Run the CLI to fetch, filter, and display ranked IT news:
```bash
# Option 1: Run using uv (no need to activate venv manually)
PYTHONPATH=src uv run python -m newsfeed.cli
```

or
```bash
# Option 2: Activate the virtual environment and run directly (classic approach)
source .venv/bin/activate
PYTHONPATH=src python src/newsfeed/cli.py
```

This will:
1. Load configured news sources
2. Fetch events from all sources
3. Filter events using IT-relevant keywords
4. Rank events by importance and recency
5. Display the top 10 most relevant events

### REST API (Automated Evaluation Interface)

Start the FastAPI server:


```bash
# Option 1: Run using uv
PYTHONPATH=src uv run fastapi dev src/newsfeed/api/server.py
```

or
```bash
# Option 2: Activate the virtual environment and run directly
source .venv/bin/activate
PYTHONPATH=src fastapi dev src/newsfeed/api/server.py
```

The API provides the contract specified for automated evaluation:

#### `POST /ingest` endpoint
_Use: Ingest raw events_ \
Accepts a single call delivering a JSON array of event objects:
- `id` (string, unique)
- `source` (string, e.g. "reddit" or "ars-technica")
- `title` (string)
- `body` (string, optional)
- `published_at` (ISO-8601/RFC 3339 timestamp, UTC)

Returns: `{"message": "ACK", "status": "successful exit"}` on success

#### `GET /retrieve` endpoint 
_Use: Retrieve filtered events_ \
Returns: Filtered and ranked events in the same JSON format, sorted by importance × recency score.

#### Additional Endpoints 
- `GET /` - Health check
- `GET /docs` - Interactive API documentation

## Testing

Run the test suite:

```bash
PYTHONPATH=src uv run pytest
```

Run specific test categories:

```bash
# Unit tests only
PYTHONPATH=src uv run pytest tests/unit/

# Integration tests only  
PYTHONPATH=src uv run pytest tests/integration/

# End-to-end tests only
PYTHONPATH=src uv run pytest tests/e2e/
```

## Project Structure

```
newsfeed/
├── src/newsfeed/         # Main application code
│   ├── api/              # FastAPI REST API
│   ├── cli.py            # Command-line interface
│   ├── config/           # Configuration files and loaders
│   ├── ingestion/        # Data ingestion from various sources
│   ├── processing/       # Event aggregation, filtering, and ranking 
│   ├── ui/               # GUI components (placeholder)
│   └── utils/            # Logging and helper utilities
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests (placeholder)
│   └── e2e/              # End-to-end tests  (placeholder)
├── logs/                 # Application logs
└── pyproject.toml        # Project configuration and dependencies
```

## Filtering and Ranking Algorithm

The system filters IT-relevant content using keyword matching and ranks events with a combined score:

### Filtering
Events are retained if they contain one or more keywords from the configuration in either the title or body text.

### Ranking Score
Events are ranked using: **Total Score = Importance Score × Recency Score**

**Importance Score** is calculated based on keyword matches using a two-factor system:

1. **Base priority scores** for each keyword category:
   - High priority keywords: 3 points
   - Medium priority keywords: 2 points  
   - Low priority keywords: 1 point

2. **Location multipliers** based on where keywords appear:
   - Title keywords: 2x multiplier (titles are more important)
   - Body keywords: 1x multiplier (standard weight)

The final score for each keyword is: `base_score × location_multiplier`, resulting in:
- High priority keywords in title: 6 points each (3 × 2)
- Medium priority keywords in title: 4 points each (2 × 2)
- Low priority keywords in title: 2 points each (1 × 2)
- High priority keywords in body: 3 points each (3 × 1)
- Medium priority keywords in body: 2 points each (2 × 1)
- Low priority keywords in body: 1 point each (1 × 1)

**Recency Score** uses time-decay: 

Recency Score formula: `1 / (0.1 × hours_since_publication + 1)`
- Recent events receive a score close to 1.0 (maximum when `hours_since_publication = 0`)
- Scores decay gradually over time, prioritizing newer content

## Logging

The system includes comprehensive logging to monitor performance and health:
- Console output for real-time monitoring
- File logging to `logs/newsfeed.log`
- Configurable log levels in `src/newsfeed/utils/logging_config.py`
