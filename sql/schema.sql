-- sql/schema.sql

CREATE TABLE fighters (
    id              TEXT PRIMARY KEY,        -- ufcstats fighter ID from URL
    name            TEXT NOT NULL,
    height_cm       FLOAT,
    reach_cm        FLOAT,
    stance          TEXT,
    dob             DATE,
    wins            INT,
    losses          INT,
    draws           INT,
    kos             INT,                     -- KO/TKO wins
    submissions     INT,
    sig_str_acc     FLOAT,                   -- significant strike accuracy
    sig_str_def     FLOAT,
    td_acc          FLOAT,                   -- takedown accuracy
    td_def          FLOAT,
    avg_fight_time  FLOAT,                   -- in seconds
    scraped_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fights (
    id              TEXT PRIMARY KEY,        -- ufcstats fight ID
    event_id        TEXT,
    event_name      TEXT,
    event_date      DATE,
    fighter_a_id    TEXT REFERENCES fighters(id),
    fighter_b_id    TEXT REFERENCES fighters(id),
    winner_id       TEXT REFERENCES fighters(id),
    method          TEXT,                    -- KO, SUB, DEC, etc.
    method_detail   TEXT,                    -- e.g. "Punches", "Rear Naked Choke"
    round           INT,
    time_seconds    INT,                     -- fight ended at X seconds in the round
    weight_class    TEXT,
    scraped_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fighter_fight_stats (
    fighter_id       TEXT REFERENCES fighters(id),
    fight_id         TEXT REFERENCES fights(id),
    fight_date       DATE NOT NULL,

    wins             INT DEFAULT 0,
    losses           INT DEFAULT 0,
    draws            INT DEFAULT 0,
    kos              INT DEFAULT 0,
    submissions      INT DEFAULT 0,
    total_fights     INT DEFAULT 0,

    last_5_wins      INT DEFAULT 0,
    last_5_losses    INT DEFAULT 0,
    streak           INT DEFAULT 0, -- positive=win streak, negative=loss streak

    PRIMARY KEY (fighter_id, fight_id)
);

CREATE INDEX idx_ffs_fighter ON fighter_fight_stats(fighter_id);
CREATE INDEX idx_ffs_date ON fighter_fight_stats(fight_date);

