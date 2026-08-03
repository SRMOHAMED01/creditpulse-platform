# kubernetes/ — Palier G (Bonus, optionnel)

À faire seulement après les Paliers A à F.

À IMPLÉMENTER dans manifests/ :
- backend-deployment.yaml + backend-service.yaml
- frontend-deployment.yaml + frontend-service.yaml
- postgres-statefulset.yaml (avec PersistentVolumeClaim)
- hpa-backend.yaml (Horizontal Pod Autoscaler, ex: scale entre 1 et 10 pods
  selon le CPU > 70%)
- ingress.yaml (point d'entrée unique vers frontend + backend)

Démo à préparer : générer de la charge (ex: avec `hey` ou `k6`) et montrer
que Kubernetes scale automatiquement le nombre de pods backend.
