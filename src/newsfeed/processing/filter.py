# Filtering logic

from newsfeed.ingestion.event import Event
from collections import Counter
import re 


def keyword_based_filter(all_events : list[Event], keywords : list[str]) -> list[dict[str, object]]:
    """Filter events based on presence of specified keywords in title or body.

    Args:
        all_events (list[Event]):  The list of Event instances to be filtered.
        keywords (list[str]):A list of target keywords used for filtering.

    Returns:
        list[Event]: A list of dictionaries for events whose title or body contains at least one keyword.
            - 'event' (Event): The matching Event object.
            - 'kw_counts_in_title' (dict[str, int]): Keyword counts found in the title.
            - 'kw_counts_in_body' (dict[str, int]): Keyword counts found in the body.
    """
    keywords_lower = [keyword.lower() for keyword in keywords]
    keyword_set = set(keywords_lower) # store keywords in a set for fast O(1) lookup
    filtered_events_with_counts = []
    for event in all_events:
        kw_counts_in_title, kw_counts_in_body = {}, {}
        kw_counts_in_title = count_keywords_occurences_regex(event.title, keyword_set)
        if event.body: # Check if body is not None before splitting
            kw_counts_in_body = count_keywords_occurences_regex(event.body, keyword_set)
        if kw_counts_in_title or kw_counts_in_body:
            filtered_events_with_counts.append({
                "event": event,
                "kw_counts_in_title": kw_counts_in_title,
                "kw_counts_in_body": kw_counts_in_body
            })
    return filtered_events_with_counts



def count_keywords_occurences_regex(text : str, lc_keyword_set : set[str]) -> dict[str, int]:
    """
    Counts how many times each keyword appears in the given text.

    This function uses regular expressions to extract word tokens from the input text,
    and counts occurrences of words that match any in the given set of keywords.
    Matching is case-insensitive.

    Args:
        text (str): The input text to search through.
        lc_keyword_set (set[str]): A set of lowercase keywords to count in the text.

    Returns:
        dict[str, int]: A dictionary where keys are the matched keywords and values are their counts.
    """
    words = regex_word_extractor(text.lower())
    matching_words = [word for word in words if word in lc_keyword_set] # only keep words matching keywords
    matching_words_counts = Counter(matching_words) # count occurences of keywords in text
    return dict(matching_words_counts)


# use a regular expression to extract word tokens from text:
# \b = word boundary, \w+ = one or more alphanumeric characters
# define globally for performance
WORD_PATTERN = re.compile(r"\b\w+\b")

def regex_word_extractor(text : str) -> list[str]:
    extracted_words = WORD_PATTERN.findall(text)
    return extracted_words

