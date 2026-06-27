import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def upsert_fighter(conn, fighter: dict):
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


def upsert_fight(conn, fight: dict):
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


if __name__ == "__main__":
    conn = get_connection()
    print("Connected:", conn.status)

    fake_fighter = {
        "id": "test123",
        "name": "Test Fighter",
        "height_cm": 180.0,
        "reach_cm": 185.0,
        "stance": "Orthodox",
        "dob": "1990-01-01",
        "wins": 10,
        "losses": 2,
        "draws": 0,
        "kos": 5,
        "submissions": 3,
        "sig_str_acc": 0.48,
        "sig_str_def": 0.62,
        "td_acc": 0.40,
        "td_def": 0.75,
        "avg_fight_time": 720.0,
    }

    upsert_fighter(conn, fake_fighter)
    print("Fighter inserted.")
    conn.close()
