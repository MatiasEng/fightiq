from __future__ import annotations
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def validate_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is missing. "
            "Set it before starting the server. "
            "See: https://ai.google.dev/gemini-api/docs/api-key"
        )


def _build_prompt(
    fighter_a: dict,
    fighter_b: dict,
    fighter_a_win_prob: float,
    fighter_b_win_prob: float,
    predicted_winner: str,
    explanation: list[dict]
) -> str:
    shap_lines = [] 
    for e in explanation[:6]:
        feature = e["feature"].replace('_', ' ')
        value = e["shap_value"]
        direction = e["direction"]
        winner = fighter_a["name"] if direction == "favors_a" else fighter_b["name"]
        shap_lines.append(
            f"- {feature}: {value:+.4f} (favors {winner})"
        )
    shap_text = "\n".join(shap_lines)

    return f"""You are a data-driven MMA analyst explaining a machine learning model's prediction. You must base your explanation ONLY on the data provided below. Do not use any outside knowledge about these fighters.
    ## Fight
    {fighter_a["name"]} vs {fighter_b["name"]}

    ## Fighter Stats
    {fighter_a["name"]}: {fighter_a["wins"]}W-{fighter_a["losses"]}L, reach {fighter_a["reach_cm"]}cm, stance {fighter_a["stance"]}, finish rate {fighter_a["finish_rate"]:.0%}, streak {fighter_a["streak"]}
    {fighter_b["name"]}: {fighter_b["wins"]}W-{fighter_b["losses"]}L, reach {fighter_b["reach_cm"]}cm, stance {fighter_b["stance"]}, finish rate {fighter_b["finish_rate"]:.0%}, streak {fighter_b["streak"]}

    ## Model Prediction
    Predicted winner: {predicted_winner}
    {fighter_a["name"]} win probability: {fighter_a_win_prob:.0%}
    {fighter_b["name"]} win probability: {fighter_b_win_prob:.0%}

    ## Key Factors (ordered by impact, most important first)
    {shap_text}

    ## Instructions
    Write exactly 3 sentences explaining this prediction:
    - Sentence 1: state the predicted winner and probability
    - Sentence 2: explain the TOP 1-2 factors by impact from the list above (the ones listed first)
    - Sentence 3: mention 1-2 secondary factors

    Rules:
    - You MUST follow the order of the factors above — the first factor listed had the most impact
    - Translate feature names to plain English: age_diff → age advantage, sig_str_def_diff → striking defense, sig_str_acc_diff → striking accuracy, reach_diff → reach advantage, win_rate_diff → overall record, streak_diff → current momentum, td_def_diff → takedown defense, form_diff → recent form, experience_diff → UFC experience, finish_rate_diff → finishing ability
    - Do NOT mention SHAP, machine learning, or model internals
    - Do NOT add any information not present in the data above
    - Do NOT mention outside knowledge about these fighters
    """



def generate_explanation(prediction: dict) -> str:
    """
    Takes the full prediction dict (output of predict())
    and return a natural language explanation string.
    """
    try: 
        prompt = _build_prompt(
            fighter_a          = prediction["fighter_a"],
            fighter_b          = prediction["fighter_b"],
            fighter_a_win_prob = prediction["fighter_a_win_prob"],
            fighter_b_win_prob = prediction["fighter_b_win_prob"],
            predicted_winner   = prediction["predicted_winner"],
            explanation        = prediction["explanation"],
        )
        response = _get_client().models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"Explanation unavailable: {str(e)}"