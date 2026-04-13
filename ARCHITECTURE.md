# Architecture MultiServe

## Schéma d'Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │   Mobile    │  │   Admin     │  │  Livreur    │        │
│  │   (React)   │  │   (PWA)     │  │   Panel     │  │    App      │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼──────────────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │                  │
          └──────────────────┴──────────────────┴──────────────────┘
                                     │
                              ┌──────▼──────┐
                              │  CDN/Cloud  │
                              │   Flare     │
                              └──────┬──────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                         APPLICATION LAYER (Kubernetes)                      │
│  ┌─────────────────────────────────┼─────────────────────────────────┐        │
│  │                    Ingress Controller (Nginx)                    │        │
│  └─────────────────────────────────┼─────────────────────────────────┘        │
│                                    │                                         │
│  ┌─────────────────────────────────┼─────────────────────────────────┐        │
│  │              API Gateway (Django REST + DRF)                    │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │        │
│  │  │  Auth    │ │  Orders  │ │  Stores  │ │  Payment │             │        │
│  │  │ Service  │ │ Service  │ │ Service  │ │ Service  │             │        │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘             │        │
│  └─────────────────────────────────┼─────────────────────────────────┘        │
│                                    │                                         │
│  ┌─────────────────────────────────┼─────────────────────────────────┐        │
│  │         WebSocket Server (Django Channels + Redis)              │        │
│  │              Chat temps réel | Notifications push               │        │
│  └─────────────────────────────────┼─────────────────────────────────┘        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                           DATA LAYER                                       │
│                                                                            │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐  │
│  │  PostgreSQL   │  │    Redis      │  │   (S3/MinIO)  │  │ Elasticsearch│  │
│  │  (Principal)  │  │   (Cache/     │  │   Médias      │  │   (Search)   │  │
│  │               │  │   Sessions)   │  │               │  │              │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  └─────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                        OBSERVABILITY LAYER                                  │
│                                                                            │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │  Prometheus   │  │   Grafana     │  │    Loki       │                   │
│  │  (Métriques) │  │ (Dashboards)  │  │    (Logs)     │                   │
│  └───────────────┘  └───────────────┘  └───────────────┘                   │
└────────────────────────────────────────────────────────────────────────────┘
```

## Architecture Réseau AWS (Terraform)

```
┌────────────────────────────────────────────────────────────────┐
│                          AWS VPC                               │
│                      10.0.0.0/16                              │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                    Public Subnets                        │   │
│  │     10.0.1.0/24 (AZ-a)    10.0.2.0/24 (AZ-b)          │   │
│  │                                                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                │   │
│  │  │  ALB    │  │  NAT    │  │ Bastion │                │   │
│  │  │         │  │ Gateway │  │   Host  │                │   │
│  │  └─────────┘  └─────────┘  └─────────┘                │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                   │
│  ┌────────────────────────┼──────────────────────────────┐   │
│  │               Private Subnets (Application)            │   │
│  │     10.0.10.0/24 (AZ-a)    10.0.11.0/24 (AZ-b)        │   │
│  │                                                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │   │
│  │  │  EKS    │  │  ECS    │  │   EC2   │              │   │
│  │  │ Workers │  │  Tasks  │  │ (Backup)│              │   │
│  │  └─────────┘  └─────────┘  └─────────┘              │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                   │
│  ┌────────────────────────┼──────────────────────────────┐   │
│  │               Private Subnets (Database)               │   │
│  │     10.0.20.0/24 (AZ-a)    10.0.21.0/24 (AZ-b)        │   │
│  │                                                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                │   │
│  │  │   RDS   │  │ ElastiCache│  │  EFS   │                │   │
│  │  │PostgreSQL│  │  Redis   │  │ (Shared)│                │   │
│  │  └─────────┘  └─────────┘  └─────────┘                │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Schéma de la Base de Données (SQLite3/PostgreSQL)

### Diagramme ER Simplifié

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      USER       │       │      STORE      │       │    PRODUCT      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ username        │       │ name            │       │ name            │
│ email           │       │ category        │       │ price           │
│ password_hash   │       │ image           │       │ store_id (FK)   │
│ phone           │       │ description     │       │ image           │
│ created_at      │       │ rating          │       │ description     │
└────────┬────────┘       │ created_at      │       │ category        │
         │                └────────┬────────┘       │ created_at      │
         │                         │                └─────────────────┘
         │                         │
         │                         │
         │                ┌────────┴────────┐
         │                │    CATEGORY     │
         │                ├─────────────────┤
         │                │ restaurant      │
         │                │ courses         │
         │                │ boutique        │
         │                │ pharmacie       │
         │                └─────────────────┘
         │
         │
         │                ┌─────────────────┐       ┌─────────────────┐
         │                │      CART       │       │    CARTITEM     │
         │                ├─────────────────┤       ├─────────────────┤
         │                │ id (PK)         │       │ id (PK)         │
         └───────────────│ user_id (FK)    │       │ cart_id (FK)    │
                          │ created_at      │       │ product_id (FK) │
                          └────────┬────────┘       │ quantity        │
                                   │                │ subtotal        │
                                   │                └─────────────────┘
                                   │
                                   │
                          ┌────────┴────────┐
                          │      ORDER      │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ user_id (FK)    │
                          │ cart_id (FK)    │
                          │ store_id (FK)   │
                          │ driver_id (FK)  │
                          │ status          │
                          │ total_price     │
                          │ delivery_addr   │
                          │ lat/lng         │
                          │ created_at      │
                          └────────┬────────┘
                                   │
                          ┌────────┴────────┐       ┌─────────────────┐
                          │     PAYMENT     │       │     MESSAGE     │
                          ├─────────────────┤       ├─────────────────┤
                          │ id (PK)         │       │ id (PK)         │
                          │ order_id (FK)   │       │ order_id (FK)   │
                          │ amount          │       │ user_id (FK)    │
                          │ method          │       │ content         │
                          │ status          │       │ timestamp       │
                          │ transaction_id  │       └─────────────────┘
                          └─────────────────┘
                                   │
                          ┌────────┴────────┐
                          │     DRIVER      │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ name            │
                          │ phone           │
                          │ vehicle         │
                          │ rating          │
                          │ is_available    │
                          │ lat/lng         │
                          └─────────────────┘
```

## Composants Docker Compose

```
┌────────────────────────────────────────────────────────────────┐
│                      Docker Compose Stack                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐                                            │
│  │     Nginx     │  Reverse Proxy + SSL Termination          │
│  │    :80:443    │                                            │
│  └───────┬───────┘                                            │
│          │                                                      │
│  ┌───────┴───────┐                                            │
│  │     App       │  Django + Gunicorn (3 workers)           │
│  │    :8000      │                                            │
│  └───────┬───────┘                                            │
│          │                                                      │
│  ┌───────┼───────┐                                            │
│  │       │       │                                            │
│  ▼       ▼       ▼                                            │
│  ┌───────────┐  ┌───────────┐                                  │
│  │PostgreSQL │  │  Redis    │  Data Layer                    │
│  │  :5432    │  │  :6379    │                                │
│  └───────────┘  └───────────┘                                  │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐                          │
│  │  Prometheus   │  │   Grafana     │  Observability          │
│  │   :9090      │  │   :3000       │                          │
│  └───────────────┘  └───────────────┘                          │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│  │Node Exporter  │  │Redis Exporter │  │Postgres Exporter│     │
│  │Metrics système│  │Metrics Redis  │  │Metrics DB       │     │
│  └───────────────┘  └───────────────┘  └───────────────┘      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Pipeline CI/CD

```
┌────────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│   │  CODE   │───▶│  BUILD  │───▶│  TEST   │                 │
│   └─────────┘    └─────────┘    └─────────┘                 │
│                      │                │                       │
│                      ▼                ▼                       │
│              ┌──────────────────────────────┐               │
│              │     Docker Image Build       │               │
│              └──────────────────────────────┘               │
│                              │                               │
│                              ▼                               │
│              ┌──────────────────────────────┐               │
│              │   Security Scan (Trivy)     │               │
│              └──────────────────────────────┘               │
│                              │                               │
│           ┌──────────────────┼──────────────────┐           │
│           │                  │                  │           │
│           ▼                  ▼                  ▼           │
│      ┌─────────┐       ┌─────────┐       ┌─────────┐      │
│      │ STAGING │       │  PROD   │       │  ROLLBACK│      │
│      │   EKS   │       │   EKS   │       │  if fail │      │
│      └─────────┘       └─────────┘       └─────────┘      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Stack Technique Détaillée

| Couche | Technologie | Version | Rôle |
|--------|-------------|---------|------|
| **Frontend** | Django Templates | 6.0 | SSR, SEO-friendly |
| | Tailwind CSS | 3.x | Styling utility-first |
| **Backend** | Django | 6.0 | Framework web |
| | Django REST Framework | 3.14 | API REST |
| | Django Channels | 4.x | WebSocket/Async |
| **Database** | PostgreSQL | 15 | Données principales |
| | Redis | 7 | Cache, Sessions, Queue |
| **Web Server** | Gunicorn | 21.x | WSGI Server |
| | Nginx | 1.25 | Reverse Proxy |
| **Containers** | Docker | 24.x | Containerization |
| | Docker Compose | 2.x | Local orchestration |
| **Orchestration** | Kubernetes | 1.28 | Production orchestration |
| | Helm | 3.12 | Package management |
| **IaC** | Terraform | 1.5+ | Infrastructure as Code |
| **CI/CD** | GitHub Actions | - | Build, Test, Deploy |
| **Registry** | GitHub Container Registry | - | Image storage |
| **Monitoring** | Prometheus | 2.47 | Metrics collection |
| | Grafana | 10.1 | Dashboards |
| | Loki | 2.9 | Log aggregation |
| **Cloud** | AWS | - | VPC, EKS, RDS, S3 |

## Flux de Données

```
1. Utilisateur → Nginx (HTTPS)
2. Nginx → Django App (HTTP/8000)
3. Django → PostgreSQL (Queries)
4. Django → Redis (Cache/Sessions)
5. Django → S3 (Médias)
6. Prometheus → Scrapes metrics
7. Grafana → Visualize data
```

## Sécurité Multi-Couche

| Couche | Mesure |
|--------|--------|
| **Network** | VPC isolé, Security Groups restrictifs |
| **Transport** | TLS 1.3, HSTS, Cert-Manager |
| **Application** | Django CSRF, XSS Protection, Rate Limiting |
| **Auth** | JWT Tokens, RBAC |
| **Data** | AES-256 at rest, SSL in transit |
| **Secrets** | AWS Secrets Manager, K8s Secrets |
| **Scanning** | Trivy (images), Bandit (code), Safety (deps) |

## Scaling Strategy

```
Horizontal Pod Autoscaler (HPA):
├── CPU > 70% → Scale up
├── Memory > 80% → Scale up
├── Min replicas: 3 (prod)
├── Max replicas: 20 (prod)
└── Cooldown: 5min

Database:
├── Read replicas for SELECT queries
├── Connection pooling (PgBouncer)
└── Vertical scaling when needed

Cache:
├── Redis Cluster mode
├── LRU eviction policy
└── Max memory: 80%
```
