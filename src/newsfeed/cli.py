# Command-Line Interface 
import logging
import time

import html2text

from newsfeed.config.loader import load_sources_config, load_keywords_config
from newsfeed.ingestion.store import store
from newsfeed.processing.aggregate import fetch_and_aggregate_events
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.utils.logging_config import setup_logging




setup_logging()
logger = logging.getLogger("newsfeed.cli")
html_converter = html2text.HTML2Text()
html_converter.ignore_links = True


def display_welcome():
    print("\n====================")
    print("Welcome to Newsfeed!")
    print("====================\n\n")

def display_sources(sources_config):
    print("\n=============")
    print("News sources")
    print("=============")

    for source_config in sources_config:
        # print(source_config)
        print(f"• {source_config['name']} ({source_config['type']})", end=", ")
        if source_config['type'] == 'rss' and source_config['url']:
            print(f"url: {source_config['url']}")
        if source_config['type'] == 'reddit' and source_config['subreddit_name']:
            print(f"subreddit name: r/{source_config['subreddit_name']}")
    print()


def fetch_events(sources_config):
    start_time = time.time()
    all_events = fetch_and_aggregate_events(sources_config)
    end_time = time.time()
    print(f"Time taken to fetch and aggregate events: {end_time - start_time:.3f} seconds")
    print(f"Number of events fetched: {len(all_events)}\n")
    return all_events


def filter_events(all_events, keywords_config):
    all_keywords = (
        keywords_config['high_priority_keywords'] +
        keywords_config['medium_priority_keywords'] +
        keywords_config['low_priority_keywords']
    )
    print("\nFiltering events...")
    start_time = time.time()
    filtered_events_with_counts = keyword_based_filter(all_events, all_keywords)
    end_time = time.time()
    print(f"Time taken to filter events: {end_time - start_time:.3f} seconds")
    print(f"Number of retained (filtered) events: ({len(filtered_events_with_counts)}/{len(all_events)})\n")
    return filtered_events_with_counts


def score_and_retrieve():
    # Score filtered events
    print("\nScoring and sorting items from the store and retrieving them...")
    start_time = time.time()
    sorted_events_with_score = store.get_sorted_events()
    end_time = time.time()            
    print(f"Time taken to score and sort filtered events: {end_time - start_time:.3f} seconds\n")
    return sorted_events_with_score


def display_top_events(sorted_events_with_score):
    print("\n===============================")
    print("Display top 10 events, ranked by score (importance x recency):")
    print("===============================")
    for i, event_with_score in enumerate(sorted_events_with_score[:10]):
        event = event_with_score["event"]
        total_score = event_with_score["total_score"]
        importance_score = event_with_score["importance_score"]
        recency_score = event_with_score["recency_score"]
        print(f"Rank {i+1}")
        print(f"• Title: {event.title}")
        print(f"• Source: {event.source}")
        print(f"• Published at: {event.published_at} (hours since published: {event_with_score['age_hours']:.2f})")
        if event.body:
            # Display first 200 characters of body 
            body_text = html_converter.handle(event.body).strip()
            truncated_body = body_text[:200] + "..." if len(body_text) > 200 else body_text
            print(f"• Body: {truncated_body}")
        else:
            print("• Body: None")

        print(f"\nRelevance metrics: ")
        print(f"• Score: {total_score:.3f} (importance: {importance_score:.3f} x recency: {recency_score:.3f})")
        print(f"• Keywords in title: {event_with_score['kw_counts_in_title']}")
        print(f"• Keywords in body:  {event_with_score['kw_counts_in_body']}")
        print("\n--------------------------------------------------------------------\n")


def countdown(remaining_seconds: int):
    """
    Displays a dynamic countdown timer in the terminal, updating on the same line.
    Inspired by: https://docs.vultr.com/python/examples/create-a-countdown-timer

    Args:
        remaining_seconds (int): Number of seconds to count down from.
    """
    while remaining_seconds:
        print(f"Refreshing feed in {remaining_seconds} seconds...  (Use Ctrl+c to quit)", end="\r")
        time.sleep(1)
        remaining_seconds -= 1
    print(" " * 30, end='\r')  # Clear the line after countdown


def main():
    logger.info('CLI Started')
    display_welcome()
    
    sources_config = load_sources_config()
    display_sources(sources_config)



    while(True):
        all_events = fetch_events(sources_config)
        
        keywords_config = load_keywords_config()
        filtered_events_with_counts = filter_events(all_events, keywords_config)
        
        store.add_events(filtered_events_with_counts)

        sorted_events_with_score = score_and_retrieve()

        display_top_events(sorted_events_with_score)

        countdown(60)


if __name__ == "__main__":
    main()
