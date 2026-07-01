from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import date

load_dotenv()


def load_training_data() -> pd.DataFrame:
    """
    Pulls fights + fighter stats from the DB and builds
    one row per fight with different features
    """
    engine = create_engine(os.getenv("DATABASE_URL"))

    query = """
        SELECT
            f.id             AS fight_id,
            f.event_date,
            f.method,
            f.weight_class,

            -- fighter A stats
            sa.wins          AS a_wins,
            sa.losses        AS a_losses,
            sa.draws         AS a_draws,
            sa.kos           AS a_kos,
            sa.submissions   AS a_submissions,
            sa.total_fights  AS a_total_fights,
            sa.last_5_wins   AS a_last5_wins,
            sa.last_5_losses AS a_last5_losses,
            sa.streak        AS a_streak,

            -- fighter B stats
            sb.wins          AS b_wins,
            sb.losses        AS b_losses,
            sb.draws         AS b_draws,
            sb.kos           AS b_kos,
            sb.submissions   AS b_submissions,
            sb.total_fights  AS b_total_fights,
            sb.last_5_wins   AS b_last5_wins,
            sb.last_5_losses AS b_last5_losses,
            sb.streak        AS b_streak,

            -- physical stats from fighters table
            fa.reach_cm      AS a_reach,
            fa.sig_str_acc   AS a_sig_str_acc,
            fa.sig_str_def   AS a_sig_str_def,
            fa.td_acc        AS a_td_acc,
            fa.td_def        AS a_td_def,
            fa.stance        AS a_stance,
            fa.dob           AS a_dob,

            fb.reach_cm      AS b_reach,
            fb.sig_str_acc   AS b_sig_str_acc,
            fb.sig_str_def   AS b_sig_str_def,
            fb.td_acc        AS b_td_acc,
            fb.td_def        AS b_td_def,
            fb.stance        AS b_stance,
            fb.dob           AS b_dob,


            -- label: 1 if A won, 0 if B won
            CASE WHEN f.winner_id = f.fighter_a_id THEN 1 ELSE 0 END AS label

        FROM fights f
        JOIN fighters fa ON fa.id = f.fighter_a_id
        JOIN fighters fb ON fb.id = f.fighter_b_id
        JOIN fighter_fight_stats sa
            ON sa.fight_id = f.id AND sa.fighter_id = f.fighter_a_id
        JOIN fighter_fight_stats sb
            ON sb.fight_id = f.id AND sb.fighter_id = f.fighter_b_id
        WHERE f.winner_id IS NOT NULL
        AND f.method NOT IN ('Overturned', 'CNC', 'DQ')
        """

    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    TAkes the raw fight dataframe and engineers differece features.
    Returns a clean dataframe ready for the model
    """
    import numpy as np

    # Swap A and B for half the rows so label isn't always 1
    rng = np.random.default_rng(seed=42)
    swap_mask = rng.random(len(df)) < 0.5

    swap_pairs = [
        ("a_wins", "b_wins"),
        ("a_losses", "b_losses"),
        ("a_draws", "b_draws"),
        ("a_kos", "b_kos"),
        ("a_submissions", "b_submissions"),
        ("a_total_fights", "b_total_fights"),
        ("a_last5_wins", "b_last5_wins"),
        ("a_last5_losses", "b_last5_losses"),
        ("a_streak", "b_streak"),
        ("a_reach", "b_reach"),
        ("a_sig_str_acc", "b_sig_str_acc"),
        ("a_sig_str_def", "b_sig_str_def"),
        ("a_td_acc", "b_td_acc"),
        ("a_td_def", "b_td_def"),
        ("a_stance", "b_stance"),
        ("a_dob", "b_dob"),
    ]

    for col_a, col_b in swap_pairs:
        df.loc[swap_mask, [col_a, col_b]] = df.loc[swap_mask, [col_b, col_a]].values

    df.loc[swap_mask, "label"] = 0

    def win_rate(wins, losses):
        total = wins + losses
        return wins / total if total > 0 else 0.0

    def finish_rate(kos, subs, wins):
        return (kos + subs) / wins if wins > 0 else 0.0

    def age_at_fight(dob, fight_date):
        if pd.isnull(dob) or pd.isnull(fight_date):
            return None
        return (fight_date - dob).days / 365.25

    df["event_date"] = pd.to_datetime(df["event_date"])
    df["a_dob"] = pd.to_datetime(df["a_dob"])
    df["b_dob"] = pd.to_datetime(df["b_dob"])

    df["a_win_rate"] = df.apply(lambda r: win_rate(r.a_wins, r.a_losses), axis=1)
    df["b_win_rate"] = df.apply(lambda r: win_rate(r.b_wins, r.b_losses), axis=1)
    df["a_finish_rate"] = df.apply(
        lambda r: finish_rate(r.a_kos, r.a_submissions, r.a_wins), axis=1
    )
    df["b_finish_rate"] = df.apply(
        lambda r: finish_rate(r.b_kos, r.b_submissions, r.b_wins), axis=1
    )

    df["a_age"] = df.apply(lambda r: age_at_fight(r.a_dob, r.event_date), axis=1)
    df["b_age"] = df.apply(lambda r: age_at_fight(r.b_dob, r.event_date), axis=1)

    # build difference features - what the model actually sees
    features = pd.DataFrame()
    features["reach_diff"] = df["a_reach"] - df["b_reach"]
    features["win_rate_diff"] = df["a_win_rate"] - df["b_win_rate"]
    features["sig_str_acc_diff"] = df["a_sig_str_acc"] - df["b_sig_str_acc"]
    features["sig_str_def_diff"] = df["a_sig_str_def"] - df["b_sig_str_def"]
    features["td_acc_diff"] = df["a_td_acc"] - df["b_td_acc"]
    features["td_def_diff"] = df["a_td_def"] - df["b_td_def"]
    features["finish_rate_diff"] = df["a_finish_rate"] - df["b_finish_rate"]
    features["age_diff"] = df["a_age"] - df["b_age"]
    features["streak_diff"] = df["a_streak"] - df["b_streak"]
    features["experience_diff"] = df["a_total_fights"] - df["b_total_fights"]
    features["form_diff"] = df["a_last5_wins"] - df["b_last5_wins"]
    features["stance_mismatch"] = (
        df["a_stance"].fillna("Unknown") != df["b_stance"].fillna("Unknown")
    ).astype(int)
    features["label"] = df["label"]

    # drop rows where too many features are missing
    features = features.dropna(thresh=6)

    return features


if __name__ == "__main__":
    print("Loading data...")
    df = load_training_data()
    print(f"Raw fights loaded: {len(df)}")

    features = build_features(df)
    print(f"Clean rows for training: {len(features)}")
    print(f"\nFeature summary:")
    print(features.describe())
    print(f"\nLabel distribution:")
    print(features["label"].value_counts())
