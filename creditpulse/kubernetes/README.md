# kubernetes/ — Palier G (Bonus, optionnel)

Déploiement Kubernetes du système complet : frontend, backend, consumer Kafka,
PostgreSQL, Kafka + Zookeeper, avec HPA et Ingress.

## Prérequis

- Cluster Kubernetes local (kind, minikube, k3d, Docker Desktop)
- `ingress-nginx` (controller + metrics-server) :
  ```bash
  kubectl apply -f https://kubernetes.github.io/ingress-nginx/deploy/
  ```
  Docker Desktop et kind installent/metrics-server est requis pour le HPA.
- `kubectl` et `kustomize` (intégré à kubectl)

## Build des images

Depuis `creditpulse/` :

```bash
docker build -t creditpulse-backend:latest -f backend/Dockerfile .
docker build -t creditpulse-frontend:latest \
  --build-arg VITE_API_BASE_URL=/api ./frontend
```

En cluster local (kind), charger les images :

```bash
kind load docker-image creditpulse-backend:latest creditpulse-frontend:latest
```

## Déploiement

```bash
kubectl apply -k kubernetes/manifests
kubectl get pods -n creditpulse -w
```

Ordre de démarrage géré par les manifests : Postgres → Kafka/Zookeeper →
consumer/backend (migrations Alembic exécutées par un initContainer) →
frontend. L'initContainer `migrate` redémarre le pod jusqu'à ce que la base
accepte les connexions.

Ajouter l'hôte du point d'entrée unique :

```bash
# Windows : C:\Windows\System32\drivers\etc\hosts (admin)
127.0.0.1 creditpulse.local
```

Application : http://creditpulse.local — API via http://creditpulse.local/api
(préfixe réécrit par l'Ingress).

## Démo de scalabilité (HPA)

Le HPA fait évoluer le déploiement backend entre 2 et 10 pods selon le CPU
(seuil 70 %) :

```bash
# Générer de la charge sur l'API
kubectl run hey --rm -it --restart=Never --image=williamyeh/hey -- \
  -z 2m -c 200 http://creditpulse.local/api/health

# Observer le scaling (ajoutez -n creditpulse si besoin)
kubectl get hpa creditpulse-backend -w
kubectl get pods -l app=creditpulse-backend -w
```

Puis la charge retombe, le HPA redescend à 2 pods après 60 s de
stabilisation.

## Vérification

```bash
kubectl get all,ingress,hpa,pvc -n creditpulse
kubectl logs deploy/creditpulse-backend -n creditpulse
kubectl logs deploy/creditpulse-consumer -n creditpulse
curl http://creditpulse.local/api/health
```

## Notes

- **Redis** n'est pas déployé : le backend n'utilise pas Redis dans la
  version actuelle (service présent dans docker-compose à titre d'extension).
- **MLflow** n'est pas déployé ici : `MLFLOW_TRACKING_URI` pointe vers
  `http://creditpulse-mlflow:5000` ; le scoring fonctionne sans
  (logging d'inférence dégradé uniquement).
- Les valeurs de `02-secret.yaml` sont des placeholders de démo
  (identiques à `.env.example`) : à remplacer par un Secret externe pour un
  déploiement réel.
