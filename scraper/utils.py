import time
import logging
import cloudscraper
from bs4 import BeautifulSoup

# 2026-06-24 10:32:01 INFO Fetching http://ufcstats.com/fighter-details/abc123
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger(__name__)


# to avoid bot detection
scraper = cloudscraper.create_scraper()


# Takes a url, waits a delay, fetches the page, returns an error if the response is not 200
# returns a BeautifulSoup object to parse
def get_page(url: str, delay: float = 1.5) -> BeautifulSoup:
    logger.info(f"fetching {url}")
    time.sleep(delay)
    response = scraper.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


# Stracts the id from a url taking the last parameter
def extract_id_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]
