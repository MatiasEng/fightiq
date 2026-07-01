from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.impute import SimpleImputer

from model.features import load_training_data, build_features

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
MODEL_PATH = os.path.join(os.path.dirname(__file__), "fighter_model.pkl")


def train():
    print("Loading and building features...")
    raw = load_training_data()
    df = build_features(raw)

    X = df[FEATURE_COLS]
    y = df["label"]

    # impute remaining nulls with column median
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)

    # 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_imputed, y, test_size=0.2, random_state=42
    )

    print(f"Traning on {len(X_train)} rows, testing on {len(X_test)}")

    model = RandomForestClassifier(
        n_estimators=100, max_depth=8, min_samples_leaf=10,
        max_features="sqrt", random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    # evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\nAccuracy: {acc:.4f} ({acc * 100:.1f}%)")
    print(f"\nConfusion matrix:")
    print(confusion_matrix(y_test, y_pred))
    print(f"\nClassification report:")
    print(classification_report(y_test, y_pred))

    # feature importance
    importance = sorted(
        zip(FEATURE_COLS, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )

    print("\nFeature importance:")
    for feat, imp in importance:
        print(f"{feat:<22} {imp:.4f}")

    train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)
    print(f"Train accuracy: {train_acc:.4f}")
    print(f"Test accuracy:  {acc:.4f}")
    print(f"Gap: {train_acc - acc:.4f}")

    # save model + imputer
    joblib.dump({"model": model, "imputer": imputer}, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
