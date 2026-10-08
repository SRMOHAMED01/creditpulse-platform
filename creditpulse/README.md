# CreditPulse

CreditPulse is a learning/portfolio credit-risk application. The currently
implemented core is React + FastAPI + PostgreSQL + XGBoost/SHAP. Kafka,
Airflow, drift monitoring, and the wider observability stack are roadmap work;
they are not part of the runnable core yet.

The model is trained on synthetic data. Its output demonstrates an ML product
flow and must not be used for real lending decisions.

## Prerequisites

- Docker Desktop with Compose, or Python 3.13 and Node.js 20 for local work
- A trained model at `ml/model_registry/model.json` (one is present in this checkout)

## Docker startup

1. Copy `.env.example` to `.env`.
2. Replace `SECRET_KEY` before any shared or deployed environment. Generate one
   with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Run `docker compose up --build` from this directory.
4. Open the frontend at http://localhost:5173 and API docs at
   http://localhost:8000/docs.

Compose waits for PostgreSQL, runs `alembic upgrade head` in a one-time
`migrate` service, and starts the API only after the migration succeeds.

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

## Verification

```powershell
backend/.venv/Scripts/python -m pytest -q -p no:cacheprovider
cd frontend
npm run build
```

The backend dependency groups are intentionally separate:

- `backend/requirements.txt`: API plus inference runtime
- `backend/requirements-dev.txt`: API, inference, and tests
- `ml/requirements.txt`: training, experiment tracking, and monitoring tools

See `docs/GUIDE_COMPLET.md` for the staged roadmap. Its later architecture is a
target design, not a claim that every component is already operational.
