from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import joblib
import shap
import numpy as np

MODEL_PATH     = os.path.join(os.path.dirname(__file__), 'fighter_model.pkl')
EXPLAINER_PATH = os.path.join(os.path.dirname(__file__), 'shap_explainer.pkl')

_explainer = None


FEATURE_COLS = [
    "reach_diff",
    "win_rate_diff",
    "sig_str_acc_diff",
    "sig_str_def_diff",
    "td_acc_diff",
    "td_def_diff",
    "finish_rate_diff",
    "age_diff",
    "streak_diff",
    "experience_diff",
    "form_diff",
]

def build_and_save_explainer():
    """
    Build the SHAP TreeExplainer from the trained model and save it.
    Run This once after training, not on every prediction
    """

    boundle = joblib.load(MODEL_PATH)
    model = boundle["model"]

    explainer = shap.TreeExplainer(model)
    joblib.dump(explainer, EXPLAINER_PATH)
    print(f"Explainer saved to {EXPLAINER_PATH}")

def load_explainer():
    global _explainer
    if _explainer is None:
        _explainer = joblib.load(EXPLAINER_PATH)
    return _explainer

def explain_prediction(feature_vector: np.ndarray) -> list[dict]:
    """
    Given a feature vector (1 x n_features), return a list of
    {feature, shap_value, direction} dicts sorted by absolute value impact.

    feature_vector already imputed (no NaNs)
    """
    explainer = load_explainer()
    shap_values = explainer.shap_values(feature_vector)

    if isinstance(shap_values, list):
        values = shap_values[1][0]
    else:
        values = shap_values[0, :, 1]

    results = []

    for feature, value in zip(FEATURE_COLS, values):
        results.append({
            "feature": feature,
            "shap_value": round(float(value), 4),
            "direction": "favors_a" if value > 0 else "favors_b",
        })

    results.sort(key=lambda x: abs(x["shap_value"]), reverse = True)
    return results

if __name__ == "__main__":
    build_and_save_explainer()
    print("Testing explainer...")


    test_vector = np.zeros((1, len(FEATURE_COLS)))
    test_vector[0][1] = 0.2 # win_rate_dif slightly positive
    test_vector[0][0] = 5.0 # postive reach_diff

    explanation = explain_prediction(test_vector)
    for e in explanation:
        print(f"  {e['feature']:<22} {e['shap_value']:+.4f}  ({e['direction']})")
