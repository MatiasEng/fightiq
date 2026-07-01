from pydantic import BaseModel


class PredictRequest(BaseModel):
    fighter_a: str
    fighter_b: str


class FighterStats(BaseModel):
    id: str
    name: str
    wins: int
    losses: int
    draws: int
    reach_cm: float | None
    stance: str | None
    finish_rate: float | None
    streak: int


class FighterDetail(BaseModel):
    id: str
    name: str
    wins: int
    losses: int
    draws: int
    height_cm: float | None
    reach_cm: float | None
    stance: str | None
    age: float | None
    sig_str_acc: float | None
    sig_str_def: float | None
    td_acc: float | None
    td_def: float | None
    finish_rate: float | None
    kos: int
    submissions: int
    total_fights: int
    streak: int
    last_5_wins: int


class PredictResponse(BaseModel):
    fighter_a: FighterStats
    fighter_b: FighterStats
    fighter_a_win_prob: float
    fighter_b_win_prob: float
    predicted_winner: str


class FighterSearchResult(BaseModel):
    id: str
    name: str


class FighterFight(BaseModel):
    id: str
    event: str | None
    date: str | None
    method: str | None
    method_detail: str | None
    round: int | None
    time_seconds: int | None
    opponent_id: str
    opponent_name: str
    result: str


class ErrorResponse(BaseModel):
    detail: str
