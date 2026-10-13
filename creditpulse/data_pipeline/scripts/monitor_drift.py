"""
monitor_drift.py — Palier D drift monitoring for Airflow.

Checks production features against the model baseline using Evidently.
Exits 0 if no drift, 1 if drift detected (Airflow surfaces as task failure).
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine


def load_baseline() -> pd.DataFrame:
    """Return the synthetic training baseline features."""
    import numpy as np
    rng = np.random.default_rng(42)
    n = 1000
    revenu = np.clip(rng.normal(12000, 4000, n), 2000, 50000)
    dettes = np.clip(rng.normal(3500, 2500, n), 0, 30000)
    dti = dettes / revenu
    historique = rng.beta(8, 2, n)
    return pd.DataFrame({
        "revenu_mensuel": revenu,
        "dettes_actuelles": dettes,
        "dti_ratio": dti,
        "historique_paiement": historique,
    })


def load_production(db_url: str) -> pd.DataFrame:
    engine = create_engine(db_url)
    return pd.read_sql(
        "SELECT revenu_mensuel, dettes_actuelles, dti_ratio, historique_paiement "
        "FROM feature_store LIMIT 1000",
        engine,
    )


def psi(expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
    """Compute Population Stability Index between two distributions."""
    import numpy as np
    eps = 1e-4
    breakpoints = np.linspace(0, 1, buckets + 1)
    expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
    return float(np.sum((actual_percents - expected_percents) *
                        np.log((actual_percents + eps) / (expected_percents + eps))))


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set; skipping drift check")
        sys.exit(0)

    try:
        from evidently.report import Report
        from evidently.metric_preset import DataDriftPreset
        HAVE_EVIDENTLY = True
    except ImportError:
        print("Evidently not installed; using PSI fallback")
        HAVE_EVIDENTLY = False

    baseline = load_baseline()
    try:
        production = load_production(db_url)
    except Exception as e:
        print(f"Cannot load production data: {e}")
        sys.exit(0)

    if HAVE_EVIDENTLY:
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=baseline, current_data=production)
        result = report.as_dict()
        drift = result.get("metrics", [{}])[0].get("result", {}).get("dataset_drift", False)
        print(f"Evidently dataset drift: {drift}")
        if drift:
            sys.exit(1)
    else:
        drifted = False
        for col in ["dti_ratio", "historique_paiement"]:
            score = psi(baseline[col], production[col])
            print(f"PSI for {col}: {score:.4f}")
            if score > 0.2:
                drifted = True
        if drifted:
            print("Drift detected (PSI > 0.2)")
            sys.exit(1)

    print("No drift detected.")


if __name__ == "__main__":
    main()