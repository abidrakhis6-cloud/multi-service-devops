# MultiServe — Plateforme Cloud-Native de Livraison Multi-Services

> Application web Django déployée sur Google Cloud Platform avec infrastructure DevOps complète : conteneurisation, Kubernetes, Terraform, CI/CD automatisé, monitoring Prometheus/Grafana, TLS/SSL et sécurité multi-couches.

**Auteur :** ABID RAKHIS AHMAT
**Formation :** Administrateur d'Infrastructures Sécurisées — DevOps | École-IT Orléans
**Formateur :** Max Fauquemberg | **Session :** Juin — Juillet 2026

---

## Accès Production

| Service | URL | Statut |
|---|---|---|
| **Application (HTTPS)** | https://34-139-199-187.nip.io/ | ✅ Live |
| **Health check** | https://34-139-199-187.nip.io/health/ | ✅ `{"status":"healthy"}` |
| Grafana (local) | http://127.0.0.1:3001 | admin / voir `.env` |
| Prometheus (local) | http://localhost:9090 | public |
| Alertmanager (local) | http://localhost:9093 | public |

> **IP statique GCP :** `34.139.199.187` (us-east1-b) — ne change pas entre les déploiements
> **Certificat TLS :** Let's Encrypt via `nip.io` — valide jusqu'au 29/09/2026, renouvellement automatique

---

## Fonctionnalités de l'Application

### 4 Catégories de Services
| Catégorie | Enseignes | Spécificité |
|---|---|---|
| **Restaurants** | KFC, McDonald's, Quick | Notes, délais, menus complets |
| **Courses** | Lidl, Leclerc, Aldi, Carrefour, Super U | Produits alimentaires |
| **Boutiques** | Apple, Dior, Chanel, Louis Vuitton | Livraison premium |
| **Pharmacie** | Médicaments, parapharmacie | Disponibilité 24/7 |

### Fonctionnalités Clés
- **Panier** : Ajout/suppression produits, calcul automatique (sous-total + livraison + service)
- **Paiement** : 6 méthodes via Stripe — CB, Visa, PayPal, Apple Pay, Google Pay, Espèces
- **Livraison** : Suivi GPS temps réel + chat client-livreur (WebSocket)
- **Authentification** : Email/MDP, OTP SMS (Twilio), Google OAuth, Facebook OAuth
- **Sécurité** : Verrouillage compte (5 tentatives / 30 min), rate limiting
- **Facturation** : Génération automatique de factures TTC/HT/TVA
- **Stripe Connect** : Virement automatique vers le compte bancaire du livreur
- **Interface** : Thème sombre/clair, responsive, Server-Side Rendering

---

## Architecture Technique

```
┌─────────────────────────────────────────────────────┐
│                  COUCHE CLIENT                      │
│          Navigateurs Web  |  Mobile (PWA)           │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS (TLS 1.2/1.3)
                       │ Let's Encrypt — nip.io
┌──────────────────────▼──────────────────────────────┐
│              COUCHE APPLICATION                     │
│   Nginx (reverse proxy) → Gunicorn (3 workers)      │
│   Django 5.2 + Django Channels (WebSocket)          │
└──────────┬───────────────────────────┬──────────────┘
           │                           │
┌──────────▼──────────┐   ┌────────────▼─────────────┐
│   COUCHE DONNÉES    │   │   COUCHE OBSERVABILITÉ    │
│  PostgreSQL 15      │   │  Prometheus v2.47         │
│  Redis 7            │   │  Grafana 10.1             │
└─────────────────────┘   │  Alertmanager v0.26       │
                          │  6 Exporters              │
                          └──────────────────────────┘

CLOUD GCP (production)
  GitHub Actions → Artifact Registry → GCE VM
  Terraform → GKE | Cloud SQL | Memorystore | GCS
```

---

## Stack Technique Complète

| Couche | Technologie | Version | Rôle |
|---|---|---|---|
| **Backend** | Django | ≥ 5.2 | Framework web Python |
| **API REST** | Django REST Framework | 3.14 | Endpoints JSON |
| **WebSocket** | Django Channels | 4.x | Chat + GPS temps réel |
| **WSGI** | Gunicorn | latest | 3 workers, gthread |
| **Proxy** | Nginx | alpine | SSL, statiques, reverse proxy |
| **Base de données** | PostgreSQL | 15 | Persistance principale |
| **Cache/WS** | Redis | 7 | Sessions, cache, pub/sub |
| **Paiement** | Stripe | latest | PaymentIntent + Connect |
| **SMS/OTP** | Twilio | ≥ 9.1 | Notifications, vérification |
| **Email** | SendGrid | latest | Emails transactionnels |
| **OAuth** | Authlib + django-allauth | 1.3 / 0.63 | Google + Facebook |
| **Métriques** | django-prometheus | 2.3.1 | Export `/metrics` |
| **Conteneurs** | Docker | 24.x | Build multi-stage 3 stages |
| **Compose local** | Docker Compose | 2.x | Stack 11 services |
| **Orchestration** | Kubernetes (GKE) | 1.28 | Déploiement cloud |
| **IaC** | Terraform | ≥ 1.5 | Provisioning GCP |
| **CI/CD** | GitHub Actions | — | 3 jobs automatisés |
| **Registry** | Artifact Registry GCP | — | 60+ images Docker |
| **TLS** | Let's Encrypt + Certbot | — | Renouvellement automatique |
| **Monitoring** | Prometheus | 2.47 | Collecte métriques |
| **Dashboards** | Grafana | 10.1 | 3 dashboards |
| **Alerting** | Alertmanager | 0.26 | Routage notifications |
| **Scan image** | Trivy | latest | Vulnérabilités Docker |
| **Scan code** | Bandit | latest | Sécurité Python |
| **Scan deps** | Safety | latest | CVE dépendances |

---

## Infrastructure Docker Compose (11 services)

```bash
docker-compose up -d
docker-compose ps
```

| Container | Image | Port(s) | Rôle |
|---|---|---|---|
| `multiserve_app` | Artifact Registry (image custom) | 8000 | Django + Gunicorn |
| `multiserve_db` | postgres:15-alpine | 5432 | Base de données |
| `multiserve_redis` | redis:7-alpine | 6379 | Cache + WebSocket |
| `multiserve_nginx` | nginx:alpine | 80, 443 | Reverse proxy SSL |
| `multiserve_prometheus` | prom/prometheus:v2.47 | 9090 | Collecte métriques |
| `multiserve_grafana` | grafana/grafana:10.1 | 3001→3000 | Dashboards |
| `multiserve_alertmanager` | prom/alertmanager:v0.26 | 9093 | Alerting |
| `multiserve_node_exporter` | prom/node-exporter | 9100 | Métriques système |
| `multiserve_nginx_exporter` | nginx/nginx-prometheus-exporter | 9113 | Métriques Nginx |
| `multiserve_postgres_exporter` | prometheuscommunity/postgres-exporter | 9187 | Métriques PostgreSQL |
| `multiserve_redis_exporter` | oliver006/redis_exporter | 9121 | Métriques Redis |

---

## Infrastructure GCP (Terraform)

```
terraform/gcp/
├── apis.tf              # 12 APIs GCP activées
├── network.tf           # VPC, sous-réseaux, règles firewall
├── gke.tf               # Cluster GKE + HPA + Workload Identity
├── sql.tf               # Cloud SQL PostgreSQL 15 managé
├── redis.tf             # Memorystore Redis managé
├── artifact_registry.tf # Registre Docker (europe-west1)
├── storage.tf           # Cloud Storage (médias, statiques)
└── variables.tf / outputs.tf
```

**12 APIs GCP activées :** Container, Artifact Registry, Cloud SQL, Redis, Storage, Service Networking, Secret Manager, Compute Engine, IAM, Cloud Logging, Cloud Monitoring, Cloud Resource Manager

```bash
cd terraform/gcp
terraform init
terraform plan
terraform apply   # ~8 minutes pour toute l'infrastructure
```

---

## Pipeline CI/CD GitHub Actions

**3 jobs séquentiels — déclenchés à chaque push sur `main`**

```
Push main
    │
    ▼
Job 1: Tests & Qualité (≈ 2 min)
    ├── Services CI : PostgreSQL 15 + Redis 7
    ├── Flake8 critiques     → BLOQUANT ❌ (E9,F63,F7,F82)
    ├── Black formatage      → avertissement ⚠️
    ├── Bandit scan code     → avertissement ⚠️
    ├── Safety dépendances   → avertissement ⚠️
    └── pytest + manage.py test
    │
    ▼
Job 2: Build & Scan Sécurité (≈ 2 min)
    ├── Auth GCP (Service Account)
    ├── Docker build multi-stage (cache BuildKit GitHub Actions)
    ├── Push → Artifact Registry europe-west1 (tag SHA + latest)
    └── Trivy scan CRITICAL/HIGH → SARIF → GitHub Security tab
    │
    ▼
Job 3: Déploiement GCP (≈ 5 min)
    ├── Injection startup script dans metadata GCE
    ├── VM reset → déclenche le script automatiquement
    ├── git pull → docker compose pull → docker compose up -d
    ├── python manage.py migrate
    └── Health check curl /health/ (6 tentatives × 20s)
```

**Résultat :** 60+ déploiements réussis — durée moyenne : 7m 37s

---

## Kubernetes (GKE)

```
k8s/
├── base/
│   ├── deployment.yaml      # 3 replicas, rolling update, probes
│   ├── service.yaml         # ClusterIP
│   ├── ingress.yaml         # Nginx Ingress Controller
│   ├── hpa.yaml             # HPA : 3 → 10 replicas (CPU 70%)
│   ├── networkpolicy.yaml   # Deny-all par défaut, allow sélectif
│   └── servicemonitor.yaml  # Prometheus scraping auto
└── overlays/
    ├── dev/        # 1 replica, DEBUG=true
    ├── staging/    # 2 replicas, données de test
    └── production/ # HPA actif, secrets GCP Secret Manager
```

```bash
# Déploiement production
kubectl apply -k k8s/overlays/production/
kubectl get pods -n multiserve -w
```

---

## Monitoring & Observabilité

### Prometheus — 6 cibles scrappées (toutes UP)

| Target | Port | Métriques exposées |
|---|---|---|
| django-app | 8000/metrics | Requêtes HTTP, latences, erreurs |
| node-exporter | 9100 | CPU, RAM, Disk, Network |
| nginx-exporter | 9113 | Connexions, requests, upstream |
| postgres-exporter | 9187 | Connexions, transactions, locks |
| redis-exporter | 9121 | Mémoire, opérations, hit rate |
| prometheus | 9090 | Auto-monitoring |

### 15 Règles d'Alerte

| Groupe | Alertes |
|---|---|
| **Application** | DjangoAppDown, HighErrorRate (>5%), HighLatency (>2s), OrderRateDrop |
| **Base de données** | PostgreSQLDown, PostgreSQLHighConnections (>80), PostgreSQLSlowQueries |
| **Cache** | RedisDown, RedisHighMemoryUsage (>80%), RedisConnectionsHigh (>100) |
| **Infrastructure** | HighCPUUsage (>80%), HighMemoryUsage (>80%), DiskSpaceLow (<10%) |
| **Containers** | ContainerHighRestartRate (>3/h) |
| **Demo** | TestAlertAlwaysFiring (toujours active — prouve le flux) |

### Grafana — 3 Dashboards (provisionnés automatiquement)

| Dashboard | Panneaux |
|---|---|
| **Infrastructure** | CPU %, RAM %, Disk %, Network I/O |
| **Application** | Requêtes/s, Latence p95, Erreurs 5xx/4xx |
| **Database** | Connexions actives, Transactions/s, Cache hit |

---

## Sécurité Multi-Couches

| Couche | Mesure | Outil |
|---|---|---|
| **Code** | Scan vulnérabilités Python | Bandit (CI/CD bloquant) |
| **Dépendances** | CVE packages | Safety (CI/CD) |
| **Images Docker** | Scan CRITICAL/HIGH | Trivy → GitHub Security |
| **Containers** | Utilisateur non-root | `appuser` UID 1000 (Dockerfile) |
| **Transport** | TLS 1.2/1.3, HSTS 1 an | Nginx + Let's Encrypt |
| **Authentification** | Brute force | django-axes (5 tentatives / 30 min) |
| **Double facteur** | OTP 6 chiffres / 10 min | django-otp + Twilio |
| **Application** | CSRF, XSS, Clickjacking | Django Security Middleware |
| **Réseau** | VPC privé, NetworkPolicy K8s | Terraform GCP |
| **Secrets** | Jamais en clair dans le code | GitHub Secrets + GCP Secret Manager |

---

## Modèles de Données (12 entités)

| Modèle | Champs clés | Relations |
|---|---|---|
| **User** | Django built-in | OneToOne → UserProfile |
| **UserProfile** | phone_verified, google_id, facebook_id, lock_account() | FK → User |
| **PhoneOTP** | otp_code (6 chars), max_attempts (3), expiration (10 min) | FK → User |
| **Store** | name, category, rating, delivery_time | — |
| **Product** | name, price, image | FK → Store |
| **Cart** | created_at | FK → User |
| **CartItem** | quantity | FK → Cart, Product |
| **Order** | status (7 états), total | FK → User, Store, Driver |
| **Payment** | method (6 méthodes), status (4 états), stripe_id | OneToOne → Order |
| **Driver** | latitude, longitude (GPS), rating | FK → User |
| **Message** | content, timestamp | FK → Order, User |
| **Invoice** | montant_ttc, montant_ht, tva | OneToOne → Order |
| **UserBankAccount** | stripe_account_id | OneToOne → User |

**7 statuts de commande :** `pending → confirmed → preparing → in_delivery → delivered → cancelled → refunded`
**6 méthodes de paiement :** `card · visa · paypal · apple_pay · google_pay · cash`

---

## Endpoints API

| URL | Méthode | Description |
|---|---|---|
| `/` | GET | Page d'accueil |
| `/restaurants/`, `/courses/`, `/boutiques/`, `/pharmacie/` | GET | Listes par catégorie |
| `/restaurants/<nom>/` | GET | Détail et menu |
| `/cart/` | GET | Panier |
| `/checkout/` | GET | Paiement |
| `/livraison/` | GET | Suivi GPS + chat |
| `/login/`, `/register/` | GET/POST | Authentification |
| `/health/` | GET | `{"status": "healthy"}` |
| `/metrics` | GET | Métriques Prometheus |
| `/api/save-order/` | POST | Sauvegarde adresse |
| `/api/send-sms/` | POST | SMS via Twilio |
| `/api/payment/create-intent/` | POST | Stripe PaymentIntent |
| `/api/payment/webhook/` | POST | Webhook Stripe |
| `/api/stripe/create-account/` | POST | Compte Stripe Connect |
| `/api/stripe/transfer/` | POST | Virement livreur |

---

## Démarrage Local

### Docker Compose (recommandé)

```bash
# 1. Cloner le projet
git clone https://github.com/abidrakhis6-cloud/multi-service-devops.git
cd multi-service-devops

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos valeurs (DB_PASSWORD, SECRET_KEY, REDIS_PASSWORD)

# 3. Lancer la stack complète (11 services)
docker-compose up -d

# 4. Vérifier l'état
docker-compose ps

# 5. Migrations (première fois uniquement)
docker-compose exec app python manage.py migrate

# Accès :
# Application    → http://localhost:8080
# Grafana        → http://127.0.0.1:3001  (admin / voir .env)
# Prometheus     → http://localhost:9090
# Alertmanager   → http://localhost:9093
```

### Stack légère production (docker-compose.free.yml)

```bash
# Stack optimisée pour VM e2-micro (1GB RAM)
# Sans monitoring (Prometheus/Grafana) pour économiser la RAM
docker-compose -f docker-compose.free.yml up -d
```

### Django natif (développement)

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
.\venv\Scripts\activate       # Windows

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

---

## Tests

```bash
# Tests unitaires avec couverture
pytest --cov=. --cov-report=html

# Tests Django natifs
python manage.py test --parallel 2

# Qualité du code
flake8 . --select=E9,F63,F7,F82   # Erreurs critiques (bloquant CI)
black --check .                     # Formatage

# Sécurité
bandit -r . --exclude ./venv
safety check
```

---

## Certificat TLS (SSL)

Le certificat Let's Encrypt est obtenu via **nip.io** — un service DNS public gratuit qui résout automatiquement `34-139-199-187.nip.io` vers l'IP `34.139.199.187`.

```bash
# Sur la VM GCE (déjà configuré)
certbot certonly --standalone -d 34-139-199-187.nip.io \
  --non-interactive --agree-tos --email votre@email.com

# Renouvellement automatique (configuré par Certbot)
certbot renew --dry-run
```

**Certificat :** `/etc/letsencrypt/live/34-139-199-187.nip.io/fullchain.pem`
**Clé privée :** `/etc/letsencrypt/live/34-139-199-187.nip.io/privkey.pem`

---

## Compétences Démontrées (Blocs REAC)

| Bloc de Compétence | Réalisation dans le projet | Preuve |
|---|---|---|
| **Rédiger des scripts** | Dockerfile, startup script GCE, scripts Terraform, CI/CD YAML | `Dockerfile`, `.github/workflows/ci-cd.yml` |
| **Déployer infrastructure IaC** | Terraform GCP : GKE, Cloud SQL, Redis, Artifact Registry, GCS, VPC, IAM | `terraform/gcp/*.tf` |
| **Sécuriser l'infrastructure** | Trivy + Bandit + Safety en CI/CD, containers non-root, OTP, OAuth, HSTS, NetworkPolicy | CI logs + `settings.py` |
| **Mettre en production** | GitHub Actions 3 stages → GCE VM (startup script) → health check automatique | Pipeline #52+ — Success |
| **Environnement de test** | CI avec services PostgreSQL et Redis réels, pytest, flake8 bloquant | `.github/workflows/ci-cd.yml` |
| **Gérer le stockage** | Cloud SQL managé + Memorystore Redis + Cloud Storage GCS | `terraform/gcp/sql.tf`, `redis.tf`, `storage.tf` |
| **Conteneuriser l'application** | Dockerfile 3 stages, Docker Compose 11 services, utilisateur non-root | `Dockerfile`, `docker-compose.yml` |
| **Déployer en CI/CD** | Pipeline automatique : test → build → scan → deploy (60+ runs réussis) | GitHub Actions |
| **Collecter les métriques** | Prometheus scrape 6 targets toutes les 15s, 15 règles d'alerte | `monitoring/prometheus/` |
| **Superviser** | Grafana 3 dashboards provisionnés automatiquement + Alertmanager | `monitoring/grafana/provisioning/` |
| **Orchestrer avec K8s** | GKE, Deployment, HPA (3→10 replicas), Kustomize overlays 3 envs, NetworkPolicy | `k8s/` |
| **TLS/SSL** | Let's Encrypt via nip.io, TLSv1.2/1.3, HSTS 1 an, redirect HTTP→HTTPS | `nginx/nginx-free.conf` |

---

## Arborescence du Projet

```
multiserve/
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # Pipeline 3 stages (test → build → deploy)
├── config/
│   ├── settings.py                # DB auto-detect, Redis, sécurité, OAuth, Twilio
│   ├── urls.py                    # Routes racine + health check
│   ├── wsgi.py / asgi.py          # Gunicorn / Django Channels
├── core/
│   ├── models.py                  # 12 modèles de données
│   ├── views.py                   # 25 vues
│   ├── urls.py                    # 35 routes URL
│   ├── stripe_views.py            # Paiement Stripe + Connect
│   └── templates/                 # Templates HTML (SSR)
├── accounts/
│   ├── models.py                  # UserProfile, PhoneOTP
│   ├── services.py                # OTP, OAuth, SMS
│   └── views.py                   # Auth avancée
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml         # Scrape config (6 jobs, 15s interval)
│   │   └── rules/alerts.yml       # 15 règles d'alerte
│   ├── alertmanager/alertmanager.yml
│   └── grafana/provisioning/      # Dashboards + datasources auto-chargés
├── terraform/gcp/                 # IaC GCP (8 fichiers .tf)
├── k8s/
│   ├── base/                      # Manifests Kubernetes communs
│   └── overlays/dev|staging|prod/ # Kustomize par environnement
├── nginx/
│   ├── nginx.conf                 # Config complète (prod + SSL)
│   └── nginx-free.conf            # Config légère VM gratuite (SSL Let's Encrypt)
├── Dockerfile                     # Multi-stage : builder → production → development
├── docker-compose.yml             # Stack complète 11 services
├── docker-compose.free.yml        # Stack légère GCE (4 services + SSL)
├── docker-compose.prod.yml        # Stack production avec SSL domaine
├── requirements.txt               # 30+ dépendances Python
├── .env.example                   # Template variables d'environnement
├── deploy.sh                      # Script déploiement production manuel
├── ssl-init.sh                    # (optionnel) Init certificat Let's Encrypt
├── CDC.md                         # Cahier des Charges complet
├── ARCHITECTURE.md                # Schémas architecture ASCII
├── CHOIX_TECHNIQUES.md            # Justification des choix technologiques
├── DEPLOIEMENT_PRODUCTION.md      # Guide déploiement production
└── ALERTS_TEST.md                 # Tests alertes Prometheus (résultats 04/05/2026)
```

---

## Variables d'Environnement

```env
# Django
SECRET_KEY=votre-clé-secrète-longue-64-chars
DEBUG=False
ALLOWED_HOSTS=*

# Base de données
DB_NAME=multiserve
DB_USER=admin
DB_PASSWORD=mot-de-passe-fort
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_PASSWORD=mot-de-passe-redis

# Stripe (paiement)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Twilio (SMS/OTP)
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+33xxxxxxxxx

# OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
FACEBOOK_APP_ID=xxx
FACEBOOK_APP_SECRET=xxx

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxx
DEFAULT_FROM_EMAIL=noreply@multiserve.com

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=mot-de-passe-fort
```

**GitHub Secrets requis pour CI/CD :**
`GCP_SA_KEY`, `GCP_PROJECT_ID`, `GCE_INSTANCE_NAME`, `GCE_ZONE`, `CI_SECRET_KEY`, `DJANGO_SECRET_KEY`, `DJANGO_DB_PASSWORD`, `DJANGO_REDIS_PASSWORD`

---

## Documentation

| Fichier | Contenu |
|---|---|
| [CDC.md](CDC.md) | Cahier des charges complet, spécifications fonctionnelles et techniques |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Schémas ASCII : réseau, BDD, Docker Compose, CI/CD |
| [CHOIX_TECHNIQUES.md](CHOIX_TECHNIQUES.md) | Justifications : GKE vs ECS, Redis vs Memcached, Terraform vs CloudFormation |
| [DEPLOIEMENT_PRODUCTION.md](DEPLOIEMENT_PRODUCTION.md) | Guide déploiement, DNS, SSL, commandes utiles |
| [ALERTS_TEST.md](ALERTS_TEST.md) | Rapport de test des 15 alertes Prometheus (04/05/2026) |
| [AVANCEMENT_MAX.md](AVANCEMENT_MAX.md) | Suivi retours formateur Max Fauquemberg |

---

## Commandes Utiles

```bash
# === DOCKER ===
docker-compose ps                              # État des 11 containers
docker-compose logs -f app                    # Logs Django
docker-compose exec app python manage.py shell # Shell Django
docker-compose exec app python manage.py migrate

# === MONITORING ===
curl http://localhost:9090/api/v1/targets      # Cibles Prometheus
curl http://localhost:9090/api/v1/alerts       # Alertes actives
curl https://34-139-199-187.nip.io/health/    # Health check production

# === GCP ===
gcloud compute instances list --project=multi-service-494900
gcloud compute ssh multiserve-vm --zone=us-east1-b --project=multi-service-494900

# === KUBERNETES ===
kubectl apply -k k8s/overlays/production/
kubectl get pods -n multiserve
kubectl top pods -n multiserve

# === TERRAFORM ===
cd terraform/gcp && terraform plan
cd terraform/gcp && terraform apply

# === SÉCURITÉ ===
bandit -r . --exclude ./venv -f json
safety check
trivy image europe-west1-docker.pkg.dev/multi-service-494900/multiserve/app:latest
```

---

## Chiffres Clés

| Indicateur | Valeur |
|---|---|
| Modèles Django | 12 |
| Vues Django | 25 |
| Routes URL | 35 |
| Services Docker Compose | 11 |
| Services Terraform GCP | 8 |
| APIs GCP activées | 12 |
| Images Artifact Registry | 60+ |
| Règles d'alerte Prometheus | 15 |
| Targets Prometheus (UP) | 6/6 |
| Dashboards Grafana | 3 |
| Méthodes de paiement | 6 |
| Méthodes d'authentification | 4 |
| Déploiements CI/CD réussis | 60+ |
| Durée pipeline complète | ~7 min 37s |

---

**MultiServe v3.0** — Infrastructure Cloud-Native — Production Ready — TLS Enabled

`https://34-139-199-187.nip.io/`
