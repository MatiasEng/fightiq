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
