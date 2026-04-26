# MultiServe - Application Multi-Services

Plateforme complète de services à domicile (Delivery as a Service) avec infrastructure cloud-native, monitoring avancé et CI/CD automatisé.

## 🚀 Fonctionnalités

### Application
- ✅ **Thème bleu foncé** avec mode sombre/clair (toggle luminosité ☀️/🌙)
- ✅ **Restaurants** : KFC, McDonald's, Quick avec menus complets
- ✅ **Courses** : Lidl, Leclerc, Aldi, Carrefour, Super U
- ✅ **Boutiques** : Apple, Dior, Chanel, Louis Vuitton
- ✅ **Pharmacie** : Médicaments et produits de beauté 24/7
- ✅ **Panier** : Calcul automatique, ajout/suppression produits
- ✅ **Paiement** : 6 méthodes (CB, Visa, PayPal, Apple Pay, Google Pay, Espèces)
- ✅ **Livraison** : Suivi GPS, Chat temps réel avec livreur, Appel/SMS

### Infrastructure & DevOps
- ✅ **Terraform** : Infrastructure AWS complète (VPC, EKS, RDS, ElastiCache)
- ✅ **Docker** : Multi-stage build Python 3.11
- ✅ **Docker Compose** : 9 services (App, PostgreSQL, Redis, Nginx, Prometheus, Grafana, Exporters)
- ✅ **Kubernetes** : Manifests Kustomize (base + overlays dev/staging/prod)
- ✅ **CI/CD GitHub Actions** : 4 stages (Test, Build, Deploy Staging, Deploy Production)
- ✅ **Monitoring** : Prometheus + Grafana avec alertes
- ✅ **Sécurité** : Network Policies, Security Groups, Secrets management

## 📁 Structure du Projet

```
multiserve/
├── .github/
│   └── workflows/
│       └── cicd.yml              # Pipeline CI/CD complète
├── config/                       # Configuration Django
├── core/                         # Application principale
│   ├── templates/               # Templates HTML (base, home, stores, cart...)
│   ├── views.py                 # Vues Django
│   ├── models.py                # Modèles de données
│   └── urls.py                  # Routes
├── k8s/                          # Kubernetes manifests
│   ├── base/                    # Ressources de base
│   └── overlays/                # Environnements (dev/staging/prod)
├── monitoring/                   # Configuration monitoring
│   ├── prometheus/              # Prometheus + alertes
│   └── grafana/                 # Dashboards
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                  # Ressources AWS
│   └── variables.tf             # Variables
├── docker-compose.yml           # Stack Docker complète
├── Dockerfile                   # Multi-stage build
├── .env.example                 # Variables d'environnement
├── .gitignore                   # Fichiers ignorés
├── CDC.md                       # Cahier des Charges complet
├── ARCHITECTURE.md              # Documentation architecture
└── README.md                    # Ce fichier
```

## 🏃 Démarrage Rapide

### Local (Django natif)

```bash
# 1. Cloner et entrer dans le projet
cd multiserve

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 5. Lancer les migrations
python manage.py migrate

# 6. Lancer le serveur
python manage.py runserver 0.0.0.0:8000

# Accéder à : http://localhost:8000
```

### Docker Compose (Recommandé)

```bash
# 1. Lancer tous les services
docker-compose up -d

# 2. Vérifier les services
docker-compose ps

# 3. Voir les logs
docker-compose logs -f app

# Accéder à :
# - Application : http://localhost
# - Grafana     : http://localhost:3000 (admin/admin)
# - Prometheus  : http://localhost:9090 (dans le réseau Docker)

# 4. Arrêter les services
docker-compose down

# 5. Arrêter et supprimer les volumes (clean slate)
docker-compose down -v
```

### Kubernetes (Production)

```bash
# 1. Construire l'image
docker build -t multiserve-app:latest .

# 2. Configurer kubectl pour votre cluster
aws eks update-kubeconfig --name multiserve-production --region eu-west-3

# 3. Déployer avec Kustomize (development)
kubectl apply -k k8s/overlays/development/

# 4. Vérifier le déploiement
kubectl get pods -n multiserve-dev
kubectl get svc -n multiserve-dev

# 5. Déployer en production
kubectl apply -k k8s/overlays/production/
```

## 📊 URLs et Endpoints

### Application Web
| Service | URL | Description |
|---------|-----|-------------|
| Accueil | http://localhost:8000/ | Page d'accueil avec catégories |
| Restaurants | http://localhost:8000/restaurants/ | Liste restaurants |
| Courses | http://localhost:8000/courses/ | Liste supermarchés |
| Boutiques | http://localhost:8000/boutiques/ | Liste boutiques luxe |
| Pharmacie | http://localhost:8000/pharmacie/ | Liste pharmacies |
| Panier | http://localhost:8000/cart/ | Récapitulatif panier |
| Paiement | http://localhost:8000/checkout/ | Page de paiement |
| Livraison | http://localhost:8000/livraison/ | Suivi livreur + Chat |
| Connexion | http://localhost:8000/login/ | Authentification |
| Inscription | http://localhost:8000/register/ | Créer un compte |

### Monitoring
| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | (aucun) |

## 🔧 Configuration

### Variables d'Environnement (.env)

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=multiserve
DB_USER=admin
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_PASSWORD=redis-password
REDIS_URL=redis://redis:6379/0

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=grafana-password

# AWS (pour production)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-west-3
```

## 🧪 Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=. --cov-report=html

# Linter
flake8 .
black --check .

# Sécurité
bandit -r .
safety check
```

## 🚀 CI/CD Pipeline

La pipeline GitHub Actions comprend 4 stages :

1. **Test & Quality**
   - Tests unitaires avec pytest
   - Coverage avec codecov
   - Lint avec flake8, black, isort
   - Scan sécurité Bandit + Safety

2. **Build & Scan**
   - Build Docker image multi-stage
   - Scan vulnérabilités avec Trivy
   - Push vers GitHub Container Registry

3. **Deploy Staging**
   - Déploiement sur EKS staging
   - Smoke tests

4. **Deploy Production**
   - Déploiement sur EKS production
   - Health checks
   - Notifications Slack

## 📈 Monitoring

### Métriques collectées

| Source | Métriques |
|--------|-----------|
| **Application** | Request rate, Latency (p50/p95/p99), Error rate |
| **PostgreSQL** | Connections, Query time, Transactions/sec |
| **Redis** | Memory usage, Hit rate, Connections |
| **Système** | CPU, Memory, Disk I/O, Network |

### Alertes configurées

- High Error Rate (> 5% erreurs 5xx)
- High Latency (p95 > 2s)
- Database Down
- High CPU/Memory Usage (> 85%)
- Disk Space Low (< 10%)

## 📚 Documentation

- [CDC.md](CDC.md) - Cahier des Charges complet
- [ARCHITECTURE.md](ARCHITECTURE.md) - Schémas d'architecture
- [terraform/](terraform/) - Infrastructure AWS (VPC, EKS, RDS...)
- [k8s/](k8s/) - Manifests Kubernetes
- [monitoring/](monitoring/) - Configuration Prometheus/Grafana

## 🔒 Sécurité

- **Network** : VPC isolé, Security Groups restrictifs
- **Transport** : TLS 1.3, HSTS
- **Application** : Django CSRF, XSS Protection, Rate Limiting
- **Auth** : JWT Tokens, RBAC
- **Data** : Chiffrement AES-256
- **Secrets** : Kubernetes Secrets, AWS Secrets Manager
- **Scanning** : Trivy, Bandit, Safety

## 🛠️ Stack Technique

| Couche | Technologie |
|--------|-------------|
| **Frontend** | Django Templates + Tailwind CSS |
| **Backend** | Django 6.0 + DRF + Channels |
| **Database** | PostgreSQL 15 + Redis 7 |
| **Web Server** | Gunicorn + Nginx |
| **Containers** | Docker + Docker Compose |
| **Orchestration** | Kubernetes (EKS) |
| **IaC** | Terraform |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus + Grafana |
| **Cloud** | AWS (VPC, EKS, RDS, S3) |

## 📞 Support

Pour toute question :
- Consulter la documentation dans `CDC.md` et `ARCHITECTURE.md`
- Vérifier les logs : `docker-compose logs -f app`
- Ouvrir une issue sur GitHub

---

**MultiServe** - Développé avec ❤️ et ☕

Version 3.0 | Infrastructure Cloud-Native | Production Ready

---

## 📚 Documentation Complète

- [KUBERNETES_DOCUMENTATION.md](KUBERNETES_DOCUMENTATION.md) - Documentation Kubernetes complète (Manifests, Déploiement, Monitoring, Sécurité)
- [AWS_SETUP.md](AWS_SETUP.md) - Guide de configuration AWS (ECR, ECS, S3, Secrets Manager)
- [CDC.md](CDC.md) - Cahier des Charges complet
- [ARCHITECTURE.md](ARCHITECTURE.md) - Schémas d'architecture

---

## 🎯 Déploiement Kubernetes

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

### Composants Kubernetes

| Composant | Description |
|----------|-------------|
| **Deployment** | 3 replicas, RollingUpdate, Anti-affinity |
| **Service** | ClusterIP + LoadBalancer |
| **HPA** | Auto-scaling 3-10 pods (CPU 70%, Memory 80%) |
| **Ingress** | NGINX, SSL/TLS, Rate limiting |
| **PostgreSQL** | StatefulSet, 20Gi PVC |
| **Redis** | StatefulSet, 5Gi PVC, AOF persistence |
| **ServiceMonitor** | Prometheus scraping /metrics |
| **NetworkPolicy** | Security par défaut deny-all |

---

## 📊 Monitoring Local

Prometheus et Grafana sont préconfigurés pour le monitoring local :

```bash
# Lancer Prometheus et Grafana
docker-compose up -d prometheus grafana

# Accès :
# - Prometheus : http://localhost:9090
# - Grafana   : http://localhost:3001 (admin/admin)
```

### Métriques disponibles

- **Django** : Requêtes HTTP, temps de réponse, erreurs
- **PostgreSQL** : Connexions, requêtes, performance
- **Redis** : Opérations, mémoire, hit rate
- **Kubernetes** : Pods, CPU, mémoire, réseau

---

## 🔒 Sécurité

### Network Policies
- Default deny : Tout le trafic ingress bloqué par défaut
- Allow ingress : Uniquement depuis Ingress Controller
- Allow egress : Ports 443, 80, 5432, 6379

### Container Security
- Non-root user : runAsNonRoot: true
- Read-only filesystem : readOnlyRootFilesystem: true
- Capabilities dropped : ALL capabilities supprimées
- No privilege escalation : allowPrivilegeEscalation: false

### Secrets Management
- Kubernetes Secrets : Stockage chiffré
- Base64 encoding : Encodage des valeurs sensibles
- IRSA : IAM Roles for Service Accounts (AWS)

---

## 📈 Scalabilité

### Horizontal Pod Autoscaler (HPA)
- **Min replicas :** 3
- **Max replicas :** 10
- **Métriques :** CPU 70%, Mémoire 80%
- **Scale up :** Rapide (15s)
- **Scale down :** Progressif (300s stabilisation)

### Cluster Autoscaler
- Ajout automatique de nœuds si nécessaire
- Suppression des nœuds inutilisés
- Économie des coûts

---

## 🚀 CI/CD Pipeline

La pipeline GitHub Actions comprend 4 stages :

1. **Test & Quality**
   - Tests unitaires avec pytest
   - Coverage avec codecov
   - Lint avec flake8, black, isort
   - Scan sécurité Bandit + Safety

2. **Build & Scan**
   - Build Docker image multi-stage
   - Scan vulnérabilités avec Trivy
   - Push vers GitHub Container Registry

3. **Deploy Staging**
   - Déploiement sur EKS staging
   - Smoke tests

4. **Deploy Production**
   - Déploiement sur EKS production
   - Health checks
   - Notifications Slack

---

## 📞 Auteur

**Abid RAKHIS AHMAT**  
Projet Multi-Service DevOps - Application Django Multi-Services  
Date : 23 Avril 2026

---

**Fin du README**