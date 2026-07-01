import os
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as PgConnection

load_dotenv()


def get_connection() -> PgConnection:
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def upsert_fighter(conn: PgConnection, fighter: dict[str, Any]) -> None:
    sql = """
        INSERT INTO fighters (
            id, name, height_cm, reach_cm, stance, dob,
            wins, losses, draws, kos, submissions,
            sig_str_acc, sig_str_def, td_acc, td_def, avg_fight_time
        )
        VALUES (
            %(id)s, %(name)s, %(height_cm)s, %(reach_cm)s, %(stance)s, %(dob)s,
            %(wins)s, %(losses)s, %(draws)s, %(kos)s, %(submissions)s,
            %(sig_str_acc)s, %(sig_str_def)s, %(td_acc)s, %(td_def)s, %(avg_fight_time)s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            height_cm = EXCLUDED.height_cm,
            reach_cm = EXCLUDED.reach_cm,
            stance = EXCLUDED.stance,
            dob = EXCLUDED.dob,
            wins = EXCLUDED.wins,
            losses = EXCLUDED.losses,
            draws = EXCLUDED.draws,
            kos = EXCLUDED.kos,
            submissions = EXCLUDED.submissions,
            sig_str_acc = EXCLUDED.sig_str_acc,
            sig_str_def = EXCLUDED.sig_str_def,
            td_acc = EXCLUDED.td_acc,
            td_def = EXCLUDED.td_def,
            avg_fight_time = EXCLUDED.avg_fight_time,
            scraped_at = NOW()
    """
    with conn.cursor() as cur:
        cur.execute(sql, fighter)
    conn.commit()


# Get only the fighters id from the last 7 days
# If a fighter was already scraped in that 7 days period
# it will skip it
def get_recent_fighter_ids(conn: PgConnection, days: int = 7) -> set[str]:
    sql = """
        SELECT id FROM fighters
        WHERE scraped_at >= NOW() - make_interval(days => %s)
    """
    with conn.cursor() as cur:
        cur.execute(sql, (days,))
        return {row[0] for row in cur.fetchall()}


def upsert_fight(conn: PgConnection, fight: dict[str, Any]) -> None:
    sql = """
        INSERT INTO fights (
            id, event_id, event_name, event_date,
            fighter_a_id, fighter_b_id, winner_id,
            method, method_detail, round, time_seconds, weight_class
        )
        VALUES (
            %(id)s, %(event_id)s, %(event_name)s, %(event_date)s,
            %(fighter_a_id)s, %(fighter_b_id)s, %(winner_id)s,
            %(method)s, %(method_detail)s, %(round)s, %(time_seconds)s, %(weight_class)s
        )
        ON CONFLICT (id) DO UPDATE SET
            winner_id    = EXCLUDED.winner_id,
            method       = EXCLUDED.method,
            method_detail = EXCLUDED.method_detail,
            round        = EXCLUDED.round,
            time_seconds = EXCLUDED.time_seconds,
            scraped_at   = NOW()
    """
    with conn.cursor() as cur:
        cur.execute(sql, fight)
    conn.commit()


def fighters_exist(conn, id_a: str, id_b: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM fighters WHERE id IN (%s, %s)", (id_a, id_b))
        return cur.fetchone()[0] == 2


def update_fighter_stats(conn: PgConnection) -> None:
    sql = """
        UPDATE fighters f
        SET
            kos = COALESCE((
                SELECT COUNT(*) FROM fights
                WHERE winner_id = f.id AND method = 'KO/TKO'
            ), 0),
            submissions = COALESCE((
                SELECT COUNT(*) FROM fights
                WHERE winner_id = f.id AND method = 'SUB'
            ), 0),
            avg_fight_time = COALESCE((
                SELECT AVG(time_seconds) FROM fights
                WHERE fighter_a_id = f.id OR fighter_b_id = f.id
            ), 0)
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
