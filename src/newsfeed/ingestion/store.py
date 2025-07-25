import threading
import logging
from newsfeed.config.loader import load_keywords_config
from newsfeed.processing.score import score_events
from newsfeed.ingestion.event import Event

logger = logging.getLogger(__name__)


class EventStore:
    def __init__(self):
        self.store_lock = threading.Lock()
        self.filtered_events_with_counts_dict = {}

    def add_events(self, filtered_events_with_counts: list[dict]):
        """
        Add filtered events. Existing ones with same ID will be ingored.
        """
        with self.store_lock:
            for filtered_event_with_counts in filtered_events_with_counts:
                if not self.is_valid_filtered_event_with_counts(filtered_event_with_counts):
                    raise ValueError(
                        f"Tried to add an invalid format to the store."
                    )
                event_id = filtered_event_with_counts['event'].id
                if event_id in self.filtered_events_with_counts_dict.keys():
                    logger.warning(f"Duplicate event id detected. The duplicate item will be ignored. {event_id}")
                    continue
                # use the event id as the "primary key" in my internal store dict
                self.filtered_events_with_counts_dict[event_id] = filtered_event_with_counts


    def get_sorted_events(self) -> list[dict]:
        """
        Retrieve all filtered events from the store, scored and sorted.

        This method scores each event from the store and returns a sorted 
        event list in descending order of total score.
        """
        with self.store_lock:
            keywords_config = load_keywords_config() # Load keyword configuration from YAML file
            high_priority_keywords = keywords_config['high_priority_keywords']
            medium_priority_keywords = keywords_config['medium_priority_keywords']
            low_priority_keywords = keywords_config['low_priority_keywords']
            
            events_with_score = score_events(self.filtered_events_with_counts_dict.values(), 
                                                high_priority_keywords,
                                                medium_priority_keywords,
                                                low_priority_keywords)
            
            for event_with_score in events_with_score:
                logger.debug(event_with_score['event'].id)
                logger.debug(event_with_score['total_score'])

            
            # Sort events by descending total_score. 
            # Break ties using event ID in ascending order
            sorted_events_with_score = sorted(
                events_with_score,
                key=lambda x: (-x['total_score'], x['event'].id)
            )
            return sorted_events_with_score

    def clear(self):
        """
        Clear stored events (e.g., for testing or reset).
        """
        with self.store_lock:
            self.filtered_events_with_counts_dict.clear()

    def has_event(self, event_id: str) -> bool:
        """
        Check if there exists an event with this event it in the store.
        """
        with self.store_lock:
            return event_id in self.filtered_events_with_counts_dict

    def get_event_count(self) -> int:
        """
        Return the number of stored events.
        """
        with self.store_lock:
            return len(self.filtered_events_with_counts_dict)
        

    def is_valid_filtered_event_with_counts(self, item: dict) -> bool:
        """
        Helper function to ensure we add the correct data type to the store
        """
        expected_keys = {"event", "kw_counts_in_title", "kw_counts_in_body"}
        return set(item.keys()) == expected_keys
    


# Singleton: shared, in-memory store instance accessible from any module
store = EventStore()