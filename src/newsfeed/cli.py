# Command-Line Interface 
from newsfeed.ingestion.sources import load_sources_config
from newsfeed.ingestion import reddit, rss

def main():
    
    print("====================")
    print("Welcome to Newsfeed!")
    print("====================")


    print("Loading Sources config:")
    sources_config = load_sources_config()

    all_events = []
    for source_config in sources_config:
        print(source_config)
        if source_config["type"] == "reddit":
            events = reddit.fetch(source_config)
        if source_config["type"] == "rss":
            events = rss.fetch(source_config)
        all_events.extend(events)


    for event in all_events:
        print(f"id: {event.id}")
        print(f"source: {event.source}")
        print(f"title: {event.title}")
        print(f"published_at: {event.published_at}")
        # print(f"body: {event.body}")
        print("========================")
        


if __name__ == "__main__":
    main()
