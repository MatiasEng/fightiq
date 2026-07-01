import atexit
import logging
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

_browser = None
_playwright = None


def _init_browser():
    global _browser, _playwright
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.firefox.launch(
            headless=True,
        )
        atexit.register(_cleanup)
    return _browser


def _cleanup():
    global _browser, _playwright
    if _browser:
        _browser.close()
        _browser = None
    if _playwright:
        _playwright.stop()
        _playwright = None


def get_page(url: str) -> BeautifulSoup:
    logger.info(f"Fetching {url}")
    time.sleep(0.3)
    browser = _init_browser()
    page = browser.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_function(
            "document.title !== 'Loading…'", timeout=45000
        )
        page.wait_for_load_state("networkidle")
        return BeautifulSoup(page.content(), "html.parser")
    finally:
        page.close()


def extract_id_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]
