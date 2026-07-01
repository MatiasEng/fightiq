from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import joblib
import numpy as np
import psycopg2
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "fighter_model.pkl")

# load model once at startup, not at every request
_bundle = joblib.load(MODEL_PATH)
MODEL = _bundle["model"]
IMPUTER = _bundle["imputer"]


FEATURE_COLS = [
    "reach_diff",
    "win_rate_diff",
    "sig_str_acc_diff",
    "sig_str_def_diff",
    "td_acc_diff",
    "td_def_diff",
    "finish_rate_diff",
    "age_diff",
    "streak_diff",
    "experience_diff",
    "form_diff",
]


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def _parse_fighter_row(row: tuple, cols: list[str]) -> dict:
    result = dict(zip(cols, row))
    dob = result.get("dob")
    if dob:
        today = date.today()
        result["age"] = round((today - dob).days / 365.25, 1)
    else:
        result["age"] = None
    return result


def _fetch_fighter_history(conn, fighter_id: str, result: dict):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT winner_id, method
            FROM fights
            WHERE (fighter_a_id = %s OR fighter_b_id = %s)
            AND winner_id IS NOT NULL
            AND method NOT IN ('Overturned', 'CNC')
            ORDER BY event_date DESC, id DESC
        """,
            (fighter_id, fighter_id),
        )

        history = cur.fetchall()
        result["last_5_wins"] = sum(1 for h in history[:5] if h[0] == fighter_id)
        result["last_5_losses"] = sum(1 for h in history[:5] if h[0] != fighter_id)

        streak = 0
        if history:
            first_win = history[0][0] == fighter_id
            for h in history:
                is_win = h[0] == fighter_id
                if is_win == first_win:
                    streak += 1 if first_win else -1
                else:
                    break
        result["streak"] = streak
    finally:
        cur.close()


_FIGHTER_COLS = [
    "id", "name",
    "height_cm", "reach_cm",
    "sig_str_acc", "sig_str_def",
    "td_acc", "td_def",
    "stance", "dob",
    "pro_wins", "pro_losses", "pro_draws",
    "wins", "losses", "kos", "submissions", "total_fights",
]

_FIGHTER_QUERY = """
    SELECT
        f.id, f.name,
        f.height_cm, f.reach_cm,
        f.sig_str_acc, f.sig_str_def,
        f.td_acc, f.td_def,
        f.stance, f.dob,
        f.wins AS pro_wins, f.losses AS pro_losses, f.draws AS pro_draws,

        COUNT(*) FILTER (WHERE fi.winner_id = f.id) AS wins,
        COUNT(*) FILTER (
            WHERE fi.winner_id IS NOT NULL AND fi.winner_id != f.id
        ) AS losses,
        COUNT(*) FILTER (
            WHERE fi.winner_id = f.id AND fi.method = 'KO/TKO'
        ) AS kos,
        COUNT(*) FILTER (
            WHERE fi.winner_id = f.id AND fi.method = 'SUB'
        ) AS submissions,
        COUNT(fi.id) AS total_fights

    FROM fighters f
    LEFT JOIN fights fi
        ON fi.fighter_a_id = f.id OR fi.fighter_b_id = f.id
"""

_FIGHTER_GROUP = """
    GROUP BY f.id, f.name, f.height_cm, f.reach_cm, f.sig_str_acc,
             f.sig_str_def, f.td_acc, f.td_def, f.stance, f.dob,
             f.wins, f.losses, f.draws
"""


def find_fighter(conn, name: str) -> dict | None:
    cur = conn.cursor()
    try:
        words = name.strip().split()
        conditions = " AND ".join(["f.name ILIKE %s" for _ in words])
        params = [f"%{w}%" for w in words]

        cur.execute(
            _FIGHTER_QUERY
            + f"WHERE {conditions}"
            + _FIGHTER_GROUP
            + "ORDER BY COUNT(fi.id) DESC LIMIT 1",
            params,
        )

        row = cur.fetchone()
        if not row:
            return None

        result = _parse_fighter_row(row, _FIGHTER_COLS)
        _fetch_fighter_history(conn, result["id"], result)
        return result
    finally:
        cur.close()


def get_fighter_by_id(conn, fighter_id: str) -> dict | None:
    cur = conn.cursor()
    try:
        cur.execute(
            _FIGHTER_QUERY + "WHERE f.id = %s" + _FIGHTER_GROUP + "LIMIT 1",
            (fighter_id,),
        )

        row = cur.fetchone()
        if not row:
            return None

        result = _parse_fighter_row(row, _FIGHTER_COLS)
        _fetch_fighter_history(conn, result["id"], result)
        return result
    finally:
        cur.close()


def finish_rate_val(f: dict) -> float:
    wins = f.get("wins") or 0
    kos = f.get("kos") or 0
    subs = f.get("submissions") or 0
    return (kos + subs) / wins if wins > 0 else 0.0


def build_feature_vector(a: dict, b: dict) -> np.ndarray:
    def win_rate(wins, losses):
        total = (wins or 0) + (losses or 0)
        return (wins or 0) / total if total > 0 else 0.0

    def finish_rate(kos, subs, wins):
        w = wins or 0
        return (kos or 0) + (subs or 0) / w if w > 0 else 0.0

    def age(dob):
        if not dob:
            return None
        today = date.today()
        return (today - dob).days / 365.25

    def safe_diff(x, y):
        if x is None or y is None:
            return None
        return x - y

    a_win_rate = win_rate(a.get("wins"), a.get("losses"))
    b_win_rate = win_rate(b.get("wins"), b.get("losses"))
    a_finish_rate = finish_rate(a.get("kos"), a.get("submissions"), a.get("wins"))
    b_finish_rate = finish_rate(b.get("kos"), b.get("submissions"), b.get("wins"))
    a_age = age(a.get("dob"))
    b_age = age(b.get("dob"))

    vector = [
        safe_diff(a.get("reach_cm"), b.get("reach_cm")),
        safe_diff(a_win_rate, b_win_rate),
        safe_diff(a.get("sig_str_acc"), b.get("sig_str_acc")),
        safe_diff(a.get("sig_str_def"), b.get("sig_str_def")),
        safe_diff(a.get("td_acc"), b.get("td_acc")),
        safe_diff(a.get("td_def"), b.get("td_def")),
        safe_diff(a_finish_rate, b_finish_rate),
        safe_diff(a_age, b_age),
        safe_diff(a.get("streak"), b.get("streak")),
        safe_diff(a.get("total_fights"), b.get("total_fights")),
        safe_diff(a.get("last_5_wins"), b.get("last_5_wins")),
    ]

    return np.array(vector, dtype=float).reshape(1, -1)


def predict(fighter_a_name: str, fighter_b_name: str) -> dict:
    conn = get_conn()

    try:
        a = find_fighter(conn, fighter_a_name)
        if not a:
            raise ValueError(f"Fighter not found: {fighter_a_name}")

        b = find_fighter(conn, fighter_b_name)
        if not b:
            raise ValueError(f"Fighter not found: {fighter_b_name}")

        vector = build_feature_vector(a, b)
        imputed = IMPUTER.transform(vector)
        proba = MODEL.predict_proba(imputed)[0]

        a_prob = round(float(proba[1]), 4)
        b_prob = round(float(proba[0]), 4)
        return {
            "fighter_a": {
                "id": a["id"],
                "name": a["name"],
                "wins": a["pro_wins"] or 0,
                "losses": a["pro_losses"] or 0,
                "draws": a["pro_draws"] or 0,
                "reach_cm": a["reach_cm"],
                "stance": a["stance"],
                "finish_rate": round(finish_rate_val(a), 4),
                "streak": a["streak"] or 0,
            },
            "fighter_b": {
                "id": b["id"],
                "name": b["name"],
                "wins": b["pro_wins"] or 0,
                "losses": b["pro_losses"] or 0,
                "draws": b["pro_draws"] or 0,
                "reach_cm": b["reach_cm"],
                "stance": b["stance"],
                "finish_rate": round(finish_rate_val(b), 4),
                "streak": b["streak"] or 0,
            },
            "fighter_a_win_prob": a_prob,
            "fighter_b_win_prob": b_prob,
            "predicted_winner": a["name"] if a_prob > b_prob else b["name"],
        }
    finally:
        conn.close()


def get_fighter_fights(conn, fighter_id: str) -> list[dict]:
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT
                f.id,
                f.event_name,
                f.event_date,
                f.method,
                f.method_detail,
                f.round,
                f.time_seconds,
                f.winner_id,
                CASE WHEN f.fighter_a_id = %s THEN f.fighter_b_id ELSE f.fighter_a_id END AS opponent_id,
                CASE WHEN f.fighter_a_id = %s THEN fb.name ELSE fa.name END AS opponent_name
            FROM fights f
            LEFT JOIN fighters fa ON fa.id = f.fighter_a_id
            LEFT JOIN fighters fb ON fb.id = f.fighter_b_id
            WHERE (f.fighter_a_id = %s OR f.fighter_b_id = %s)
              AND f.winner_id IS NOT NULL
            ORDER BY f.event_date DESC, f.id DESC
        """,
            (fighter_id, fighter_id, fighter_id, fighter_id),
        )

        rows = cur.fetchall()
        result = []
        for row in rows:
            (
                fight_id,
                event_name,
                event_date,
                method,
                method_detail,
                round_num,
                time_sec,
                winner_id,
                opponent_id,
                opponent_name,
            ) = row
            is_win = winner_id == fighter_id
            result.append(
                {
                    "id": fight_id,
                    "event": event_name,
                    "date": event_date.isoformat() if event_date else None,
                    "method": method,
                    "method_detail": method_detail,
                    "round": round_num,
                    "time_seconds": time_sec,
                    "opponent_id": opponent_id,
                    "opponent_name": opponent_name,
                    "result": "Win" if is_win else "Loss",
                }
            )
        return result
    finally:
        cur.close()


def search_fighters(query: str) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor()
    try:
        words = query.strip().split()
        if not words:
            return []
        conditions = " AND ".join(["name ILIKE %s" for _ in words])
        params = [f"%{w}%" for w in words]
        cur.execute(
            f"""
            SELECT id, name FROM fighters
            WHERE {conditions}
            ORDER BY name ASC
            LIMIT 20
        """,
            params,
        )
        rows = cur.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]
    finally:
        cur.close()
        conn.close()
