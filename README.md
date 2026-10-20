# CreditPulse - Credit Risk Scoring Platform

CreditPulse is an end-to-end credit risk assessment platform that demonstrates production-ready ML engineering practices. It combines a React frontend with a FastAPI backend, an XGBoost scoring model with SHAP explanations, and a complete data engineering + MLOps stack.

## What This Project Does

Users can register, fill in their financial profile, submit credit applications, and receive instant credit decisions with explainable AI insights. The platform supports both synchronous and asynchronous (event-driven) scoring flows.

## Key Features

- **ML-Powered Scoring**: XGBoost model with genuine TreeSHAP explanations for transparent decisions
- **RESTful API**: FastAPI backend with JWT authentication, input validation, and comprehensive health checks
- **Modern Frontend**: React + Vite UI with interactive visualizations and assessment history
- **Event-Driven Architecture**: Kafka-based async processing for scalable credit scoring
- **Data Pipeline**: Airflow orchestration, dbt transformations, and Great Expectations validation
- **MLOps**: MLflow experiment tracking, Evidently drift detection, automated monitoring
- **Observability**: Prometheus metrics, Grafana dashboards, and Alertmanager notifications
- **Production Ready**: Docker Compose for local dev, GitHub Actions CI/CD, Kubernetes manifests with HPA

## Quick Start

`ash
git clone https://github.com/SRMOHAMED01/creditpulse-platform.git
cd creditpulse-platform/creditpulse
cp .env.example .env
docker compose up --build
`

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, XGBoost, scikit-learn, SHAP  
**Frontend:** React 18, Vite, Tailwind CSS, React Query, Recharts  
**Data/ML:** Airflow, dbt, Great Expectations, MLflow, Evidently, Kafka  
**Infrastructure:** Docker, Kubernetes, Prometheus, Grafana, GitHub Actions  

## Project Structure

`
creditpulse-platform/
+-- .github/workflows/   # CI/CD pipelines
+-- creditpulse/         # Main application code
    +-- backend/         # FastAPI API
    +-- frontend/        # React UI
    +-- ml/             # Model training & serving
    +-- data_pipeline/  # Airflow/dbt/GE
    +-- observability/  # Prometheus/Grafana
    +-- kubernetes/     # K8s manifests
`

See [creditpulse/README.md](creditpulse/README.md) for detailed setup instructions, API documentation, and architecture details.
