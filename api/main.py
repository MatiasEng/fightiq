from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.schemas import (
    PredictRequest,
    PredictResponse,
    FighterSearchResult,
    FighterDetail,
    FighterFight,
)
from api.predict import (
    predict,
    search_fighters,
    get_fighter_by_id,
    get_fighter_fights,
    get_conn,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FightIQ API", description="UFC fight outcome predictor", version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fightiq-one.vercel.app", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/fighters", response_model=list[FighterSearchResult])
@limiter.limit("30/minute")
def get_fighters(request: Request, q: str = Query(..., min_length=2)):
    results = search_fighters(q)
    if not results:
        raise HTTPException(status_code=404, detail="No fighters found")
    return results


@app.get("/fighters/{fighter_id}", response_model=FighterDetail)
@limiter.limit("30/minute")
def get_fighter_detail(request: Request, fighter_id: str):
    conn = get_conn()
    try:
        f = get_fighter_by_id(conn, fighter_id)
        if not f:
            raise HTTPException(status_code=404, detail="Fighter not found")
        wins = f.get("wins") or 0
        kos = f.get("kos") or 0
        subs = f.get("submissions") or 0
        finish_rate = round((kos + subs) / wins, 4) if wins > 0 else 0.0
        return {
            "id": f["id"],
            "name": f["name"],
            "wins": f["pro_wins"] or 0,
            "losses": f["pro_losses"] or 0,
            "draws": f["pro_draws"] or 0,
            "height_cm": f.get("height_cm"),
            "reach_cm": f.get("reach_cm"),
            "stance": f.get("stance"),
            "age": f.get("age"),
            "sig_str_acc": f.get("sig_str_acc"),
            "sig_str_def": f.get("sig_str_def"),
            "td_acc": f.get("td_acc"),
            "td_def": f.get("td_def"),
            "finish_rate": finish_rate,
            "kos": kos,
            "submissions": subs,
            "total_fights": f.get("total_fights") or 0,
            "streak": f.get("streak") or 0,
            "last_5_wins": f.get("last_5_wins") or 0,
        }
    finally:
        conn.close()


@app.get("/fighters/{fighter_id}/fights", response_model=list[FighterFight])
@limiter.limit("30/minute")
def get_fighter_fights_endpoint(request: Request, fighter_id: str):
    conn = get_conn()
    try:
        f = get_fighter_by_id(conn, fighter_id)
        if not f:
            raise HTTPException(status_code=404, detail="Fighter not found")
        return get_fighter_fights(conn, fighter_id)
    finally:
        conn.close()


@app.post("/predict", response_model=PredictResponse)
@limiter.limit("10/minute")
def predict_fight(request: Request, body: PredictRequest):
    try:
        result = predict(body.fighter_a, body.fighter_b)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
