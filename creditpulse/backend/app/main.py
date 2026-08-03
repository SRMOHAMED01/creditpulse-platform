"""
main.py — Point d'entrée FastAPI (Palier A.2)

À IMPLÉMENTER :
1. Créer l'app FastAPI
2. Inclure les routers : auth, users, credit (voir app/routers/)
3. Configurer CORS pour autoriser le frontend (localhost:5173 en dev)
4. Palier E : monter prometheus-fastapi-instrumentator pour exposer /metrics
   from prometheus_fastapi_instrumentator import Instrumentator
   Instrumentator().instrument(app).expose(app)

from fastapi import FastAPI
app = FastAPI(title="CreditPulse API")

# TODO: app.include_router(auth.router, prefix="/auth")
# TODO: app.include_router(users.router, prefix="/users")
# TODO: app.include_router(credit.router, prefix="/credit")
"""
