# CreditPulse (ex-Fentech Lian v1)

Plateforme de Credit Risk Scoring event-driven : React → FastAPI → Kafka → Data Pipeline (Airflow+dbt) → XGBoost/SHAP → Observabilité (Prometheus/Grafana) → MLOps (MLflow/Evidently).

## Structure du projet

- `frontend/`        → Interface React (auth, dashboard, formulaire crédit, résultat SHAP)
- `backend/`          → API FastAPI (auth JWT, endpoints CRUD, producer/consumer Kafka)
- `data_pipeline/`     → Airflow + dbt + Great Expectations (feature engineering)
- `ml/`                → Entraînement XGBoost, explicabilité SHAP, monitoring Evidently, MLflow
- `observability/`     → Prometheus, Grafana, Alertmanager
- `kubernetes/`        → Manifests K8s (palier bonus)
- `docs/GUIDE_COMPLET.md` → Le guide de construction détaillé, palier par palier

## Comment démarrer

Lis `docs/GUIDE_COMPLET.md` en premier — il explique l'ordre de construction (Palier A à G).
Chaque fichier de ce scaffold contient un commentaire en en-tête qui explique ce qu'il doit faire.

## Démarrage rapide (une fois le code écrit)

```bash
cp .env.example .env
docker-compose up
```
