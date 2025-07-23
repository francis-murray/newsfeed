# Ranking logic
from newsfeed.ingestion.event import Event
from datetime import datetime
from zoneinfo import ZoneInfo

def rank_events(events_with_counts: list[dict[str, object]], 
                high_priority_keywords: list[str], 
                medium_priority_keywords: list[str], 
                low_priority_keywords: list[str],
                ) -> list[dict[str, object]]:

    high_set = set(keyword.lower() for keyword in high_priority_keywords)
    med_set = set(keyword.lower() for keyword in medium_priority_keywords)
    low_set = set(keyword.lower() for keyword in low_priority_keywords)

    events_with_score = []
    for event_with_counts in events_with_counts:
        # event_with_counts_example = {
        #     'event': Event(
        #         id='1m6u9sx',
        #         source='Sysadmin',
        #         title='AI can’t update user profile photo via Graph API returns 200 but nothing changes?',
        #         published_at=datetime.datetime(2025, 7, 22, 16, 57, 6, tzinfo=zoneinfo.ZoneInfo(key='UTC'),
        #         body=('We’ve been building an AI layer on top of the most widely used PSAs to help ... '
        #     ),
        #     'kw_counts_in_title': {'update': 1},
        #     'kw_counts_in_body': {'authentication': 1,'update': 1,'fix': 1}
        # }

        # print()
        # print(event_with_counts['event'].title)
        # print(f"kw_counts_in_title: {event_with_counts['kw_counts_in_title']}")
        # print(f"kw_counts_in_body: {event_with_counts['kw_counts_in_body']}")
        # print()

        # count how many keywords are in the title
        high_priority_title_counts = 0
        med_priority_title_counts = 0
        low_priority_title_counts = 0
        for kw in event_with_counts['kw_counts_in_title']:
            if kw in high_set:
                high_priority_title_counts += 1

            elif kw in med_set:
                med_priority_title_counts += 1
            elif kw in low_set: 
                low_priority_title_counts += 1


        # count how many keywords are in the body
        high_priority_body_counts = 0
        med_priority_body_counts = 0
        low_priority_body_counts = 0
        for kw in event_with_counts['kw_counts_in_body']:
            if kw in high_set:
                high_priority_body_counts += 1
            elif kw in med_set:
                med_priority_body_counts += 1
            elif kw in low_set:
                low_priority_body_counts += 1

        # print()
        # print(f"high_priority_title_counts: {high_priority_title_counts}")
        # print(f"med_priority_title_counts: {med_priority_title_counts}")
        # print(f"low_priority_title_counts: {low_priority_title_counts}")
        # print(f"high_priority_body_counts: {high_priority_body_counts}")
        # print(f"med_priority_body_counts: {med_priority_body_counts}")
        # print(f"low_priority_body_counts: {low_priority_body_counts}")


        recency_score_dict = compute_recency_score(event_with_counts['event'].published_at)
        recency_score = recency_score_dict["recency_score"]
        age_hours = recency_score_dict["age_hours"]

        importance_score = (
            5 * high_priority_title_counts +
            2 * med_priority_title_counts +
            1 * low_priority_title_counts +
            3 * high_priority_body_counts +
            1 * med_priority_body_counts +
            0.5 * low_priority_body_counts
        )

        total_score = importance_score * recency_score 

        events_with_score.append({
            "event": event_with_counts['event'], 
            "total_score": total_score ,
            "importance_score": importance_score,
            "recency_score": recency_score,
            "age_hours": age_hours,
            "kw_counts_in_title": event_with_counts['kw_counts_in_title'],
            "kw_counts_in_body": event_with_counts['kw_counts_in_body'],                
            }
        )
    sorted_events_with_score = sorted(events_with_score, key=lambda x: x["total_score"], reverse=True)
    
    return sorted_events_with_score



def compute_recency_score(published_at: datetime) -> dict[str, float]:
    """
    Compute recency score, making sure datetime is timezone-aware in UTC.
    """
    # If datetime is naive, assume it's UTC (optional fallback)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=ZoneInfo("UTC"))

    now = datetime.now(ZoneInfo("UTC"))
    age_hours = (now - published_at).total_seconds() / 3600

    # formula for calculating recency score with a slow decay.
    # a smaller coefficient yields a slower decay
    coef = 0.1
    recency_score = 1 / (coef * age_hours + 1)
    # for example, when coef is 0.1:
    # when age_hours is 0,  recency_score is 1.000
    # when age_hours is 1,  recency_score is 0.909
    # when age_hours is 2,  recency_score is 0.833
    # when age_hours is 3,  recency_score is 0.769
    # when age_hours is 6,  recency_score is 0.625
    # when age_hours is 12, recency_score is 0.455
    # when age_hours is 24, recency_score is 0.294
    # when age_hours is 48, recency_score is 0.172
    # when age_hours is 96, recency_score is 0.094

    return {
        "recency_score": recency_score,
        "age_hours": age_hours
    }
    
