# Reddit ingestion logic
# Portions of this code were inspired by Archanak Kokate's blog post:
# "Scraping Reddit Data using Python and PRAW – A Beginner’s Guide"
# https://medium.com/@archanakkokate/scraping-reddit-data-using-python-and-praw-a-beginners-guide-7047962f5d29

import os
import praw
from dotenv import load_dotenv
from newsfeed.ingestion.event import Event
from newsfeed.utils import helpers

# load environment variables
load_dotenv()

reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                     user_agent=os.getenv("REDDIT_USER_AGENT"))


def fetch(source_config) -> list[Event]:
    """Fetches posts from a subreddit and returns a list of Event objects."""
    subreddit = reddit.subreddit(source_config["subreddit_name"])
    limit = source_config.get("limit", None)
    
    if limit:
        print(f"Fetching {limit} posts from {source_config['name']}...")
    else: 
        print(f"Fetching all posts from {source_config['name']}...")

    events = []
    for post in subreddit.new(limit=limit): 
        events.append(
            Event(
                id=post.id,
                source=source_config["name"],
                title=post.title,
                body=post.selftext,
                published_at=helpers.convert_ts_to_dt(post.created_utc)
            )
        )

    return events    