import logging

from .utils import get_page
from .parser import parse_event_fights, parse_event_list
from .db import get_connection, upsert_fight, fighters_exist

logger = logging.getLogger(__name__)

EVENTS_URL = "http://ufcstats.com/statistics/events/completed?page=all"


def scrape_event_list() -> list[dict]:
    """Scrape all completed events"""
    logger.info("Scraping event list...")
    try:
        soup = get_page(EVENTS_URL)
        events = parse_event_list(soup)
        logger.info(f"Found {len(events)} events")
        return events
    except Exception as e:
        logger.error(f"Failed to scrape event list: {e}")
        return []


def scrape_event(event: dict, conn) -> tuple[int, int]:
    """
    Scrape all fights from one event.
    Returns (success_count, skipped_count).
    """
    try:
        soup = get_page(event["url"])
        fights = parse_event_fights(soup, event)
    except Exception as e:
        logger.error(f"Failed to fetch event {event['name']}: {e}")
        return 0, 0

    success = 0
    skipped = 0

    for fight in fights:
        if not fighters_exist(conn, fight["fighter_a_id"], fight["fighter_b_id"]):
            logger.warning(f"Skipped fight {fight['id']} - fighter not in DB")
            skipped += 1
            continue

        try:
            upsert_fight(conn, fight)
            success += 1
        except Exception as e:
            logger.error(f"Failed to upsert fight {fight['id']}: {e}")
            skipped += 1

    return success, skipped


def scrape_all_fights():
    logger.info("Starting fight scrape...")
    events = scrape_event_list()

    if not events:
        logger.error("No events found, aborting.")
        return

    conn = get_connection()
    total_success = 0
    total_skipped = 0

    for i, event in enumerate(events, 1):
        logger.info(f"[{i}/{len(events)}] {event['name']} ({event['date']})")
        success, skipped = scrape_event(event, conn)
        total_success += success
        total_skipped += skipped

    conn.close()
    logger.info(f"Done: {total_success} fight saved, {total_skipped} skipped")
