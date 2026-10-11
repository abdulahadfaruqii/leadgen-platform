# Deployment Guide

## Local Development
```bash
cp .env.example .env
# Edit .env with your API keys
make build
make up
make migrate
```

## Production Kubernetes
```bash
# Build images
docker build -t leadgen/api:latest -f docker/Dockerfile.api backend/
docker build -t leadgen/worker:latest -f docker/Dockerfile.worker backend/
docker build -t leadgen/frontend:latest -f docker/Dockerfile.frontend frontend/

# Deploy
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/worker-deployment.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

## Environment Variables
See `.env.example` for all required variables.

## Monitoring
- Flower: http://localhost:5555 (Celery monitoring)
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
