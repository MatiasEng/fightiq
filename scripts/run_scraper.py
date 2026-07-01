import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scraper.db import get_connection, update_fighter_stats
from scraper.fighters import scrape_all_fighters
from scraper.fights import scrape_all_fights

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    # scrape_all_fighters()
    # scrape_all_fights()

    logger = logging.getLogger(__name__)
    logger.info("Updating fighter stats from fight data...")
    conn = get_connection()
    update_fighter_stats(conn)
    conn.close()
    logger.info("Done.")
