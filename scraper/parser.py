from __future__ import annotations
import re
from .utils import extract_id_from_url


def _clean(text: str | None) -> str | None:
    """Strip whitespace and return None if the value is missing."""
    if text is None:
        return None
    text = text.strip()
    return None if text in ("--", "", "N/A") else text


def _height_to_cm(value: str | None) -> float | None:
    """Convert inch to cm"""
    if not value:
        return None
    try:
        parts = value.replace('"', "").split("'")
        feet = int(parts[0].strip())
        inches = int(parts[1].strip()) if parts[1].strip() else 0
        return round((feet * 12 + inches) * 2.54, 1)
    except Exception:
        return None


def _reach_to_cm(value: str | None) -> float | None:
    """Convert inch to cm"""
    if not value:
        return None
    try:
        inches = float(value.replace('"', "").strip())
        return round(inches * 2.54, 1)
    except Exception:
        return None


def _percent_to_float(value: str | None) -> float | None:
    """Convert inch to cm"""
    if not value:
        return None
    try:
        return round(float(value.replace("%", "").strip()) / 100, 4)
    except Exception:
        return None


def _parse_dob(value: str | None) -> str | None:
    """Convert date to posgtres DATE"""
    if not value:
        return None
    try:
        from datetime import datetime

        return datetime.strptime(value.strip().replace(",", ""), "%b %d %Y").strftime(
            "%Y-%m-%d"
        )
    except Exception:
        return None


def _parse_date(value: str | None) -> str | None:
    """Convert 'June 27, 2026' to '2026-06-27'."""
    if not value:
        return None
    try:
        from datetime import datetime

        return datetime.strptime(value.strip(), "%B %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        return None


def _time_to_seconds(value: str | None) -> int | None:
    """Convert '4:28' to 268."""
    if not value:
        return None
    try:
        parts = value.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return None


def _get_stat_map(soup) -> dict[str, str | None]:
    """
    Build a dict of {label: value} from all li.b-list__box-list-item elements.
    Works for both the bio section and the career stats section
    """

    stat_map: dict[str, str | None] = {}
    items = soup.find_all("li", class_="b-list__box-list-item")

    for item in items:
        label_tag = item.find("i")
        if not label_tag:
            continue
        label = label_tag.get_text(strip=True).rstrip(":").strip().upper()
        if not label:
            continue
        # Get the value text by removing the label text from the full text.
        # Doesn't mutate the soup.
        value = _clean(item.get_text().replace(label_tag.get_text(), "", 1).strip())
        stat_map[label] = value
    return stat_map


# -- public Functions


def parse_fighter_list(soup) -> list[dict]:
    """
    Parses the fighter list page (statistics/fighter?char=X&page=all)
    Returns a list of {id, name, url} dicts.
    """

    fighters = []
    rows = soup.find_all("tr", class_="b-statistics__table-row")
    for row in rows:
        cols = row.find_all("td", class_="b-statistics__table-col")
        if not cols:
            continue

        # first col has first name, second col has last name
        first_tag = cols[0].find("a", class_="b-link")
        last_tag = cols[1].find("a", class_="b-link")

        if not first_tag:
            continue

        url = first_tag.get("href", "").strip()
        first = _clean(first_tag.get_text())
        last = _clean(last_tag.get_text())
        name = f"{first} {last}".strip() if last else first

        # use helper to get the id
        fighter_id = extract_id_from_url(url)

        fighters.append({"id": fighter_id, "name": name, "url": url})
    return fighters


def parse_fighter_detail(soup, fighter_id: str) -> dict:
    """
    Parses an individual fighter page (fighter-details/{id}).
    Returns a dict ready to pass to upsert_fighter().
    """
    stats = _get_stat_map(soup)

    # record is in a separete span - format "10-2-0 (W-L-D)"
    record_tag = soup.find("span", class_="b-content__title-record")
    wins = losses = draws = kos = submissions = 0

    if record_tag:
        record_text = _clean(record_tag.get_text())
        if record_text:
            m = re.search(r"(\d+)\s*-\s*(\d+)\s*-\s*(\d+)", record_text)
            if m:
                wins = int(m.group(1))
                losses = int(m.group(2))
                draws = int(m.group(3))

    name_tag = soup.find("span", class_="b-content__title-highlight")
    return {
        "id": fighter_id,
        "name": _clean(name_tag.get_text()) if name_tag else None,
        "height_cm": _height_to_cm(stats.get("HEIGHT")),
        "reach_cm": _reach_to_cm(stats.get("REACH")),
        "stance": _clean(stats.get("STANCE")),
        "dob": _parse_dob(_clean(stats.get("DOB"))),
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "kos": kos,
        "submissions": submissions,
        "sig_str_acc": _percent_to_float(stats.get("STR. ACC.")),
        "sig_str_def": _percent_to_float(stats.get("STR. DEF")),
        "td_acc": _percent_to_float(stats.get("TD ACC.")),
        "td_def": _percent_to_float(stats.get("TD DEF.")),
        "avg_fight_time": None,  # calculated later from fight history
    }


def parse_event_list(soup) -> list[dict]:
    """
    Parses the completed event list page.
    Return a list of {id, name, date, url} dicts.
    """
    events = []
    rows = soup.find_all("tr", class_="b-statistics__table-row")

    for row in rows:
        # skip upcomming event
        if "b-statistics__table-row_type_first" in row.get("class", []):
            continue

        link = row.find("a", class_="b-link")
        date_tag = row.find("span", class_="b-statistics__date")

        if not link:
            continue

        url = link.get("href", "").strip()
        name = _clean(link.get_text())
        date = _clean(date_tag.get_text()) if date_tag else None

        events.append(
            {
                "id": extract_id_from_url(url),
                "name": name,
                "date": _parse_date(date),
                "url": url,
            }
        )
    return events


def parse_event_fights(soup, event: dict) -> list[dict]:
    """
    Parses an event detail page.
    Returns a list of fight dicts ready to upsert, with event metadata attached
    """

    fights = []
    rows = soup.find_all("tr", class_="b-fight-details__table-row")

    for row in rows:
        fight_url = row.get("data-link", "").strip()
        if not fight_url:
            continue

        fight_id = extract_id_from_url(fight_url)

        winner_flag = row.find("a", class_="b-flag_style_green")

        fighter_links = row.find_all("a", class_="b-link_style_black")

        if len(fighter_links) < 2:
            continue

        fighter_a_url = fighter_links[0].get("href", "").strip()
        fighter_b_url = fighter_links[1].get("href", "").strip()
        fighter_a_id = extract_id_from_url(fighter_a_url)
        fighter_b_id = extract_id_from_url(fighter_b_url)

        winner_id = fighter_a_id if winner_flag else None

        cols = row.find_all("td", class_="b-fight-details__table-col")
        if len(cols) < 10:
            continue

        weight_class = (
            _clean(cols[6].find("p").get_text().split("\n")[0])
            if cols[6].find("p")
            else None
        )
        method_texts = cols[7].find_all("p")
        method = _clean(method_texts[0].get_text()) if len(method_texts) > 0 else None
        method_detail = (
            _clean(method_texts[1].get_text()) if len(method_texts) > 1 else None
        )
        round_num = _clean(cols[8].find("p").get_text()) if cols[8].find("p") else None
        time_str = _clean(cols[9].find("p").get_text()) if cols[9].find("p") else None

        fights.append(
            {
                "id": fight_id,
                "event_id": event["id"],
                "event_name": event["name"],
                "event_date": event["date"],
                "fighter_a_id": fighter_a_id,
                "fighter_b_id": fighter_b_id,
                "winner_id": winner_id,
                "method": method,
                "method_detail": method_detail,
                "round": int(round_num) if round_num and round_num.isdigit() else None,
                "time_seconds": _time_to_seconds(time_str),
                "weight_class": weight_class,
            }
        )

    return fights
