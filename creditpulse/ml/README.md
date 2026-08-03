# ml/ — Modèle IA (Palier A.1, D)

Contient l'entraînement XGBoost, l'explicabilité SHAP, le monitoring de dérive Evidently, et le tracking MLflow.

Ordre de développement :
1. `train.py` (données simulées + entraînement)
2. `explain.py` (SHAP)
3. `serve.py` (fonction predict() utilisée par le backend)
4. `monitor.py` (Evidently, Palier D)
