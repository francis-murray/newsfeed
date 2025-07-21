# Command-Line Interface 

from newsfeed.ingestion.sources import load_sources_config
from newsfeed.processing.aggregate import fetch_and_aggregate_events
from newsfeed.processing.filter import keyword_based_filter
from newsfeed.processing.rank import sort_events_by_date


def main():
    
    print("\n====================")
    print("Welcome to Newsfeed!")
    print("====================\n\n")


    print("\n=============")
    print("News sources")
    print("=============")

    sources_config = load_sources_config()
    print(sources_config)
    for source_config in sources_config:
        print(source_config)



    print("\n===============================")
    print("Relevant events ranked by date")
    print("===============================")

    all_events = fetch_and_aggregate_events(sources_config)

    # filter events using a keyword-based approach and rank by date
    keywords = ["outage", "breach", "vulnerability", "exploit", "incident", "security",
                "cybersecurity", "critical", "down", "downtime", "emergency", "breaking", "bug", 
                "disruption", "patch", "ransomware", "zero-day", "mitigation", "CVE"]
    
    filtered_events = keyword_based_filter(all_events, keywords)
    sorted_filtered_events = sort_events_by_date(filtered_events)

    for event in sorted_filtered_events:
        print(f"title: {event.title}")
        print(f"source: {event.source}")
        print(f"published_at: {event.published_at} (PST)")
        # print(f"body: {event.body}")
        print("----------------------------------")


if __name__ == "__main__":
    main()
