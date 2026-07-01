# Improvements in the model
[ ] Historical stats at fight time        → +2–4%
[ ] Recent form (last 5 fights)           → +1–3%
[x] Fix finish_rate (scrape KO/sub data)  → +0.5–1.5%
[ ] Add stance matchup                    → +0.5–1%
[ ] Add experience diff                   → +0.5–1%
[ ] Better parameters                     → +0–0.5



Session Summary
Core Goal: Eliminate data leakage + prepare model for production API.
Completed (Phase 1 & 2):
- fighter_fight_stats table + compute_historical_stats.py — pre-fight cumulative stats with zero leakage
- features.py — joins fighter_fight_stats instead of raw fighters for wins/losses/kos/subs/form/streak
- train.py — retrained with honest features, accuracy 65.6%, train/test gap 0.071
- Hyperparams tuned (max_depth=8, min_samples_leaf=10, max_features="sqrt")
Active Changes:
- api/main.py — FastAPI app with GET /fighters (autocomplete) and POST /predict (prediction endpoint)
- Loads model + imputer at startup, builds feature vectors matching features.py logic
Outstanding Bugs:
- sig_str_acc, sig_str_def, td_acc, td_def still leak (come from full-career fighters table) — minor, <2% impact
Next Step:
- Finalize api/main.py and run with uvicorn api.main:app --reload
