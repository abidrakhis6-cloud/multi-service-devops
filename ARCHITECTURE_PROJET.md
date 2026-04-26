# ==========================================
# MultiServe - Document d'Architecture
# Cahier des Charges & Schémas
# ==========================================

**Auteur :** Abid RAKHIS AHMAT  
**Date :** 24 Avril 2026  
**Version :** 1.0

---

## 📋 Table des Matières

1. [Cahier des Charges](#cahier-des-charges)
2. [Architecture Globale](#architecture-globale)
3. [Schémas d'Architecture](#schémas-darchitecture)
4. [Configuration Réseau AWS](#configuration-réseau-aws)
5. [Ports et Protocoles](#ports-et-protocoles)
6. [Infrastructure Cloud](#infrastructure-cloud)
7. [Sécurité](#sécurité)
8. [Monitoring](#monitoring)

---

## 📝 Cahier des Charges

### 1.1 Objectifs du Projet

**MultiServe** est une application multi-services DevOps qui démontre les meilleures pratiques de :

- **Développement** : Application Django avec architecture modulaire
- **Infrastructure as Code** : Terraform pour AWS
- **Containerisation** : Docker et Docker Compose
- **Orchestration** : Kubernetes avec EKS
- **CI/CD** : GitHub Actions
- **Monitoring** : Prometheus et Grafana
- **Sécurité** : Network Policies, Secrets Management

### 1.2 Fonctionnalités Principales

#### Application Django
- ✅ Gestion des utilisateurs et authentification
- ✅ API RESTful avec Django REST Framework
- ✅ Base de données PostgreSQL
- ✅ Cache Redis
- ✅ Stockage de fichiers media
- ✅ Logging structuré

#### Infrastructure
- ✅ Déploiement sur AWS EKS (Kubernetes)
- ✅ Load Balancing avec Nginx
- ✅ Auto-scaling avec HPA
- ✅ Infrastructure as Code avec Terraform
- ✅ CI/CD avec GitHub Actions

#### Monitoring
- ✅ Métriques système avec Prometheus
- ✅ Dashboards avec Grafana
- ✅ Alerting avec Prometheus Alertmanager
- ✅ Logs centralisés

### 1.3 Contraintes Techniques

| Contrainte | Description |
|------------|-------------|
| **Cloud Provider** | AWS (eu-west-3) |
| **Orchestrateur** | Kubernetes (EKS) |
| **Base de données** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Monitoring** | Prometheus + Grafana |
| **CI/CD** | GitHub Actions |
| **IaC** | Terraform |

### 1.4 Exigences de Performance

- **Disponibilité** : 99.9% uptime
- **Temps de réponse** : < 200ms pour les API
- **Scalabilité** : Auto-scaling horizontal
- **Capacité** : Support de 10,000 utilisateurs simultanés

---

## 🏗️ Architecture Globale

### 2.1 Vue d'Ensemble

L'architecture suit le pattern **Microservices** avec :

- **Frontend** : Nginx (Reverse Proxy + Load Balancer)
- **Backend** : Django Application
- **Base de données** : PostgreSQL
- **Cache** : Redis
- **Monitoring** : Prometheus + Grafana
- **Orchestration** : Kubernetes (EKS)

### 2.2 Composants Principaux

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS EKS Cluster                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Kubernetes Namespace: multiserve          │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │   Nginx      │  │   Django     │  │  PostgreSQL  │ │  │
│  │  │   Ingress    │  │   Pods       │  │   StatefulSet│ │  │
│  │  │   (LB)       │  │   (HPA)      │  │              │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  │         │                 │                 │          │  │
│  │         └─────────────────┴─────────────────┘          │  │
│  │                           │                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │   Redis      │  │  Prometheus  │  │   Grafana    │ │  │
│  │  │   StatefulSet│  │  Deployment  │  │  Deployment  │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Schémas d'Architecture

### 3.1 Architecture Réseau

```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  AWS Route 53 │
                    │   (DNS)       │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  AWS ALB/ELB  │
                    │  (Port 80/443)│
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  Nginx Ingress│   │  Grafana      │   │  Prometheus   │
│  (Port 80)    │   │  (Port 3001)  │   │  (Port 9090)  │
└───────┬───────┘   └───────────────┘   └───────────────┘
        │
        │
┌───────▼───────────────────────────────────────────────┐
│              Kubernetes Services (ClusterIP)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Django App  │  │  PostgreSQL  │  │    Redis     │ │
│  │  (Port 8000) │  │  (Port 5432) │  │  (Port 6379) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────────────────────────────────────┘
```

### 3.2 Architecture des Données

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Flow Architecture                     │
└─────────────────────────────────────────────────────────────┘

User Request
     │
     ▼
┌──────────────┐
│   Nginx      │
│  Ingress     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Django App  │
│  (API)       │
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌──────┐
│ Redis│ │  PG  │
│Cache │ │  DB  │
└──────┘ └──────┘
   │       │
   └───┬───┘
       ▼
┌──────────────┐
│  Prometheus  │
│  (Metrics)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Grafana    │
│ (Dashboards) │
└──────────────┘
```

### 3.3 Architecture CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                             │
└─────────────────────────────────────────────────────────────┘

GitHub Push
     │
     ▼
┌──────────────┐
│ GitHub Actions│
│  (Trigger)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│         Stage 1: Test & Quality          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Syntax  │  │  Linting │  │ Tests  │ │
│  └──────────┘  └──────────┘  └────────┘ │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│         Stage 2: Build & Scan            │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Docker  │  │ Trivy    │  │ Push   │ │
│  │  Build   │  │  Scan    │  │  ECR   │ │
│  └──────────┘  └──────────┘  └────────┘ │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│      Stage 3: Deploy Staging             │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  K8s     │  │  HPA     │  │ Health │ │
│  │  Deploy  │  │  Config  │  │  Check │ │
│  └──────────┘  └──────────┘  └────────┘ │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│      Stage 4: Deploy Production          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Blue/   │  │  Canary  │  │  Roll  │ │
│  │  Green   │  │  Deploy  │  │  Back  │ │
│  └──────────┘  └──────────┘  └────────┘ │
└──────────────────────────────────────────┘
```

### 3.4 Architecture Monitoring

```
┌─────────────────────────────────────────────────────────────┐
│                  Monitoring Stack                            │
└─────────────────────────────────────────────────────────────┘

Application
     │
     ▼ (Metrics)
┌──────────────────────────────────────────┐
│         Exporters                        │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Django  │  │  Node    │  │  Redis │ │
│  │  Exporter│  │ Exporter │  │Exporter│ │
│  └──────────┘  └──────────┘  └────────┘ │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│           Prometheus                     │
│  (Scrape & Store Metrics)                │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│           Alertmanager                    │
│  (Alert Routing & Notification)          │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│           Grafana                        │
│  (Visualization & Dashboards)            │
└──────────────────────────────────────────┘
```

---

## 🔌 Configuration Réseau AWS

### 4.1 VPC Configuration

| Composant | Configuration |
|-----------|---------------|
| **VPC CIDR** | 10.0.0.0/16 |
| **Public Subnets** | 10.0.1.0/24, 10.0.2.0/24 |
| **Private Subnets** | 10.0.10.0/24, 10.0.11.0/24 |
| **Availability Zones** | eu-west-3a, eu-west-3b |

### 4.2 Security Groups

#### Security Group: Load Balancer
```
Inbound Rules:
- HTTP (80)    : 0.0.0.0/0
- HTTPS (443)  : 0.0.0.0/0

Outbound Rules:
- All Traffic : 0.0.0.0/0
```

#### Security Group: EKS Nodes
```
Inbound Rules:
- HTTP (80)    : Load Balancer SG
- HTTPS (443)  : Load Balancer SG
- NodePort (30000-32767) : Load Balancer SG
- SSH (22)     : Bastion Host IP (optional)

Outbound Rules:
- All Traffic : 0.0.0.0/0
```

#### Security Group: Database
```
Inbound Rules:
- PostgreSQL (5432) : EKS Nodes SG
- SSH (22)          : Bastion Host IP (optional)

Outbound Rules:
- All Traffic : 0.0.0.0/0
```

#### Security Group: Redis
```
Inbound Rules:
- Redis (6379) : EKS Nodes SG
- SSH (22)     : Bastion Host IP (optional)

Outbound Rules:
- All Traffic : 0.0.0.0/0
```

#### Security Group: Monitoring
```
Inbound Rules:
- Prometheus (9090) : Bastion Host IP / VPN
- Grafana (3001)    : 0.0.0.0/0 (or restricted)
- Node Exporter (9100) : EKS Nodes SG

Outbound Rules:
- All Traffic : 0.0.0.0/0
```

### 4.3 Network ACLs

#### Public Subnet NACL
```
Inbound Rules:
- 100 | HTTP (80)    | 0.0.0.0/0 | ALLOW
- 110 | HTTPS (443)  | 0.0.0.0/0 | ALLOW
- 120 | Ephemeral Ports (1024-65535) | 0.0.0.0/0 | ALLOW
- *   | All Traffic | 0.0.0.0/0 | DENY

Outbound Rules:
- 100 | HTTP (80)    | 0.0.0.0/0 | ALLOW
- 110 | HTTPS (443)  | 0.0.0.0/0 | ALLOW
- 120 | Ephemeral Ports (1024-65535) | 0.0.0.0/0 | ALLOW
- *   | All Traffic | 0.0.0.0/0 | DENY
```

#### Private Subnet NACL
```
Inbound Rules:
- 100 | PostgreSQL (5432) | EKS Nodes CIDR | ALLOW
- 110 | Redis (6379)     | EKS Nodes CIDR | ALLOW
- 120 | Ephemeral Ports  | 0.0.0.0/0 | ALLOW
- *   | All Traffic      | 0.0.0.0/0 | DENY

Outbound Rules:
- 100 | All Traffic | 0.0.0.0/0 | ALLOW
```

---

## 🔌 Ports et Protocoles

### 5.1 Ports Externes (Internet)

| Port | Protocole | Service | Source | Destination |
|------|----------|---------|--------|-------------|
| 80 | TCP | HTTP | 0.0.0.0/0 | ALB/Nginx |
| 443 | TCP | HTTPS | 0.0.0.0/0 | ALB/Nginx |
| 3001 | TCP | Grafana | 0.0.0.0/0 (ou restreint) | Grafana Pod |
| 9090 | TCP | Prometheus | VPN/Bastion (optionnel) | Prometheus Pod |

### 5.2 Ports Internes (Cluster)

| Port | Protocole | Service | Source | Destination |
|------|----------|---------|--------|-------------|
| 5432 | TCP | PostgreSQL | Django Pods | PostgreSQL |
| 6379 | TCP | Redis | Django Pods | Redis |
| 8000 | TCP | Django App | Nginx/Ingress | Django Pods |
| 10250 | TCP | Kubelet API | Kubernetes Control Plane | Worker Nodes |
| 6443 | TCP | Kubernetes API | Worker Nodes | Control Plane |
| 2379-2380 | TCP | etcd | Control Plane | etcd |
| 10256 | TCP | Kube-proxy | Kubernetes Components | Worker Nodes |

### 5.3 Ports Monitoring

| Port | Protocole | Service | Description |
|------|----------|---------|-------------|
| 9090 | TCP | Prometheus | Web UI & API |
| 9091 | TCP | Alertmanager | Alerting |
| 9093 | TCP | Alertmanager | Cluster communication |
| 9094 | TCP | Alertmanager | Cluster communication |
| 3000 | TCP | Grafana | Web UI (mappé à 3001) |
| 9100 | TCP | Node Exporter | System metrics |
| 9121 | TCP | Redis Exporter | Redis metrics |
| 9187 | TCP | Postgres Exporter | PostgreSQL metrics |

### 5.4 Configuration AWS Security Group

```json
{
  "SecurityGroups": {
    "multiserve-alb-sg": {
      "Description": "Security Group for Application Load Balancer",
      "InboundRules": [
        {
          "Protocol": "TCP",
          "FromPort": 80,
          "ToPort": 80,
          "Source": "0.0.0.0/0"
        },
        {
          "Protocol": "TCP",
          "FromPort": 443,
          "ToPort": 443,
          "Source": "0.0.0.0/0"
        }
      ]
    },
    "multiserve-eks-sg": {
      "Description": "Security Group for EKS Worker Nodes",
      "InboundRules": [
        {
          "Protocol": "TCP",
          "FromPort": 80,
          "ToPort": 80,
          "Source": "multiserve-alb-sg"
        },
        {
          "Protocol": "TCP",
          "FromPort": 443,
          "ToPort": 443,
          "Source": "multiserve-alb-sg"
        },
        {
          "Protocol": "TCP",
          "FromPort": 30000,
          "ToPort": 32767,
          "Source": "multiserve-alb-sg"
        }
      ]
    },
    "multiserve-db-sg": {
      "Description": "Security Group for PostgreSQL",
      "InboundRules": [
        {
          "Protocol": "TCP",
          "FromPort": 5432,
          "ToPort": 5432,
          "Source": "multiserve-eks-sg"
        }
      ]
    },
    "multiserve-redis-sg": {
      "Description": "Security Group for Redis",
      "InboundRules": [
        {
          "Protocol": "TCP",
          "FromPort": 6379,
          "ToPort": 6379,
          "Source": "multiserve-eks-sg"
        }
      ]
    },
    "multiserve-monitoring-sg": {
      "Description": "Security Group for Monitoring Stack",
      "InboundRules": [
        {
          "Protocol": "TCP",
          "FromPort": 9090,
          "ToPort": 9090,
          "Source": "VPN_CIDR"  // Remplacer par votre VPN CIDR
        },
        {
          "Protocol": "TCP",
          "FromPort": 3001,
          "ToPort": 3001,
          "Source": "0.0.0.0/0"  // Ou restreindre
        }
      ]
    }
  }
}
```

---

## ☁️ Infrastructure Cloud

### 6.1 Composants AWS

| Composant | Service AWS | Description |
|-----------|-------------|-------------|
| **Compute** | EKS | Kubernetes Managed Service |
| **Load Balancer** | ALB/NLB | Application Load Balancer |
| **Database** | RDS PostgreSQL | Managed PostgreSQL (optionnel) |
| **Cache** | ElastiCache Redis | Managed Redis (optionnel) |
| **Storage** | EBS | Block Storage |
| **Container Registry** | ECR | Docker Image Registry |
| **IAM** | IAM Roles | Security & Access Control |
| **VPC** | VPC | Network Isolation |
| **Monitoring** | CloudWatch | AWS Native Monitoring |

### 6.2 Terraform Modules

```
terraform/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── main.tf
├── variables.tf
├── outputs.tf
└── provider.tf
```

### 6.3 EKS Cluster Configuration

```yaml
# EKS Cluster Configuration
cluster_name: multiserve-cluster
region: eu-west-3
version: "1.28"

node_groups:
  - name: general-purpose
    instance_types:
      - t3.medium
      - t3.large
    min_size: 2
    max_size: 10
    desired_size: 3
    labels:
      node-type: general
  
  - name: monitoring
    instance_types:
      - t3.small
    min_size: 1
    max_size: 3
    desired_size: 1
    labels:
      node-type: monitoring
    taints:
      - key: monitoring
        value: "true"
        effect: NoSchedule
```

---

## 🔒 Sécurité

### 7.1 Kubernetes Security

#### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: multiserve-network-policy
  namespace: multiserve
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: multiserve
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

#### Secrets Management
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: multiserve-secrets
  namespace: multiserve
type: Opaque
data:
  db-password: <base64-encoded>
  redis-password: <base64-encoded>
  secret-key: <base64-encoded>
```

### 7.2 AWS Security

#### IAM Roles for Service Accounts (IRSA)
```json
{
  "Role": {
    "RoleName": "multiserve-eks-role",
    "AssumeRolePolicyDocument": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/oidc.eks.REGION.amazonaws.com/id/CLUSTER_ID"
          },
          "Action": "sts:AssumeRoleWithWebIdentity"
        }
      ]
    }
  }
}
```

---

## 📊 Monitoring

### 8.1 Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'django'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - multiserve
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: django

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 8.2 Grafana Dashboards

#### Dashboard: MultiServe Overview
- **Panel 1**: Request Rate (req/s)
- **Panel 2**: Response Time (ms)
- **Panel 3**: Error Rate (%)
- **Panel 4**: CPU Usage (%)
- **Panel 5**: Memory Usage (%)
- **Panel 6**: Database Connections
- **Panel 7**: Cache Hit Rate (%)
- **Panel 8**: Pod Status

### 8.3 Alerting Rules

```yaml
# monitoring/prometheus/rules/alerts.yml
groups:
  - name: multiserve_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: DatabaseConnectionPool
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly full"
          description: "{{ $value }} active connections"
```

---

## 📚 Annexes

### A. Commandes Utiles

#### Docker Compose
```bash
# Lancer tous les services
docker-compose up -d

# Lancer seulement monitoring
docker-compose up -d prometheus grafana

# Voir les logs
docker-compose logs -f prometheus
docker-compose logs -f grafana

# Arrêter les services
docker-compose down
```

#### Kubernetes
```bash
# Appliquer les manifests
kubectl apply -f k8s/base/

# Vérifier les pods
kubectl get pods -n multiserve

# Voir les logs
kubectl logs -f deployment/django -n multiserve

# Vérifier les services
kubectl get svc -n multiserve
```

#### Terraform
```bash
# Initialiser
terraform init

# Planifier
terraform plan

# Appliquer
terraform apply

# Détruire
terraform destroy
```

### B. Liens Utiles

- **Documentation Kubernetes**: https://kubernetes.io/docs/
- **Documentation AWS EKS**: https://docs.aws.amazon.com/eks/
- **Documentation Prometheus**: https://prometheus.io/docs/
- **Documentation Grafana**: https://grafana.com/docs/
- **Documentation Terraform**: https://www.terraform.io/docs

---

## 📝 Conclusion

Ce document d'architecture définit l'ensemble des spécifications techniques pour le projet **MultiServe**. Il couvre :

- ✅ Cahier des charges complet
- ✅ Schémas d'architecture détaillés
- ✅ Configuration réseau AWS
- ✅ Ports et protocoles nécessaires
- ✅ Infrastructure cloud
- ✅ Sécurité et monitoring

L'architecture est conçue pour être :
- **Scalable** : Auto-scaling horizontal
- **Résiliente** : Haute disponibilité
- **Sécurisée** : Network policies et secrets management
- **Observable** : Monitoring complet avec Prometheus/Grafana
- **Maintenable** : Infrastructure as Code avec Terraform

---

**Document Version**: 1.0  
**Last Updated**: 24 Avril 2026  
**Author**: Abid RAKHIS AHMAT
