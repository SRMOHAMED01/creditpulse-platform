"""
serve.py — Point d'entrée utilisé par le backend (Palier A.2, puis C)

À IMPLÉMENTER :
def predict(profile: dict) -> dict:
    \"\"\"
    profile : dict avec les mêmes clés que les features d'entraînement
    Retourne :
    {
        "score": int (0-100, probabilité de remboursement),
        "decision": "accepté" | "refusé",
        "explanation": [...]  # sortie de explain.format_explanation()
    }
    \"\"\"
    # 1. Charger le modèle (mettre en cache pour ne pas recharger à chaque appel)
    # 2. Construire le DataFrame à partir de profile
    # 3. model.predict_proba() -> probabilité de défaut
    # 4. score = round((1 - proba_defaut) * 100)
    # 5. decision = "accepté" si score >= seuil (ex: 60) sinon "refusé"
    # 6. explanation = explain.get_shap_values(...)
    # 7. return {...}
    pass

# NOTE Palier C : cette fonction sera appelée par backend/app/kafka/consumer.py
# au lieu d'être appelée directement par le router credit.py
