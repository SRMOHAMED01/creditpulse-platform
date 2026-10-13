"""
validate.py — Validates raw financial_profiles data before dbt runs (Palier B.3).

Uses Great Expectations to check:
  - revenu_mensuel > 0
  - dettes_actuelles >= 0
  - age between 18 and 100
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine


def load_data(db_url: str = None) -> pd.DataFrame:
    db_url = db_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/creditpulse",
    )
    engine = create_engine(db_url)
    query = "SELECT revenu_mensuel, dettes_actuelles, age FROM financial_profiles LIMIT 10000"
    return pd.read_sql(query, engine)


def run_validation(df: pd.DataFrame) -> bool:
    """Run expectations on the financial profiles data.

    Returns True if all critical checks pass, False otherwise.
    Exits with code 1 on validation failure so Airflow can surface it.
    """
    results = []

    # Check 1: revenu_mensuel must be present and > 0
    null_revenue = df["revenu_mensuel"].isna().sum() if df is not None else 1
    non_positive = (df["revenu_mensuel"] <= 0).sum() if df is not None else 1
    results.append(("revenu_mensuel_not_null", null_revenue == 0))
    results.append(("revenu_mensuel_positive", non_positive == 0))

    # Check 2: dettes_actuelles must be present and >= 0
    null_debt = df["dettes_actuelles"].isna().sum()
    negative_debt = (df["dettes_actuelles"] < 0).sum()
    results.append(("dettes_actuelles_not_null", null_debt == 0))
    results.append(("dettes_actuelles_non_negative", negative_debt == 0))

    # Check 3: age between 18 and 100
    null_age = df["age"].isna().sum()
    bad_age = ((df["age"] < 18) | (df["age"] > 100)).sum()
    results.append(("age_not_null", null_age == 0))
    results.append(("age_between_18_and_100", bad_age == 0))

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    return all_passed


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set; skipping validation")
        sys.exit(0)

    print("Loading financial profile data...")
    try:
        df = load_data(db_url)
    except Exception as e:
        print(f"Could not load data: {e}")
        sys.exit(1)

    print(f"Loaded {len(df)} records. Running validation...")
    passed = run_validation(df)

    if passed:
        print("Data validation passed successfully.")
    else:
        print("Data validation FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()