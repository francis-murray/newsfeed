# Command-Line Interface 

from newsfeed.config.loader import load_sources_config, load_keywords_config
from newsfeed.processing.aggregate import fetch_and_aggregate_events
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.processing.rank import rank_events
from newsfeed.utils.logging_config import setup_logging
import logging
import time
import html2text


setup_logging()
logger = logging.getLogger("newsfeed.cli")

def main():
    logger.info('CLI Started')

    print("\n====================")
    print("Welcome to Newsfeed!")
    print("====================\n\n")


    print("\n=============")
    print("News sources")
    print("=============")

    sources_config = load_sources_config()
    for source_config in sources_config:
        print(source_config)
    print()

    # fetch and aggregate events
    start_time = time.time()
    all_events = fetch_and_aggregate_events(sources_config)
    end_time = time.time()
    print(f"Time taken to fetch and aggregate events: {end_time - start_time:.3f} seconds")
    print(f"Number of events fetched: {len(all_events)}")
    print()


    print("\nFiltering events...")
    keywords_config = load_keywords_config() # Load keyword configuration from YAML file
    high_priority_keywords = keywords_config['high_priority_keywords']
    medium_priority_keywords = keywords_config['medium_priority_keywords']
    low_priority_keywords = keywords_config['low_priority_keywords']
    
    all_keywords = high_priority_keywords + medium_priority_keywords + low_priority_keywords

    start_time = time.time()
    filtered_events_with_counts = keyword_based_filter(all_events, all_keywords)
    end_time = time.time()
    print(f"Time taken to filter events: {end_time - start_time:.3f} seconds")
    print(f"Number of retained (filtered) events: ({len(filtered_events_with_counts)}/{len(all_events)})")
    print()


    print("\nRanking filtered events with scoring...")
    sorted_events_with_score = rank_events(filtered_events_with_counts, 
                                         high_priority_keywords,
                                         medium_priority_keywords,
                                         low_priority_keywords)
    
    
    print("\n===============================")
    print("Display top 10 events, ranked by score (importance x recency):")
    print("===============================")
    for i, event_with_score in enumerate(sorted_events_with_score[:10]):
        event = event_with_score["event"]
        total_score = event_with_score["total_score"]
        importance_score = event_with_score["importance_score"]
        recency_score = event_with_score["recency_score"]
        print(f"Rank {i+1}")
        print(f"Title: {event.title}")
        print(f"Source: {event.source}")
        print(f"Published at: {event.published_at} (age_hours: {event_with_score['age_hours']:.2f})")
        print(f"Score: {total_score:.3f} (importance: {importance_score:.3f} x recency: {recency_score:.3f})")
        print(f"Keywords in title: {event_with_score['kw_counts_in_title']}")
        print(f"Keywords in body:  {event_with_score['kw_counts_in_body']}")
        # print(f"Body:\n{html2text.html2text(event.body)}")
        print("\n--------------------------------------------------------------------\n")

if __name__ == "__main__":
    main()
