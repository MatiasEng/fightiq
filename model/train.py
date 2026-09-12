# %%
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


import matplotlib
import shap
import matplotlib.pyplot as plt
import numpy as np

import xgboost as xgb

from model.features import load_training_data, build_features
from sklearn.model_selection import RandomizedSearchCV

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


#%%
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

    # SciKit learn Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=8, 
        min_samples_leaf=3,
        max_features="sqrt", 
        random_state=42, 
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    """
    model2 = xgb.XGBClassifier(
        n_estimators=300, 
        max_depth=4, 
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8, 
        min_child_weight=5,
        #reg_lambda=1,
        eval_matric="logloss", 
        random_state=42, 
        #early_stopping_rounds=20
    )
    #model2.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    for name, model in [("RF SciKIt", model), ("XGB", model2)]:
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:,1]

        print(name)
        print("accuracy:", accuracy_score(y_test, preds))
        # print("log_loss:", log_loss(y_test, probs))       # penalizes confident wrong predictions
        # print("auc:", roc_auc_score(y_test, probs))         # ranking quality, threshold-independent
        print(confusion_matrix(y_test, preds))
        print(classification_report(y_test, preds))
    param_dist_xgb = {
        "max_depth": [2, 3, 4],
        "learning_rate": [0.01, 0.03, 0.05],
        "min_child_weight": [3, 5, 10],
    } 
    params_dist_rf = {
        "max_depth": [4, 6, 8, None],
        "min_samples_leaf": [3, 5, 10],
        "max_features": ["sqrt", "log2", 0.5],
    }


    print("RF MODEL")
    search = RandomizedSearchCV(model, params_dist_rf, n_iter=30, scoring="neg_log_loss", cv=5, random_state=42)
    search.fit(X_train, y_train)
    print(search.best_params_, search.best_score_)

    print("XGB MODEL")
    search = RandomizedSearchCV(model2, param_dist_xgb, n_iter=30, scoring="neg_log_loss", cv=5, random_state=42)
    search.fit(X_train, y_train)
    print(search.best_params_, search.best_score_)


    best_params = search.best_params_
    best_params["n_estimators"] = 1000  # give it room to stop early
    final_model = xgb.XGBClassifier(**best_params, early_stopping_rounds=30, eval_metric="logloss", random_state=42)
    final_model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
    print(final_model.best_iteration)



    rf_final = RandomForestClassifier(
        n_estimators=100, max_depth=8, min_samples_leaf=3,   # use the search's best params, not min_samples_leaf=10
        max_features="sqrt", random_state=42, n_jobs=-1
    )
    xgb_final = xgb.XGBClassifier(
        max_depth=3, learning_rate=0.03, min_child_weight=10,
        n_estimators=300, random_state=42
    )

    rf_final.fit(X_train, y_train)
    xgb_final.fit(X_train, y_train)

    print("RF accuracy: ", accuracy_score(y_test, rf_final.predict(X_test)))
    print("XGB accuracy:", accuracy_score(y_test, xgb_final.predict(X_test)))


    print(y_test.mean())
    """
    """
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

    """
    # Shap analysis 
    shap.initjs()

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_test)
    shap_values.feature_names = [
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
    #print(shap_values)

    shap.plots.bar(shap_values[:, :, 1])
    shap.plots.beeswarm(shap_values[:, :, 1])

    mean_abs_shap_values = np.abs(shap_values.values[:, :, 1]).mean(axis=0)

    feature_names = FEATURE_COLS;
    feature_importances = zip(feature_names, mean_abs_shap_values)
    sorted_importances = sorted(feature_importances, key=lambda x: x[1], reverse=True)
    for feature, importance in sorted_importances:
        print(f"{feature}: {importance:.4f}")

    print(shap_values)


if __name__ == "__main__":
    train()

# %%
