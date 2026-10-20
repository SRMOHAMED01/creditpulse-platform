# CreditPulse

CreditPulse is a credit-risk (scoring) platform built as a full data/ML product:
React frontend, FastAPI API, PostgreSQL, and an XGBoost model with genuine
TreeSHAP explanations. Around that core it ships a complete data pipeline
(Airflow + dbt + Great Expectations), MLOps tracking and drift monitoring
(MLflow + Evidently), observability (Prometheus + Grafana + Alertmanager),
containerized infrastructure (Docker Compose), CI/CD (GitHub Actions), and
Kubernetes manifests with autoscaling.

The roadmap (`docs/GUIDE_COMPLET.md`) is organized in "paliers" (stages).
All stages A through G are implemented and pushed to `main`.

The model is trained on synthetic data. Its output demonstrates an ML product
flow and must not be used for real lending decisions.

## Architecture

```
                       ┌──────────────────────────────┐
   Browser ──────────► │  React + Vite (5173)         │
                       └──────────────┬───────────────┘
                                      │ REST (JWT)
                       ┌──────────────▼───────────────┐
                       │  FastAPI (8000)              │
                       │  /auth /credit /users /fs    │
                       │  /health /ready /metrics     │
                       └───┬──────────────────┬───────┘
            sync scoring   │                  │  async event
              ┌────────────▼──────┐   ┌───────▼─────────┐
              │ XGBoost + TreeSHAP│   │ Kafka producer  │
              │ (ml/serve.py)     │   │ credit-requests │
              └───────────────────┘   └───────┬─────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │ Kafka consumer     │
                                    │ (scoring worker)   │
                                    └─────────┬──────────┘
                                              │
   ┌──────────────────────────────────────────▼───────────────────────┐
   │ PostgreSQL: users, financial_profiles, credit_applications,      │
   │             feature_store                                         │
   └──────┬───────────────────────────────────────┬───────────────────┘
          │ hourly DAG                             │ features read back
   ┌──────▼───────┐   ┌──────────┐   ┌──────────┐  │  at scoring time
   │ Great        │──►│ dbt      │──►│feature_  │──┘
   │ Expectations │   │ run      │   │store     │
   └──────────────┘   └──────────┘   └──────────┘
          │ drift check (Evidently / PSI) ──► MLflow (training + inference logs)

   Observability: Prometheus ──► Grafana ──► Alertmanager
   Packaging: docker-compose (12 services) · CI (GitHub Actions) · Kubernetes (HPA + Ingress)
```

## Repository layout

| Path | Contents |
|---|---|
| `backend/` | FastAPI app (`app/routers`, `app/services`, `app/models`, `app/kafka`), Alembic migrations, tests |
| `frontend/` | React + Vite app (pages, components, hooks), vitest units, Playwright E2E |
| `ml/` | Training (`train.py`), serving (`serve.py`), TreeSHAP (`explain.py`), drift (`monitor.py`), model registry |
| `data_pipeline/` | Airflow DAG, dbt project, Great Expectations validation, drift script |
| `observability/` | Prometheus config + alert rules, Alertmanager, Grafana dashboard |
| `kubernetes/` | K8s manifests + kustomization + deployment guide (Palier G) |
| `.github/workflows/ci.yml` | CI: backend tests, genuine-inference tests, E2E on an isolated Compose stack |
| `docs/GUIDE_COMPLET.md` | The staged A→G roadmap |

## Prerequisites

- Docker Desktop with Compose, or Python 3.13 and Node.js 20 for local work
- A trained model at `ml/model_registry/model.json` (one is present in this checkout)

## Docker startup (full stack)

1. Copy `.env.example` to `.env`.
2. Replace `SECRET_KEY` before any shared or deployed environment. Generate one
   with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Run `docker compose up --build` from this directory.
4. Open the frontend at http://localhost:5173 and API docs at
   http://localhost:8000/docs.

Compose waits for PostgreSQL, runs `alembic upgrade head` in a one-time
`migrate` service, and starts the API only after the migration succeeds.

| Service | URL | Purpose |
|---|---|---|
| Frontend | http://localhost:5173 | React UI |
| Backend API | http://localhost:8000/docs | REST API + OpenAPI |
| Kafka | localhost:9092 | Async scoring events |
| Airflow | http://localhost:8080 | Pipeline orchestration |
| MLflow | http://localhost:5000 | Experiment/model tracking |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 (admin/admin) | Dashboards |
| Alertmanager | http://localhost:9093 | Alert routing |

## Local development

Create `.env` from `.env.example`, then change `POSTGRES_HOST` from `postgres`
to `localhost`. Create and activate a virtual environment before installing:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -r backend/requirements-dev.txt
backend/.venv/Scripts/python -m alembic -c backend/alembic.ini upgrade head
backend/.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Optional local services (Kafka, MLflow, Airflow) can be started individually
with `docker compose up kafka mlflow airflow-webserver ...`.

To train a new synthetic demonstration model, first install the training stack
and then run the module from the project root:

```powershell
backend/.venv/Scripts/python -m pip install -r ml/requirements.txt
backend/.venv/Scripts/python -m ml.train
```

## Configuration

`DATABASE_URL` overrides the individual `POSTGRES_*` settings. `MODEL_PATH`
may be absolute or relative to this project directory. `CORS_ORIGINS` must be a
JSON array of explicit frontend origins. The application refuses short or
placeholder secrets and wildcard CORS configuration.

Kafka (`KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC_REQUESTS`), MLflow
(`MLFLOW_TRACKING_URI`), and the frontend base URL (`VITE_API_BASE_URL`) are
configured through the same `.env` / compose environment. In Kubernetes these
values live in the ConfigMap and Secret under `kubernetes/manifests/`.

## API surface

| Endpoint | Purpose |
|---|---|
| `POST /auth/register`, `POST /auth/login` | JWT authentication |
| `POST /credit/apply` | Synchronous scoring (uses feature-store `dti_ratio` when available) |
| `POST /credit/apply-async` | Publish to Kafka, returns `202` with a `pending` record |
| `GET /credit/status/{id}` | Poll an async request (`pending` → `scored`/`failed`) |
| `GET /credit/applications` | Assessment history (newest first) |
| `GET /credit/stats` | Per-user totals, average score, accepted count |
| `GET /health` / `GET /ready` | Liveness / readiness (DB tables + model loaded) |
| `GET /metrics` | Prometheus metrics |

## Saved assessments

`POST /credit/apply` scores and saves an assessment for the authenticated user.
The response includes its ID, original financial inputs, loan amount and duration,
score, default probability, decision, SHAP explanation, UTC timestamp, and model
version (SHA-256 of the loaded model). Model outputs remain synthetic demonstrations;
loan amount and duration are recorded but do not affect the current borrower-risk model.

`GET /credit/applications?limit=20&offset=0` lists the current user's assessments,
newest first (maximum page size 100). `GET /credit/applications/{id}` retrieves
one assessment; missing IDs and another user's IDs both return 404. The dashboard
loads saved history, and `/result/{id}` opens a durable result after login.

Run `alembic upgrade head` before starting an existing installation (Compose's
migration service does this automatically). Older assessments retain their results;
their unknown input snapshots, explanations, and model versions remain null.

## Health endpoints

- `GET /health` is a liveness check: it confirms the API process is running.
- `GET /ready` verifies the migrated database tables and configured model.
  It returns HTTP 503 with per-component status when a dependency is unavailable.

## Data pipeline (Airflow + dbt + Great Expectations)

The hourly DAG `credit_scoring_pipeline` runs:

1. `validate_raw_data` — Great Expectations checks on `financial_profiles`
   (revenue positive and non-null, debts non-negative, age 18–100). A failure
   exits non-zero and fails the task.
2. `run_dbt_models` — dbt builds `stg_financial_profiles`, `dti_ratio`,
   `score_regularite`, and the `feature_store` table.
3. `check_drift_and_retrain` — Evidently data-drift report with a PSI fallback
   (threshold 0.2); a non-zero exit surfaces drift as a task failure.

The API writes to `feature_store` when a profile is saved, and scoring reads the
dbt-computed `dti_ratio` back, so training and serving use the same feature
definition.

## Verification

```powershell
backend/.venv/Scripts/python -m pytest backend/tests -q -p no:cacheprovider
cd frontend
npm run build
```

Genuine native inference checks (no scoring mocks):

Serving loads the XGBoost Booster directly, so optional scikit-learn and plotting
imports are not required for predictions or native TreeSHAP explanations.

```powershell
backend/.venv/Scripts/python -m pytest verification -q -p no:cacheprovider
```

With the backend ready on port 8000, browser checks run on desktop and mobile:

```powershell
cd frontend
npm ci
npx playwright install chromium
npm run test:e2e
```

The full browser check creates unique demonstration accounts, saves a profile,
verifies the assessment form uses it, requests a genuine prediction, reloads
the saved result, signs out, and reopens history in a fresh browser session.
It also checks that a different user cannot read the assessment. Run against a
development/test database. For an already running frontend, set
`E2E_EXTERNAL_SERVER=1`; `E2E_BASE_URL` and `E2E_API_URL` override the URLs.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request:

- **backend job** (Python 3.13): API, privacy, and migration tests plus the
  genuine inference/TreeSHAP verification suite against SQLite.
- **browser job** (Node 20): frontend build, then the full Playwright flow
  against an isolated Docker Compose PostgreSQL stack, with container logs and
  reports uploaded when a step fails.

## Kubernetes (Palier G)

Production-style manifests live in `kubernetes/manifests/` (namespace, ConfigMap,
Secret, PostgreSQL StatefulSet with PVC, Kafka + Zookeeper, backend Deployment
with an Alembic initContainer, Kafka consumer, frontend, HPA 2→10 pods on CPU,
and a single Ingress). Deploy with:

```bash
kubectl apply -k kubernetes/manifests
```

See `kubernetes/README.md` for prerequisites, image builds, and the load-test
scaling demo.

## Project status

All roadmap stages are implemented: A (core app), B (dbt feature store + Airflow
+ Great Expectations), C (Kafka async scoring), D (MLflow + Evidently), E
(Prometheus + Grafana + Alertmanager), F (Docker Compose + CI/CD), and G
(Kubernetes manifests with HPA and Ingress).

## Notes and limitations

- The model is a **synthetic demonstration** model, not a lending decision tool.
- `kubernetes/manifests/02-secret.yaml` contains development placeholders only;
  use an external secret manager for real deployments.
- Redis and MLflow are not part of the Kubernetes manifests; the scoring path
  does not require them.

The backend dependency groups are intentionally separate:

- `backend/requirements.txt`: API plus inference runtime
- `backend/requirements-dev.txt`: API, inference, and tests
- `ml/requirements.txt`: training, experiment tracking, and monitoring tools

See `docs/GUIDE_COMPLET.md` for the staged roadmap. Its later architecture is
a target design, not a claim that every component is already operational.
