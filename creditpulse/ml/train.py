"""
train.py
Entraînement du modèle de scoring crédit - Palier A.1
"""

from pathlib import Path

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
# Configuration
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

TARGET_COLUMN = "defaut_paiement"

MODEL_PATH = Path(__file__).parent / "model_registry" / "model.json"


# ============================================================
# 1. Génération du dataset
# ============================================================

def generate_synthetic_data(
    n_samples: int = 10_000,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Génère un dataset synthétique de profils financiers.

    Colonnes :
    - revenu_mensuel
    - dettes_actuelles
    - age
    - anciennete_emploi
    - nombre_credits_en_cours
    - historique_paiement
    - dti_ratio
    - defaut_paiement
    """

    rng = np.random.default_rng(random_state)

    # Revenu mensuel en MAD
    revenu_mensuel = rng.lognormal(
        mean=np.log(12_000),
        sigma=0.45,
        size=n_samples,
    )

    revenu_mensuel = np.clip(
        revenu_mensuel,
        3_000,
        60_000,
    )

    # Dette actuelle
    dettes_actuelles = rng.lognormal(
        mean=np.log(4_000),
        sigma=0.75,
        size=n_samples,
    )

    dettes_actuelles = np.clip(
        dettes_actuelles,
        0,
        40_000,
    )

    # Age
    age = rng.normal(
        loc=40,
        scale=10,
        size=n_samples,
    )

    age = np.clip(
        age,
        18,
        75,
    )

    # Ancienneté professionnelle
    anciennete_emploi = rng.exponential(
        scale=5,
        size=n_samples,
    )

    anciennete_emploi = np.clip(
        anciennete_emploi,
        0,
        40,
    )

    # Nombre de crédits
    nombre_credits_en_cours = rng.poisson(
        lam=1.5,
        size=n_samples,
    )

    nombre_credits_en_cours = np.clip(
        nombre_credits_en_cours,
        0,
        8,
    )

    # Historique de paiement
    # 0 = très mauvais
    # 1 = excellent
    historique_paiement = rng.beta(
        a=8,
        b=2,
        size=n_samples,
    )

    # DTI = dette / revenu
    dti_ratio = dettes_actuelles / revenu_mensuel

    # --------------------------------------------------------
    # Construction d'un score de risque latent
    # --------------------------------------------------------

    risk_score = (
        3.5 * dti_ratio
        + 2.5 * (1 - historique_paiement)
        + 0.18 * nombre_credits_en_cours
        - 0.04 * anciennete_emploi
        - 0.005 * age
    )

    # Transformation en probabilité
    probability_default = 1 / (
        1 + np.exp(
            -(risk_score - 1.8)
        )
    )

    # Variable cible
    defaut_paiement = rng.binomial(
        1,
        probability_default,
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
# 2. Entraînement XGBoost
# ============================================================

def train_model(
    df: pd.DataFrame,
) -> tuple[XGBClassifier, dict]:
    """
    Entraîne le modèle XGBoost et calcule les métriques.
    """

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # Train / test stratifié
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # --------------------------------------------------------
    # XGBoost
    # --------------------------------------------------------

    model = XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )

    # Early stopping compatible avec les versions
    # récentes de XGBoost via callback si disponible.
    #
    # Pour la première version, on entraîne sans callback.
    # Nous ajouterons l'early stopping après validation
    # de la version XGBoost installée.

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    metrics = {
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
    }

    print()
    print("=" * 50)
    print("MODEL EVALUATION")
    print("=" * 50)

    for name, value in metrics.items():
        print(f"{name:12s}: {value:.4f}")

    print("=" * 50)

    return model, metrics


# ============================================================
# 3. Sauvegarde du modèle
# ============================================================

def save_model(
    model: XGBClassifier,
    path: Path = MODEL_PATH,
) -> None:
    """
    Sauvegarde le modèle XGBoost.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_model(
        str(path)
    )

    print()
    print(f"Model saved to:")
    print(path)


# ============================================================
# 4. Main
# ============================================================

def main() -> None:

    print("=" * 50)
    print("CREDITPULSE - ML TRAINING")
    print("=" * 50)

    # Dataset
    print()
    print("1. Generating synthetic dataset...")

    df = generate_synthetic_data(
        n_samples=10_000
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    print()
    print("Columns:")
    print(list(df.columns))

    print()
    print("Default distribution:")
    print(
        df[TARGET_COLUMN]
        .value_counts()
    )

    # Training
    print()
    print("2. Training XGBoost...")

    model, metrics = train_model(
        df
    )

    # Save
    print()
    print("3. Saving model...")

    save_model(
        model
    )

    print()
    print("=" * 50)
    print("TRAINING COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()