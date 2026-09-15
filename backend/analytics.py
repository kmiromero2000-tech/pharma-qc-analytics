import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from scipy.stats import f

FEATURES = [
    "api_water", "api_content", "lactose_water", "smcc_water", "starch_water",
    "tbl_av_hardness", "tbl_rsd_weight", "tbl_tensile", "dissolution_av", "impurities_total"
]

def calculate_mspc_metrics(df: pd.DataFrame, alpha=0.05):
    X = df[FEATURES].fillna(df[FEATURES].mean())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_components = min(4, X.shape[1])
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(X_scaled)
    reconstructed = pca.inverse_transform(scores)
    residuals = X_scaled - reconstructed

    variances = pca.explained_variance_
    t2 = np.sum((scores ** 2) / variances, axis=1)

    n_samples, p = X.shape
    f_crit = f.ppf(1 - alpha, n_components, n_samples - n_components)
    t2_ucl = (n_components * (n_samples - 1) / (n_samples - n_components)) * f_crit

    spe = np.sum(residuals ** 2, axis=1)
    spe_ucl = np.percentile(spe, (1 - alpha) * 100)

    return t2, t2_ucl, spe, spe_ucl

def compare_models(df: pd.DataFrame):
    X = df[FEATURES].fillna(df[FEATURES].mean())
    y = df["is_deviation"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["recall", "f1", "precision", "roc_auc"]

    rf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)

    rf_results = cross_validate(rf, X_scaled, y, cv=cv, scoring=scoring)
    lr_results = cross_validate(lr, X_scaled, y, cv=cv, scoring=scoring)

    rf.fit(X_scaled, y)
    probabilities = rf.predict_proba(X_scaled)[:, 1]

    comparison = {
        "RandomForest": {
            "recall": float(np.mean(rf_results["test_recall"])),
            "f1": float(np.mean(rf_results["test_f1"])),
            "precision": float(np.mean(rf_results["test_precision"])),
            "auc": float(np.mean(rf_results["test_roc_auc"]))
        },
        "LogisticRegression": {
            "recall": float(np.mean(lr_results["test_recall"])),
            "f1": float(np.mean(lr_results["test_f1"])),
            "precision": float(np.mean(lr_results["test_precision"])),
            "auc": float(np.mean(lr_results["test_roc_auc"]))
        }
    }

    return comparison, probabilities
