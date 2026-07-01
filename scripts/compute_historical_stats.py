import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scraper.db import get_connection


def compute_streak(prev_fights: list, fighter_id: str) -> int:
    """
    Compute current streak at the time of the fight.
    Positive = win streak, Negative = loss streak
    prev_fights is ordered by date DESC
    """

    if not prev_fights:
        return 0

    streak = 0
    first_result = prev_fights[0][0] == fighter_id

    for fight in prev_fights:
        result = fight[0] == fighter_id  # True if win

        if result == first_result:
            streak += 1 if first_result else -1
        else:
            break

    return streak


def compute_and_store():
    conn = get_connection()
    cur = conn.cursor()

    # fetch all fights in chronological order
    cur.execute("""
        SELECT id, event_date, fighter_a_id, fighter_b_id, winner_id
        FROM fights
        WHERE winner_id IS NOT NULL
        ORDER BY event_date ASC, id ASC
        """)

    fights = cur.fetchall()
    print(f"Computing historical stats for {len(fights)} fights...")

    for i, (fight_id, event_date, a_id, b_id, winner_id) in enumerate(fights):
        for fighter_id in [a_id, b_id]:
            # all previous fights before this one
            cur.execute(
                """
                SELECT winner_id, method, draws
                FROM (
                    SELECT
                        winner_id,
                        method,
                        CASE WHEN winner_id IS NULL THEN 1 ELSE 0 END AS draws
                    FROM fights
                    WHERE (fighter_a_id = %s OR fighter_b_id = %s)
                    AND event_date < %s
                    AND method NOT IN ('Overturned', 'CNC')
                    ORDER BY event_date DESC, id DESC
                ) prev
            """,
                (fighter_id, fighter_id, event_date),
            )

            prev_fights = cur.fetchall()

            wins = sum(1 for f in prev_fights if f[0] == fighter_id)
            losses = sum(1 for f in prev_fights if f[0] != fighter_id and f[2] == 0)
            draws = sum(1 for f in prev_fights if f[2] == 1)
            kos = sum(1 for f in prev_fights if f[0] == fighter_id and f[1] == "KO/TKO")
            subs = sum(1 for f in prev_fights if f[0] == fighter_id and f[1] == "SUB")
            total = len(prev_fights)

            # last 5 fights
            last5 = prev_fights[:5]
            last5_wins = sum(1 for f in last5 if f[0] == fighter_id)
            last5_losses = sum(1 for f in last5 if f[0] != fighter_id and f[2] == 0)

            streak = compute_streak(prev_fights, fighter_id)

            cur.execute(
                """
                INSERT INTO fighter_fight_stats (
                    fighter_id, fight_id, fight_date,
                    wins, losses, draws,
                    kos, submissions, total_fights,
                    last_5_wins, last_5_losses, streak
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (fighter_id, fight_id) DO UPDATE SET
                    wins         = EXCLUDED.wins,
                    losses       = EXCLUDED.losses,
                    draws        = EXCLUDED.draws,
                    kos          = EXCLUDED.kos,
                    submissions  = EXCLUDED.submissions,
                    total_fights = EXCLUDED.total_fights,
                    last_5_wins  = EXCLUDED.last_5_wins,
                    last_5_losses = EXCLUDED.last_5_losses,
                    streak       = EXCLUDED.streak
                """,
                (
                    fighter_id,
                    fight_id,
                    event_date,
                    wins,
                    losses,
                    draws,
                    kos,
                    subs,
                    total,
                    last5_wins,
                    last5_losses,
                    streak,
                ),
            )
        if i % 500 == 0 and i > 0:
            conn.commit()
            print(f"{i}/{len(fights)} processed...")

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done. Processed {len(fights)} fights")


if __name__ == "__main__":
    compute_and_store()
