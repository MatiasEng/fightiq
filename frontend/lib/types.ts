export interface FighterSearchResult {
  id: string
  name: string
}

export interface FighterStats {
  id: string
  name: string
  wins: number
  losses: number
  draws: number
  reach_cm: number | null
  stance: string | null
  finish_rate: number | null
  streak: number
}

export interface FighterDetail extends FighterStats {
  height_cm: number | null
  age: number | null
  sig_str_acc: number | null
  sig_str_def: number | null
  td_acc: number | null
  td_def: number | null
  kos: number
  submissions: number
  total_fights: number
  last_5_wins: number
}

export interface FighterFight {
  id: string
  event: string | null
  date: string | null
  method: string | null
  method_detail: string | null
  round: number | null
  time_seconds: number | null
  opponent_id: string
  opponent_name: string
  result: string
}

export interface PredictResponse {
  fighter_a: FighterStats
  fighter_b: FighterStats
  fighter_a_win_prob: number
  fighter_b_win_prob: number
  predicted_winner: string
}
