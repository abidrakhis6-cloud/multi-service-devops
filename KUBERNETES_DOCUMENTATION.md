# Documentation Kubernetes - MultiServe

**Auteur :** Abid RAKHIS AHMAT  
**Date :** 23 Avril 2026  
**Projet :** Multi-Service DevOps - Application Django Multi-Services  
**Cluster :** AWS EKS (Elastic Kubernetes Service)

---

## Table des matières

1. [Introduction](#introduction)
2. [Architecture Kubernetes](#architecture-kubernetes)
3. [Composants Kubernetes](#composants-kubernetes)
4. [Manifests Kubernetes](#manifests-kubernetes)
5. [Déploiement](#déploiement)
6. [Monitoring avec Prometheus](#monitoring-avec-prometheus)
7. [Sécurité](#sécurité)
8. [Scalabilité](#scalabilité)
9. [Commandes utiles](#commandes-utiles)
10. [Schéma d'architecture](#schéma-darchitecture)

---

## Introduction

Ce document décrit l'architecture Kubernetes complète de l'application MultiServe, une application Django multi-services (pharmacie, banque, chat) déployée sur AWS EKS.

### Objectifs

- Déploiement containerisé avec Kubernetes
- Scalabilité automatique (HPA)
- Monitoring avec Prometheus et Grafana
- Sécurité renforcée (Network Policies, Secrets)
- Haute disponibilité (3 replicas, anti-affinity)

---

## Architecture Kubernetes

```
┌─────────────────────────────────────────────────────────────┐
│                     Internet / Utilisateurs                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  AWS Load Balancer (ALB)                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Ingress Controller (NGINX)                  │
│              - SSL/TLS termination                           │
│              - Rate limiting                                 │
│              - Routing basé sur l'hôte                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              MultiServe Application (Django)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │  Pod 1   │  │  Pod 2   │  │  Pod 3   │                   │
│  │  (App)   │  │  (App)   │  │  (App)   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│         │              │              │                      │
│         └──────────────┴──────────────┘                      │
│                        │                                       │
│         ┌──────────────┴──────────────┐                       │
│         ▼                              ▼                       │
│  ┌──────────────┐           ┌──────────────┐                 │
│  │ PostgreSQL    │           │    Redis     │                 │
│  │  (StatefulSet)│           │ (StatefulSet)│                 │
│  └──────────────┘           └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                           │
│  ┌──────────────┐           ┌──────────────┐                 │
│  │  Prometheus  │◄──────────│ ServiceMonitor│                 │
│  └──────────────┘           └──────────────┘                 │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   Grafana    │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Composants Kubernetes

### Namespace

**Fichier :** `namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: multiserve
  labels:
    name: multiserve
    environment: production
    istio-injection: enabled
```

**Description :**
- Isolation logique des ressources
- Labels pour l'organisation
- Istio injection activé pour le service mesh

---

### Deployment

**Fichier :** `deployment.yaml`

**Caractéristiques :**
- **Replicas :** 3 (haute disponibilité)
- **Strategy :** RollingUpdate (déploiement sans interruption)
- **Ressources :**
  - Requests : 256Mi RAM, 250m CPU
  - Limits : 512Mi RAM, 500m CPU
- **Probes :**
  - Liveness probe : `/health/` (vérifie si le pod est vivant)
  - Readiness probe : `/health/` (vérifie si le pod est prêt)
- **Sécurité :**
  - runAsNonRoot : true
  - readOnlyRootFilesystem : true
  - Capabilities : ALL dropped
- **Anti-affinity :** Distribution sur différents nœuds

---

### Service

**Fichier :** `service.yaml`

**Types :**
1. **ClusterIP** : Communication interne entre pods
2. **LoadBalancer** : Exposition externe via AWS ALB

---

### Horizontal Pod Autoscaler (HPA)

**Fichier :** `hpa.yaml`

**Configuration :**
- **Min replicas :** 3
- **Max replicas :** 10
- **Métriques :**
  - CPU : 70% d'utilisation
  - Mémoire : 80% d'utilisation
- **Comportement :**
  - Scale down : 10% par 60s (stabilisation 300s)
  - Scale up : 100% ou 4 pods par 15s (réactif)

---

### Ingress

**Fichier :** `ingress.yaml`

**Fonctionnalités :**
- **SSL/TLS** : Redirection automatique HTTPS
- **Cert-Manager** : Certificats Let's Encrypt automatiques
- **Rate limiting** : 100 requêtes par minute
- **Hosts :** multiserve.app, www.multiserve.app

---

### ConfigMap

**Fichier :** `configmap.yaml`

**Variables d'environnement :**
- DEBUG, DB_ENGINE, DB_NAME, DB_USER
- DB_HOST, DB_PORT, REDIS_URL
- ALLOWED_HOSTS, MEDIA_URL, STATIC_URL

---

### Secret

**Fichier :** `secret.yaml.template`

**Données sensibles (base64) :**
- SECRET_KEY (Django)
- DB_PASSWORD (PostgreSQL)
- REDIS_PASSWORD
- STRIPE_SECRET_KEY
- PAYPAL_CLIENT_SECRET

---

### PersistentVolumeClaim (PVC)

**Fichier :** `pvc.yaml`

**Stockage :**
- **static-pvc :** 5Gi (fichiers statiques)
- **media-pvc :** 10Gi (fichiers médias)
- **StorageClass :** efs-sc (AWS EFS)

---

### ServiceAccount

**Fichier :** `serviceaccount.yaml**

**IAM Role :** Intégration avec AWS IAM via IRSA (IAM Roles for Service Accounts)

---

### NetworkPolicy

**Fichier :** `networkpolicy.yaml`

**Règles de sécurité :**
- **Default deny :** Tout le trafic ingress bloqué par défaut
- **Allow ingress :** Uniquement depuis Ingress Controller
- **Allow egress :** Ports 443, 80, 5432, 6379

---

### PostgreSQL

**Fichier :** `postgresql.yaml`

**Configuration :**
- **StatefulSet** : 1 replica
- **Image :** postgres:15-alpine
- **Stockage :** 20Gi PVC
- **Ressources :** 512Mi-1Gi RAM, 250m-500m CPU
- **Probes :** pg_isready

---

### Redis

**Fichier :** `redis.yaml`

**Configuration :**
- **StatefulSet** : 1 replica
- **Image :** redis:7-alpine
- **Stockage :** 5Gi PVC
- **Ressources :** 256Mi-512Mi RAM, 100m-250m CPU
- **Authentification :** Password required
- **Persistence :** AOF enabled

---

### ServiceMonitor

**Fichier :** `servicemonitor.yaml`

**Configuration Prometheus :**
- **Endpoint :** /metrics
- **Interval :** 15s
- **Scrape timeout :** 10s

---

## Déploiement

### Prérequis

```bash
# Installer kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/windows/amd64/kubectl.exe"

# Installer kustomize
go install sigs.k8s.io/kustomize/kustomize/v5@latest

# Configurer AWS CLI
aws configure
```

### Déploiement sur EKS

```bash
# 1. Configurer le contexte EKS
aws eks update-kubeconfig --name multiserve-cluster --region eu-west-3

# 2. Créer le namespace
kubectl apply -f k8s/base/namespace.yaml

# 3. Créer les secrets
kubectl create secret generic multiserve-secrets \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=DB_PASSWORD='your-db-password' \
  --from-literal=REDIS_PASSWORD='your-redis-password' \
  --from-literal=STRIPE_SECRET_KEY='your-stripe-key' \
  --from-literal=PAYPAL_CLIENT_SECRET='your-paypal-secret' \
  -n multiserve

# 4. Déployer avec Kustomize
kubectl apply -k k8s/base/

# 5. Vérifier le déploiement
kubectl get all -n multiserve
kubectl get pods -n multiserve -w
```

### Déploiement avec overlay (staging/production)

```bash
# Déploiement staging
kubectl apply -k k8s/overlays/staging/

# Déploiement production
kubectl apply -k k8s/overlays/production/
```

---

## Monitoring avec Prometheus

### Architecture Monitoring

```
Application Pods
       │
       │ /metrics
       ▼
ServiceMonitor (Prometheus Operator)
       │
       ▼
Prometheus (scrape 15s)
       │
       ▼
Grafana (dashboards)
```

### Métriques exposées

- **Django :** Requêtes HTTP, temps de réponse, erreurs
- **PostgreSQL :** Connexions, requêtes, performance
- **Redis :** Opérations, mémoire, hit rate
- **Kubernetes :** Pods, CPU, mémoire, réseau

### Dashboards Grafana

1. **MultiServe Overview** : Vue globale de l'application
2. **Django Performance** : Métriques Django
3. **Database Performance** : Métriques PostgreSQL
4. **Redis Performance** : Métriques Redis
5. **Kubernetes Cluster** : Ressources cluster

---

## Sécurité

### 1. Network Policies

- **Principe de moindre privilège** : Tout bloqué par défaut
- **Segmentation réseau** : Isolation par namespace
- **Contrôle du trafic** : Egress limité aux ports nécessaires

### 2. Secrets Management

- **Kubernetes Secrets** : Stockage chiffré
- **Base64 encoding** : Encodage des valeurs sensibles
- **IRSA** : IAM Roles for Service Accounts (AWS)

### 3. Container Security

- **Non-root user** : runAsNonRoot: true
- **Read-only filesystem** : readOnlyRootFilesystem: true
- **Capabilities dropped** : ALL capabilities supprimées
- **No privilege escalation** : allowPrivilegeEscalation: false

### 4. Ingress Security

- **SSL/TLS** : Certificats Let's Encrypt automatiques
- **Rate limiting** : Protection contre DDoS
- **HTTPS redirect** : Redirection automatique

### 5. Pod Security

- **Anti-affinity** : Distribution sur différents nœuds
- **Resource limits** : Protection contre l'épuisement des ressources
- **Health checks** : Probes liveness/readiness

---

## Scalabilité

### Horizontal Pod Autoscaler (HPA)

**Métriques de scaling :**
- **CPU** : Scale si > 70%
- **Mémoire** : Scale si > 80%

**Comportement :**
- **Scale up** : Rapide (15s) pour répondre à la charge
- **Scale down** : Progressif (300s stabilisation) pour éviter le flapping

### Vertical Pod Autoscaler (VPA)

**Recommandation de ressources :**
- Analyse de l'utilisation historique
- Ajustement automatique des requests/limits

### Cluster Autoscaler

**AWS EKS :**
- Ajout automatique de nœuds si nécessaire
- Suppression des nœuds inutilisés
- Économie des coûts

---

## Commandes utiles

### Déploiement

```bash
# Appliquer tous les manifests
kubectl apply -k k8s/base/

# Vérifier l'état
kubectl get all -n multiserve

# Logs des pods
kubectl logs -f deployment/multiserve-app -n multiserve

# Entrer dans un pod
kubectl exec -it deployment/multiserve-app -n multiserve -- /bin/bash
```

### Debug

```bash
# Décrire un pod
kubectl describe pod <pod-name> -n multiserve

# Décrire un service
kubectl describe service multiserve-app -n multiserve

# Événements du namespace
kubectl get events -n multiserve --sort-by='.lastTimestamp'
```

### Scaling

```bash
# Manuel
kubectl scale deployment multiserve-app --replicas=5 -n multiserve

# Vérifier HPA
kubectl get hpa -n multiserve

# Désactiver HPA
kubectl delete hpa multiserve-hpa -n multiserve
```

### Monitoring

```bash
# Vérifier ServiceMonitor
kubectl get servicemonitor -n multiserve

# Vérifier les targets Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Vérifier Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

### Rollback

```bash
# Historique des déploiements
kubectl rollout history deployment/multiserve-app -n multiserve

# Rollback à la version précédente
kubectl rollout undo deployment/multiserve-app -n multiserve

# Rollback à une version spécifique
kubectl rollout undo deployment/multiserve-app --to-revision=2 -n multiserve
```

### Nettoyage

```bash
# Supprimer tous les ressources
kubectl delete -k k8s/base/

# Supprimer le namespace
kubectl delete namespace multiserve

# Supprimer les PVC
kubectl delete pvc static-pvc media-pvc postgres-pvc redis-pvc -n multiserve
```

---

## Schéma d'architecture

### Vue détaillée

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS EKS Cluster                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Node Group 1 (m5.large)              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │  Pod 1   │  │  Pod 2   │  │  Postgres│              │  │
│  │  │ (Django) │  │ (Django) │  │  (DB)    │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Node Group 2 (m5.large)              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │  Pod 3   │  │  Redis   │  │  Nginx   │              │  │
│  │  │ (Django) │  │  (Cache) │  │(Ingress) │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Services                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   ALB    │  │   EFS    │  │   RDS    │  │ ElastiCache│    │
│  │ (LB)     │  │ (Storage)│  │ (Backup) │  │  (Redis)   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de requête

```
User Request
    │
    ▼
AWS ALB (Load Balancer)
    │
    ▼
NGINX Ingress Controller (SSL termination, routing)
    │
    ▼
MultiServe Service (ClusterIP)
    │
    ▼
MultiServe Pods (Django application)
    │
    ├─► PostgreSQL (StatefulSet)
    └─► Redis (StatefulSet)
```

---

## Conclusion

Cette architecture Kubernetes offre :

✅ **Haute disponibilité** : 3 replicas, anti-affinity  
✅ **Scalabilité automatique** : HPA basé sur CPU/mémoire  
✅ **Sécurité renforcée** : Network policies, secrets, RBAC  
✅ **Monitoring complet** : Prometheus + Grafana  
✅ **Déploiement sans interruption** : Rolling updates  
✅ **Résilience** : Health checks, auto-restart  
✅ **Flexibilité** : Kustomize pour différents environnements  

---

## Annexes

### Fichiers Kubernetes

| Fichier | Description |
|---------|-------------|
| `namespace.yaml` | Namespace multiserve |
| `configmap.yaml` | Configuration non sensible |
| `secret.yaml.template` | Template pour secrets |
| `deployment.yaml` | Deployment Django |
| `service.yaml` | Services ClusterIP et LoadBalancer |
| `hpa.yaml` | Horizontal Pod Autoscaler |
| `ingress.yaml` | Ingress NGINX |
| `pvc.yaml` | PersistentVolumeClaims |
| `serviceaccount.yaml` | ServiceAccount avec IAM role |
| `networkpolicy.yaml` | Network policies |
| `postgresql.yaml` | StatefulSet PostgreSQL |
| `redis.yaml` | StatefulSet Redis |
| `servicemonitor.yaml` | ServiceMonitor Prometheus |

### Liens utiles

- [Documentation Kubernetes](https://kubernetes.io/docs/)
- [Documentation EKS](https://docs.aws.amazon.com/eks/)
- [Kustomize](https://kustomize.io/)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [NGINX Ingress](https://kubernetes.github.io/ingress-nginx/)

---

**Fin de la documentation**
