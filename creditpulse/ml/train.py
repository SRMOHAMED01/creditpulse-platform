import os

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


FEATURE_COLUMNS = [
    "revenu_mensuel",
    "dettes_actuelles",
    "age",
    "anciennete_emploi",
    "nombre_credits_en_cours",
    "historique_paiement",
    "dti_ratio",
]


def generate_synthetic_data(
    n_samples: int = 10_000,
    random_state: int = 42,
) -> pd.DataFrame:

    rng = np.random.default_rng(random_state)

    revenu_mensuel = rng.normal(
        loc=12000,
        scale=5000,
        size=n_samples,
    )

    revenu_mensuel = np.clip(
        revenu_mensuel,
        3000,
        50000,
    )

    dettes_actuelles = rng.normal(
        loc=4000,
        scale=3000,
        size=n_samples,
    )

    dettes_actuelles = np.clip(
        dettes_actuelles,
        0,
        30000,
    )

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
        lam=1.5,
        size=n_samples,
    )

    nombre_credits_en_cours = np.clip(
        nombre_credits_en_cours,
        0,
        8,
    )

    historique_paiement = rng.beta(
        a=8,
        b=2,
        size=n_samples,
    )

    dti_ratio = dettes_actuelles / revenu_mensuel

    # Score latent de risque.
    risk_score = (
        3.5 * dti_ratio
        + 2.5 * (1 - historique_paiement)
        + 0.15 * nombre_credits_en_cours
        - 0.03 * anciennete_emploi
        - 0.005 * age
    )

    # Transformation en probabilité.
    probability_default = 1 / (
        1 + np.exp(-risk_score + 2.5)
    )

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


def train_model(df: pd.DataFrame):

    X = df[FEATURE_COLUMNS]
    y = df["defaut_paiement"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    probabilities = model.predict_proba(X_test)[:, 1]

    predictions = (probabilities >= 0.5).astype(int)

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

    print("\nModel evaluation")
    print("----------------")
    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")

    return model, metrics


def save_model(
    model,
    path="model_registry/model.json",
):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True,
    )

    model.save_model(path)

    print(f"\nModel saved to: {path}")


if __name__ == "__main__":

    print("Generating synthetic credit data...")

    df = generate_synthetic_data(
        n_samples=10_000
    )

    print("\nDataset shape:")
    print(df.shape)

    print("\nDataset preview:")
    print(df.head())

    print("\nDefault distribution:")
    print(df["defaut_paiement"].value_counts())

    model, metrics = train_model(df)

    save_model(model)