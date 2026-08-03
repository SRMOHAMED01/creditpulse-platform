# 🗺️ CreditPulse — Guide Complet de Construction (ex-Fentech Lian v1)

> Plateforme de Credit Risk Scoring event-driven : React → FastAPI → Kafka → Data Pipeline → XGBoost/SHAP → Observabilité

---

## Philosophie de construction

Cette architecture est ambitieuse (Kafka, Kubernetes, observabilité complète). La règle pour réussir :

**On construit en paliers. Chaque palier est un produit démontrable seul, AVANT d'ajouter la complexité du palier suivant.**

```
Palier A — Cœur fonctionnel (sans Kafka, sans K8s, sans observabilité)
   → Frontend + Backend + Modèle IA qui marchent ensemble en synchrone

Palier B — Data Engineering (le vrai différenciant)
   → dbt + Feature Store + Airflow branchés dessus

Palier C — Architecture event-driven
   → Kafka remplace l'appel direct synchrone

Palier D — MLOps
   → MLflow + Evidently + ré-entraînement automatique

Palier E — Observabilité
   → Prometheus + Grafana + Alertmanager

Palier F — Industrialisation
   → Docker Compose complet + CI/CD GitHub Actions

Palier G (bonus, optionnel) — Kubernetes
   → Scalabilité, si tu veux aller jusqu'au bout
```

---

## PALIER A — Cœur fonctionnel

### But
Un utilisateur peut s'inscrire, remplir son profil, demander un crédit, et recevoir un score + explication SHAP. Tout en synchrone, pas de Kafka encore.

### A.1 — Modèle IA (`ml/`)
- Génère un dataset simulé réaliste (`revenu`, `dettes`, `age`, `historique_paiement`, `anciennete_emploi`, `nombre_credits_en_cours`)
- Calcule le `DTI ratio` = dettes / revenu à la main pour l'instant (dbt le fera au Palier B)
- Entraîne un `XGBClassifier`, évalue avec AUC-ROC / précision / rappel
- Ajoute `shap.TreeExplainer` pour générer les valeurs d'explication
- Sauvegarde le modèle (`model.json` ou `.pkl`)

**Fichiers** : `ml/train.py`, `ml/explain.py`, `ml/serve.py` (fonction `predict(profile: dict) -> {score, decision, shap_values}`)

### A.2 — Backend (`backend/`)
- FastAPI + SQLAlchemy + PostgreSQL
- Tables : `users`, `financial_profiles`, `credit_applications`
- Auth JWT : `/auth/register`, `/auth/login`
- `POST /credit/apply` : récupère le profil, appelle directement `ml/serve.py`, sauvegarde le résultat, retourne le JSON

**Fichiers** : voir arborescence `backend/app/`

### A.3 — Frontend (`frontend/`)
- React + Vite + Tailwind
- Pages : Signup, Login, ProfileForm, CreditRequest, Result (gauge + SHAP chart avec Recharts)
- Axios + React Query pour les appels API

### ✅ Checkpoint Palier A
De bout en bout dans le navigateur : inscription → profil → demande de crédit → résultat visuel avec explication. **C'est déjà un projet solide et démontrable.**

---

## PALIER B — Data Engineering (le cœur de ton profil)

### But
Remplacer le calcul "à la main" du DTI par un vrai pipeline versionné et orchestré. C'est la partie qui te différencie le plus pour un poste data eng.

### B.1 — dbt Core (`data_pipeline/dbt_project/`)
- Modèle `staging/stg_financial_profiles.sql` : nettoyage des données brutes venant de PostgreSQL
- Modèles `features/` :
  - `dti_ratio.sql` = dettes / revenu
  - `score_regularite.sql` = régularité des paiements historiques
  - `stabilite_professionnelle.sql` = ancienneté emploi normalisée
- Tests dbt : `not_null`, `accepted_values` sur les colonnes critiques

### B.2 — Great Expectations (`data_pipeline/great_expectations/`)
- Validation avant que les données entrent dans le feature store : `revenu > 0`, pas de valeurs aberrantes, colonnes obligatoires présentes

### B.3 — Feature Store
- Table PostgreSQL dédiée `feature_store` alimentée par dbt, qui contient uniquement les variables prêtes pour le modèle (pas les données brutes)

### B.4 — Airflow (`data_pipeline/dags/`)
- DAG `credit_scoring_dag.py` orchestrant : extraction PostgreSQL → run dbt → validation Great Expectations → écriture feature store
- (Bonus) Une tâche de collecte de données marché via `yfinance` pour enrichir le contexte économique

### ✅ Checkpoint Palier B
Le DAG tourne dans l'UI Airflow (localhost:8080), les features apparaissent dans la table `feature_store`, et le backend lit depuis cette table au lieu de calculer le DTI en Python.

---

## PALIER C — Architecture event-driven avec Kafka

### But
Découpler le backend du calcul du score, pour que le système survive même si le service ML est temporairement indisponible.

### C.1 — Producer (`backend/app/kafka/producer.py`)
- `POST /credit/apply` ne calcule plus le score directement
- Il publie un événement `credit_request_submitted` dans le topic Kafka `credit-requests` et retourne immédiatement un statut `"en cours de traitement"`

### C.2 — Consumer (`backend/app/kafka/consumer.py`)
- Un service séparé écoute le topic `credit-requests`
- Récupère les features depuis le feature store
- Appelle le modèle ML (`ml/serve.py`)
- Écrit le résultat en base
- Publie un événement `credit_decision_ready` (topic `credit-decisions`)

### C.3 — Notification au frontend
- Option simple : polling (le frontend interroge `GET /credit/status/{id}` toutes les 2s)
- Option avancée : WebSocket qui pousse le résultat dès qu'il est prêt

### ✅ Checkpoint Palier C
Tu coupes le service ML manuellement (docker stop) → la demande de crédit reste dans Kafka sans être perdue → tu relances le service → la demande est traitée automatiquement. **C'est la preuve de la résilience.**

---

## PALIER D — MLOps

### D.1 — MLflow
- `train.py` log chaque run : hyperparamètres XGBoost, AUC, F1, date, auteur
- Model Registry : marquer une version comme "Production"

### D.2 — Evidently AI (`ml/monitor.py`)
- Compare la distribution des données de production (feature store) vs les données d'entraînement
- Calcule le PSI (Population Stability Index) ; si PSI > 0.2 → alerte drift

### D.3 — Ré-entraînement automatique
- Ajoute une tâche Airflow qui vérifie le rapport Evidently ; si drift détecté → relance `train.py` → nouvelle version loggée dans MLflow

### ✅ Checkpoint Palier D
UI MLflow (localhost:5000) montre l'historique des runs. Un rapport Evidently HTML montre un dashboard de dérive.

---

## PALIER E — Observabilité

### E.1 — Prometheus (`observability/prometheus/prometheus.yml`)
- Le backend FastAPI expose `/metrics` (via `prometheus-fastapi-instrumentator`)
- Prometheus scrape : temps de réponse, nombre de requêtes, taux d'erreur, CPU/mémoire des conteneurs

### E.2 — Grafana (`observability/grafana/dashboards/`)
- Dashboard "Business" : nombre de crédits traités, score moyen, taux d'acceptation
- Dashboard "Technique" : latence API, erreurs, drift (branché sur Evidently)

### E.3 — Alertmanager
- Règle d'alerte : si taux d'erreur > 5% pendant 5 min → notification (Slack/email simulé)

### ✅ Checkpoint Palier E
Tableaux de bord Grafana en direct pendant que tu envoies des requêtes de test.

---

## PALIER F — Industrialisation

### F.1 — Docker Compose complet
- Un seul `docker-compose.yml` à la racine qui lance : frontend, backend, postgres, kafka+zookeeper, redis, airflow, mlflow, prometheus, grafana

### F.2 — CI/CD (`.github/workflows/ci.yml`)
- À chaque push : lint (ruff/eslint) → tests (pytest/vitest) → build des images Docker → (optionnel) déploiement

### ✅ Checkpoint Palier F
`docker-compose up` démarre tout le système en une commande.

---

## PALIER G (Bonus, optionnel) — Kubernetes

- Manifests dans `kubernetes/manifests/` : Deployments, Services, HPA (Horizontal Pod Autoscaler) pour le backend
- Démonstration : montée en charge simulée → Kubernetes scale automatiquement le nombre de pods backend

À faire seulement si tu as le temps après les paliers A→F, qui sont déjà largement suffisants pour un portfolio très solide.

---

## 🏗️ Architecture finale (vue d'ensemble)

```
                        React Frontend (TS)
                              │
                    HTTPS / REST API
                              │
                     FastAPI Gateway
                              │
         ┌────────────────────┴───────────────────┐
         │                                        │
     Authentication (JWT)                  Credit API
         │                                        │
         └────────────────────┬───────────────────┘
                              │
                   Kafka Event Producer
                              │
                   ===== Apache Kafka =====
                              │
                Credit Request Consumer
                              │
               Validation / Cleaning
                              │
                       PostgreSQL
                              │
                    Feature Pipeline (Airflow)
                              │
                            dbt
                              │
                     Feature Store
                              │
                      XGBoost Model
                              │
                            SHAP
                              │
                    Decision Engine
                              │
                     Redis Cache
                              │
                    Response API → Frontend

   Observabilité :
   Prometheus → Grafana → Alertmanager
   MLflow → Evidently AI
   GitHub Actions → Docker → (Kubernetes en option)
```

## 📋 Table de suivi

| Palier | Contenu | Différenciant pour Data Eng/Finance | Durée réaliste |
|---|---|---|---|
| A | Frontend + Backend + Modèle | Base solide | 3-4 semaines |
| B | dbt + Feature Store + Airflow | ⭐⭐⭐ Très fort | 2-3 semaines |
| C | Kafka event-driven | ⭐⭐⭐ Très fort | 2 semaines |
| D | MLflow + Evidently | ⭐⭐ Fort | 1-2 semaines |
| E | Prometheus + Grafana | ⭐⭐ Fort | 1 semaine |
| F | Docker + CI/CD | ⭐ Attendu | 1 semaine |
| G | Kubernetes | ⭐ Bonus | optionnel |

---

## Comment on travaille ensemble à partir de maintenant

On suit les paliers dans l'ordre. Pour chaque fichier du zip fourni, tu trouveras un commentaire en en-tête expliquant précisément ce qu'il doit contenir — c'est ta feuille de route ligne par ligne. Dis-moi quand tu veux qu'on commence le **Palier A.1 (génération des données + entraînement XGBoost)** et on code ensemble, toi à l'écriture, moi en guide.
