"""
monitor.py — Détection de dérive avec Evidently AI (Palier D)
"""

import os
import pandas as pd
from sqlalchemy import create_engine

# Import Evidently components safely
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False

def load_reference_data() -> pd.DataFrame:
    """Loads initial training dataset baseline or generates reference data."""
    # Synthetic baseline data format matching training schema
    reference_data = {
        "revenu_mensuel": [3000, 4500, 2000, 6000, 3500],
        "dettes_actuelles": [500, 1200, 800, 1500, 300],
        "age": [25, 42, 31, 55, 29],
        "anciennete_emploi": [2, 10, 5, 20, 3],
        "nombre_credits_en_cours": [1, 2, 1, 3, 0],
        "historique_paiement": [0.95, 0.88, 0.99, 0.92, 1.0],
        "dti_ratio": [0.166, 0.266, 0.400, 0.250, 0.085]
    }
    return pd.DataFrame(reference_data)

def load_production_data() -> pd.DataFrame:
    """Reads recent production data from feature_store in PostgreSQL."""
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    try:
        engine = create_engine(db_url)
        query = "SELECT revenu_mensuel, dettes_actuelles, age, anciennete_emploi, nombre_credits_en_cours, historique_paiement, dti_ratio FROM feature_store LIMIT 1000;"
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Could not load production data from db: {e}")
        return load_reference_data()

def run_drift_report(reference_df: pd.DataFrame, production_df: pd.DataFrame) -> dict:
    """Generates Data Drift report."""
    if not EVIDENTLY_AVAILABLE:
        print("Evidently is not installed. Skipping HTML report generation.")
        return {"drift_detected": False}

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=production_df)
    
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "drift_report.html")
    report.save_html(report_path)
    print(f"Drift report saved to {report_path}")
    
    result = report.as_dict()
    dataset_drift = result.get("metrics", [{}])[0].get("result", {}).get("dataset_drift", False)
    return {"drift_detected": dataset_drift}

def should_retrain() -> bool:
    ref_df = load_reference_data()
    prod_df = load_production_data()
    report_res = run_drift_report(ref_df, prod_df)
    return report_res.get("drift_detected", False)

if __name__ == "__main__":
    retrain_needed = should_retrain()
    print(f"Should retrain model? {retrain_needed}")
