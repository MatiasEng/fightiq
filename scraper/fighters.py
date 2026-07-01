import logging
from typing import Any

from psycopg2.extensions import connection as PgConnection

from .utils import get_page
from .parser import parse_fighter_list, parse_fighter_detail
from .db import get_connection, get_recent_fighter_ids, upsert_fighter

logger = logging.getLogger(__name__)
BASE_URL = "http://ufcstats.com/statistics/fighters"
ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def scrape_fighter_list() -> list[dict[str, Any]]:
    """Scrape all fighter URLs from the A-Z listing pages."""

    all_fighters: list[dict[str, Any]] = []

    for letter in ALPHABET:
        url = f"{BASE_URL}?char={letter}&page=all"
        logger.info(f"Scrapping fighter list: {letter.upper()}")

        try:
            soup = get_page(url)
            fighters = parse_fighter_list(soup)
            logger.info(f"Found {len(fighters)} fighters")
            all_fighters.extend(fighters)
        except Exception as e:
            logger.error(f"Fail on letter {letter.upper()}: {e}")
            continue

        logger.info(f"Total fighters found: {len(all_fighters)}")
    return all_fighters


def scrape_fighter(fighter: dict[str, Any], conn: PgConnection) -> bool:
    """Scrape and save one fighter. Returns True on Success, False on Failure"""
    try:
        soup = get_page(fighter["url"])
        data = parse_fighter_detail(soup, fighter["id"])
        upsert_fighter(conn, data)
        return True
    except Exception as e:
        logger.error(f"Failed on {fighter['name']}: {e}")
        return False


def scrape_all_fighters():
    """Main entry point - scrapes all fighters and saves them to the DB"""

    logger.info("Starting fighters scrape")
    fighters = scrape_fighter_list()

    if not fighters:
        logger.error("No fighters found, aborting.")
        return

    conn = get_connection()
    success = 0
    failed = 0

    for i, fighter in enumerate(fighters, 1):
        logger.info(f"[{i}/{len(fighters)}] {fighter['name']}")
        if scrape_fighter(fighter, conn):
            success += 1
        else:
            failed += 1

    conn.close()
    logger.info(f"Done: {success} saved, {failed} failed ({len(fighters)} total)")
