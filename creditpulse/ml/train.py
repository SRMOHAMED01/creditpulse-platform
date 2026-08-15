"""
train.py
Entraînement du modèle de scoring crédit.

Pipeline :
1. Génération de données synthétiques
2. Entraînement XGBoost
3. Évaluation du modèle
4. Enregistrement MLflow
5. Sauvegarde du modèle
"""

from pathlib import Path

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)

from xgboost import XGBClassifier


# ============================================================
# 1. FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "revenu_mensuel",
    "dettes_actuelles",
    "age",
    "anciennete_emploi",
    "nombre_credits_en_cours",
    "historique_paiement",
    "dti_ratio",
]


# ============================================================
# 2. GENERATE SYNTHETIC DATA
# ============================================================

def generate_synthetic_data(n_samples: int = 10_000) -> pd.DataFrame:
    """
    Génère un dataset synthétique de profils financiers.

    Plus le DTI est élevé et plus l'historique de paiement
    est mauvais, plus la probabilité de défaut augmente.
    """

    rng = np.random.default_rng(42)

    revenu_mensuel = rng.normal(
        loc=12_000,
        scale=4_000,
        size=n_samples,
    )

    revenu_mensuel = np.clip(
        revenu_mensuel,
        2_000,
        50_000,
    )

    dettes_actuelles = rng.normal(
        loc=3_500,
        scale=2_500,
        size=n_samples,
    )

    dettes_actuelles = np.clip(
        dettes_actuelles,
        0,
        30_000,
    )

    age = rng.integers(
        21,
        65,
        size=n_samples,
    )

    anciennete_emploi = rng.exponential(
        scale=5,
        size=n_samples,
    )

    anciennete_emploi = np.clip(
        anciennete_emploi,
        0,
        40,
    )

    nombre_credits_en_cours = rng.poisson(
        lam=2,
        size=n_samples,
    )

    nombre_credits_en_cours = np.clip(
        nombre_credits_en_cours,
        0,
        10,
    )

    historique_paiement = rng.beta(
        a=8,
        b=2,
        size=n_samples,
    )

    # DTI = dette / revenu
    dti_ratio = dettes_actuelles / revenu_mensuel

    # --------------------------------------------------------
    # Probabilité de défaut
    # --------------------------------------------------------

    risk_score = (
        4.0 * dti_ratio
        + 2.5 * (1 - historique_paiement)
        + 0.12 * nombre_credits_en_cours
        - 0.02 * anciennete_emploi
        - 0.005 * (age - 30)
    )

    # Transformation en probabilité entre 0 et 1
    probability_default = 1 / (
        1 + np.exp(-(
            risk_score - 1.8
        ))
    )

    defaut_paiement = rng.binomial(
        n=1,
        p=probability_default,
        size=n_samples,
    )

    df = pd.DataFrame(
        {
            "revenu_mensuel": revenu_mensuel,
            "dettes_actuelles": dettes_actuelles,
            "age": age,
            "anciennete_emploi": anciennete_emploi,
            "nombre_credits_en_cours": nombre_credits_en_cours,
            "historique_paiement": historique_paiement,
            "dti_ratio": dti_ratio,
            "defaut_paiement": defaut_paiement,
        }
    )

    return df


# ============================================================
# 3. TRAIN MODEL
# ============================================================

def train_model(df: pd.DataFrame):
    """
    Entraîne XGBoost et retourne :
    model, params, metrics
    """

    X = df[FEATURE_COLUMNS]
    y = df["defaut_paiement"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # --------------------------------------------------------
    # Gestion du déséquilibre des classes
    # --------------------------------------------------------

    negative = (y_train == 0).sum()
    positive = (y_train == 1).sum()

    scale_pos_weight = negative / positive

    model = XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    probability_default = model.predict_proba(X_test)[:, 1]

    predictions = (
        probability_default >= 0.5
    ).astype(int)

    roc_auc = roc_auc_score(
        y_test,
        probability_default,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    params = {
        "n_estimators": 500,
        "max_depth": 5,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": scale_pos_weight,
    }

    metrics = {
        "roc_auc": roc_auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

    return model, params, metrics


# ============================================================
# 4. MLFLOW
# ============================================================

def log_to_mlflow(model, params, metrics):
    """
    Enregistre le modèle, les paramètres et les métriques
    dans MLflow.
    """

    mlflow.set_experiment("creditpulse-credit-scoring")

    with mlflow.start_run():

        mlflow.log_params(params)

        mlflow.log_metrics(metrics)

        mlflow.xgboost.log_model(
            model,
            "model",
        )


# ============================================================
# 5. SAVE MODEL
# ============================================================

def save_model(
    model,
    path="model_registry/model.json",
):
    """
    Sauvegarde le modèle XGBoost localement.
    """

    model_path = Path(__file__).parent / path

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_model(
        str(model_path)
    )

    print(
        f"Model saved to: {model_path}"
    )


# ============================================================
# 6. MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CreditPulse - Model Training")
    print("=" * 60)

    print("\n[1/4] Generating synthetic data...")

    df = generate_synthetic_data(
        n_samples=10_000
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    print(
        f"Default rate: "
        f"{df['defaut_paiement'].mean():.2%}"
    )

    print("\n[2/4] Training XGBoost model...")

    model, params, metrics = train_model(df)

    print("\n[3/4] Evaluation")

    print(
        f"ROC-AUC  : {metrics['roc_auc']:.4f}"
    )

    print(
        f"Precision: {metrics['precision']:.4f}"
    )

    print(
        f"Recall   : {metrics['recall']:.4f}"
    )

    print(
        f"F1       : {metrics['f1']:.4f}"
    )

    print("\n[4/4] Saving model...")

    save_model(
        model,
        "model_registry/model.json",
    )

    print("\nLogging experiment to MLflow...")

    try:
        log_to_mlflow(
            model,
            params,
            metrics,
        )
        print("MLflow logging completed.")

    except Exception as e:
        print(
            f"MLflow logging skipped: {e}"
        )

    print("\nTraining completed successfully.")