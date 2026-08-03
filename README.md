# CreditPulse

**Plateforme de scoring crédit event-driven, explicable et monitorée en temps réel.**

## 🎯 Le problème

Les banques et fintechs traitent chaque jour des milliers de demandes de crédit. Une décision automatisée doit répondre à trois exigences souvent difficiles à concilier : être **rapide**, être **fiable même en cas de panne partielle**, et être **explicable** — un client refusé a le droit de savoir pourquoi (exigence renforcée par les cadres réglementaires type IFRS 9 / Bâle).

## 💡 La solution

CreditPulse est une plateforme complète de credit risk scoring qui automatise cette décision de bout en bout :

- Le client soumet sa demande via une interface React
- La demande transite par un pipeline event-driven (Kafka) qui garantit qu'aucune requête n'est perdue, même si le service de calcul tombe
- Les données sont nettoyées et transformées en variables métier (DTI ratio, régularité de paiement...) via un pipeline orchestré (Airflow + dbt)
- Un modèle XGBoost calcule la probabilité de défaut, et **SHAP génère une explication détaillée** de chaque décision
- L'ensemble du système est monitoré en temps réel (Prometheus/Grafana) et surveille sa propre dérive de performance (Evidently AI), avec ré-entraînement automatique si nécessaire

## 🏗️ Ce que le projet démontre

| Domaine | Compétences illustrées |
|---|---|
| **Data Engineering** | Pipelines orchestrés (Airflow), transformation versionnée (dbt), qualité des données (Great Expectations), architecture event-driven (Kafka) |
| **Machine Learning** | Modélisation (XGBoost), explicabilité (SHAP), gestion du cycle de vie du modèle |
| **MLOps** | Tracking d'expériences (MLflow), détection de dérive (Evidently AI), ré-entraînement automatisé |
| **Backend / Full-stack** | API REST sécurisée (FastAPI, JWT), frontend React connecté en temps réel |
| **Observabilité & Ops** | Monitoring (Prometheus/Grafana), alerting, conteneurisation (Docker), CI/CD (GitHub Actions) |
| **Finance** | Compréhension des enjeux réglementaires du credit scoring (explicabilité, robustesse, traçabilité) |

## 🧱 Stack technique

`React` · `FastAPI` · `PostgreSQL` · `Apache Kafka` · `Apache Airflow` · `dbt` · `XGBoost` · `SHAP` · `MLflow` · `Evidently AI` · `Redis` · `Prometheus` · `Grafana` · `Docker`

## 📐 Architecture

Voir `docs/GUIDE_COMPLET.md` pour l'architecture détaillée et la méthodologie de construction en paliers.
