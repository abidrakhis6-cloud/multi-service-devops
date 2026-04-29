# Cahier des Charges - MultiServe

## 1. CONTEXTE ET PRESENTATION DU PROJET

### 1.1 Contexte
MultiServe est une application web de services à domicile (Delivery as a Service) inspirée des plateformes comme Uber Eats, Instacart et Amazon. Elle permet aux utilisateurs de commander des repas, faire leurs courses, acheter des produits de luxe et des médicaments avec livraison en temps réel.

### 1.2 Objectifs
- **Objectif principal** : Créer une plateforme multi-services unifiée avec livraison en 30 minutes
- **Objectifs secondaires** :
  - Suivi GPS temps réel des livreurs
  - Système de chat intégré client-livreur
  - Paiement sécurisé multi-méthodes (6 options)
  - Interface responsive avec mode sombre/clair
  - Infrastructure cloud scalable avec Kubernetes

### 1.3 Périmètre du projet
| Inclus | Exclus |
|--------|--------|
| Restaurants (KFC, McDo, Quick) | Service de réservation table |
| Courses (Lidl, Leclerc, Carrefour) | Livraison internationale |
| Boutiques luxe (Apple, Dior, Chanel) | Marketplace B2B |
| Pharmacie 24/7 | Téléconsultation médicale |
| Suivi GPS + Chat | App mobile native (future V2) |

## 2. ARCHITECTURE TECHNIQUE

### 2.1 Schéma d'Architecture Globale

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

### 2.2 Stack Technique

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| **Frontend** | Django Templates + Tailwind CSS | SSR pour SEO, rapidité de développement |
| **Backend** | Django 6.0 + Django REST Framework | Framework mature, ORM puissant, admin intégré |
| **WebSocket** | Django Channels + Redis | Chat temps réel, notifications |
| **Base de données** | PostgreSQL 15 | ACID compliant, JSON support, scalable |
| **Cache** | Redis 7 | Sessions, cache API, pub/sub WebSocket |
| **Message Queue** | Redis / Celery | Tâches asynchrones (emails, notifications) |
| **Conteneurisation** | Docker + Docker Compose | Reproductibilité, isolation |
| **Orchestration** | Kubernetes (EKS/GKE) | Auto-scaling, haute disponibilité |
| **Infrastructure** | Terraform | IaC, versionnable, reproductible |
| **CI/CD** | GitHub Actions | Intégration native GitHub, marketplace riche |
| **Monitoring** | Prometheus + Grafana | Standard industriel, dashboards flexibles |
| **Logging** | Loki + Grafana | Agrégation centralisée des logs |
| **Reverse Proxy** | Nginx | Performance, SSL termination, load balancing |

## 3. INFRASTRUCTURE CLOUD (AWS)

### 3.1 Architecture Réseau (Terraform)

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

### 3.2 Ressources AWS (Terraform)

| Ressource | Type | Configuration |
|-----------|------|---------------|
| VPC | aws_vpc | CIDR: 10.0.0.0/16, DNS enabled |
| Subnets Public | aws_subnet | 2 AZs, /24 each |
| Subnets Private App | aws_subnet | 2 AZs, /24 each |
| Subnets Private DB | aws_subnet | 2 AZs, /24 each |
| Internet Gateway | aws_internet_gateway | Attaché au VPC |
| NAT Gateway | aws_nat_gateway | 1 par AZ pour HA |
| Route Tables | aws_route_table | Public + Private séparés |
| Security Groups | aws_security_group | ALB, App, DB layers |
| EKS Cluster | aws_eks_cluster | Version 1.28, 3 nodes t3.medium |
| RDS PostgreSQL | aws_db_instance | db.t3.micro, Multi-AZ |
| ElastiCache Redis | aws_elasticache_cluster | cache.t3.micro |
| ALB | aws_lb | Application Load Balancer |
| S3 Bucket | aws_s3_bucket | Médias + Static files |
| CloudWatch | aws_cloudwatch_log_group | Logs centralisés |

## 4. DOCKER ARCHITECTURE

### 4.1 Multi-Stage Dockerfile (Django)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /app

# Créer utilisateur non-root
RUN groupadd -r django && useradd -r -g django django

# Installation dépendances runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier wheels et installer
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copier code
COPY --chown=django:django . .

# Static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

USER django

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "config.wsgi:application"]
```

### 4.2 Docker Compose (Production-like)

```yaml
version: '3.8'

services:
  # Application Django
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: multiserve_app
    environment:
      - DEBUG=False
      - DB_ENGINE=postgresql
      - DB_NAME=multiserve
      - DB_USER=${DB_USER:-admin}
      - DB_PASSWORD=${DB_PASSWORD:-changeme}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-django-insecure-change-me}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1}
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Base de données PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: multiserve_db
    environment:
      - POSTGRES_DB=multiserve
      - POSTGRES_USER=${DB_USER:-admin}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-admin} -d multiserve"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache + Sessions + WebSocket
  redis:
    image: redis:7-alpine
    container_name: multiserve_redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Reverse Proxy Nginx
  nginx:
    image: nginx:alpine
    container_name: multiserve_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - app
    networks:
      - backend
      - frontend
    restart: unless-stopped

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: multiserve_prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - backend
    restart: unless-stopped

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: multiserve_grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    networks:
      - backend
      - frontend
    restart: unless-stopped

  # Node Exporter (metrics système)
  node-exporter:
    image: prom/node-exporter:latest
    container_name: multiserve_node_exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  prometheus_data:
  grafana_data:

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

## 5. CI/CD PIPELINE (GitHub Actions)

### 5.1 Workflow Complet (3 stages)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ==========================================
  # STAGE 1: TEST
  # ==========================================
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_multiserve
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov black flake8 bandit safety

      - name: Lint with flake8
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Format check with black
        run: black --check .

      - name: Security scan with Bandit
        run: bandit -r . -f json -o bandit-report.json || true

      - name: Dependency vulnerability check
        run: safety check || true

      - name: Run tests with pytest
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/test_multiserve
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key
          DEBUG: True
        run: |
          pytest --cov=. --cov-report=xml --cov-report=html -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            htmlcov/
            bandit-report.json

  # ==========================================
  # STAGE 2: BUILD & SCAN
  # ==========================================
  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          load: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Push image to registry
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  # ==========================================
  # STAGE 3: DEPLOY
  # ==========================================
  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Setup Helm
        uses: azure/setup-helm@v3
        with:
          version: 'v3.12.0'

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name multiserve-cluster --region ${{ secrets.AWS_REGION }}

      - name: Deploy to Kubernetes
        run: |
          # Update image tag
          sed -i 's|image: .*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}|' k8s/ deployment.yaml
          
          # Apply configurations
          kubectl apply -k k8s/overlays/production/
          
          # Wait for rollout
          kubectl rollout status deployment/multiserve-app -n production --timeout=300s

      - name: Verify deployment
        run: |
          kubectl get pods -n production
          kubectl get svc -n production

      - name: Run smoke tests
        run: |
          # Get load balancer URL
          URL=$(kubectl get svc multiserve-lb -n production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
          
          # Wait for service
          sleep 30
          
          # Health check
          curl -f http://$URL/health/ || exit 1
          echo "Deployment successful!"

      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          text: 'Deployment to production ${{ job.status }}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 6. KUBERNETES ARCHITECTURE

### 6.1 Structure Kustomize

```
k8s/
├── base/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml (template)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml (Horizontal Pod Autoscaler)
│   └── ingress.yaml
├── overlays/
│   ├── development/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── production/
│       ├── kustomization.yaml
│       ├── deployment-patch.yaml
│       └── ingress-patch.yaml
└── monitoring/
    ├── servicemonitor.yaml
    └── prometheus-rules.yaml
```

### 6.2 Deployment Kubernetes (base)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multiserve-app
  labels:
    app: multiserve
    component: app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: multiserve
      component: app
  template:
    metadata:
      labels:
        app: multiserve
        component: app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: app
          image: multiserve-app:latest
          ports:
            - containerPort: 8000
              name: http
          envFrom:
            - configMapRef:
                name: multiserve-config
            - secretRef:
                name: multiserve-secrets
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          volumeMounts:
            - name: static-files
              mountPath: /app/staticfiles
            - name: media-files
              mountPath: /app/media
      volumes:
        - name: static-files
          persistentVolumeClaim:
            claimName: static-pvc
        - name: media-files
          persistentVolumeClaim:
            claimName: media-pvc
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - multiserve
                topologyKey: kubernetes.io/hostname
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: multiserve-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: multiserve-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

## 7. MONITORING & OBSERVABILITY

### 7.0 URLs d'accès au Monitoring (Local)

| Service | URL | Credentials | Statut |
|---------|-----|-------------|--------|
| **Grafana** | http://127.0.0.1:3001 | admin / admin123 | ✅ Fonctionnel |
| **Prometheus** | http://localhost:9090 | (aucune) | ✅ Fonctionnel |
| **Alertmanager** | http://localhost:9093 | (aucune) | ✅ Fonctionnel |
| **Node Exporter** | http://localhost:9100/metrics | (aucune) | ✅ Fonctionnel |

> **Note :** Sur Windows avec Docker Desktop, utiliser `127.0.0.1` pour Grafana au lieu de `localhost` en raison du port forwarding.

### 7.1 Métriques Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'django-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/rules/*.yml
```

### 7.2 Dashboards Grafana

| Dashboard | Métriques |
|-----------|-----------|
| **Application Overview** | RPS, Latence p99, Erreurs 5xx, Taux de succès |
| **Django Performance** | Temps de requête DB, Cache hit/miss, Queue length |
| **Infrastructure** | CPU/Mem/Disque des pods, Network I/O |
| **Business Metrics** | Commandes/heure, Panier moyen, Taux de conversion |
| **SLA Monitoring** | Uptime %, Temps de réponse, Disponibilité par région |

### 7.3 Alertes Prometheus

```yaml
# monitoring/rules/alerts.yml
groups:
  - name: multiserve-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(django_http_responses_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "p95 latency is above 2 seconds"

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod is crash looping"
          description: "Pod {{ $labels.pod }} is restarting frequently"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connection count"
          description: "PostgreSQL has more than 80 active connections"
```

## 8. PLANNING & GESTION DE PROJET

### 8.1 Phases du Projet

| Phase | Durée | Livrables |
|-------|-------|-----------|
| **Phase 1: Fondation** | 2 semaines | CDC, Architecture, Setup repos |
| **Phase 2: MVP** | 4 semaines | Backend Django, Frontend, Docker |
| **Phase 3: Infrastructure** | 3 semaines | Terraform, Kubernetes, CI/CD |
| **Phase 4: Observability** | 2 semaines | Monitoring, Alerting, Logging |
| **Phase 5: Sécurité** | 2 semaines | Audit, Scan, Hardening |
| **Phase 6: Production** | 1 semaine | Go-live, Runbooks, Support |

### 8.2 Ressources

| Rôle | Quantité | Skills |
|------|----------|--------|
| Tech Lead / Architecte | 1 | AWS, K8s, Terraform, Django |
| Développeurs Backend | 2 | Python, Django, PostgreSQL |
| Développeur Frontend | 1 | React/Tailwind (optionnel mobile) |
| DevOps Engineer | 1 | CI/CD, Kubernetes, Monitoring |
| QA Engineer | 1 | Tests auto, Sécurité |

## 9. SECURITE

### 9.1 Mesures de Sécurité

| Couche | Mesure | Implémentation |
|--------|--------|----------------|
| **Application** | OWASP Top 10 | Django security middleware, CSRF, XSS protection |
| **Authentification** | JWT + Refresh tokens | django-rest-framework-simplejwt |
| **Autorisation** | RBAC | Django permissions + groups |
| **Données** | Chiffrement | AES-256 pour données sensibles, TLS 1.3 transit |
| **Secrets** | Vault | AWS Secrets Manager + Kubernetes external-secrets |
| **Réseau** | Segmentation | VPC isolé, Security Groups restrictifs |
| **Scan** | Vulnérabilités | Trivy (images), Bandit (code), Snyk (deps) |
| **Audit** | Logging | CloudTrail + Loki pour traçabilité |

## 10. DOCUMENTATION OPERATIONNELLE

### 10.1 Runbooks

- **R011**: Procédure de déploiement en production
- **R012**: Rollback d'urgence
- **R013**: Scaling horizontal automatique
- **R014**: Procédure incident base de données
- **R015**: Rotation des credentials

### 10.2 Procédures de Monitoring

```bash
# Vérifier santé des pods
kubectl get pods -n production -o wide

# Logs applicatifs en temps réel
kubectl logs -f deployment/multiserve-app -n production --tail=100

# Métriques Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Dashboards Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

---

**Document version**: 2.0  
**Date**: 27 Avril 2026  
**Auteur**: Équipe MultiServe DevOps  
**Approbation**: En cours

---

## 11. ARCHITECTURE CIBLE DÉTAILLÉE

### 11.1 Vue d'ensemble de l'architecture de production

L'architecture cible de MultiServe repose sur une infrastructure cloud AWS entièrement provisionnée via Terraform (IaC), orchestrée par Kubernetes (EKS), et monitorée par la stack Prometheus/Grafana.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           FLUX DE TRAFIC PRODUCTION                          │
│                                                                              │
│  Utilisateurs ──► CloudFront (CDN) ──► ALB (SSL Termination)               │
│                                              │                               │
│                                     ┌────────▼────────┐                      │
│                                     │  EKS Cluster     │                      │
│                                     │  (3x t3.medium)  │                      │
│                                     │  Django + Celery  │                      │
│                                     └──┬─────┬─────┬───┘                      │
│                                        │     │     │                          │
│                              ┌─────────▼┐ ┌──▼───┐ ┌▼────────┐               │
│                              │ RDS PG   │ │Redis │ │ S3 Media│               │
│                              │ (Multi-AZ│ │Cache │ │ Bucket  │               │
│                              └──────────┘ └──────┘ └─────────┘               │
│                                                                              │
│  Monitoring: Prometheus ──► Alertmanager ──► Grafana                        │
│  CI/CD: GitHub Actions ──► ECR ──► EKS (kubectl)                           │
│  IaC: Terraform (S3 backend + DynamoDB lock)                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Composants de l'architecture cible

| Composant | Service AWS | Rôle | Redondance |
|-----------|------------|------|------------|
| **CDN** | CloudFront | Distribution statique, cache edge | Global |
| **Load Balancer** | ALB | Distribution trafic, SSL termination | Multi-AZ |
| **Orchestration** | EKS v1.28 | Gestion conteneurs, auto-scaling | 3 nodes min |
| **Base de données** | RDS PostgreSQL | Stockage persistant ACID | Multi-AZ |
| **Cache/Sessions** | ElastiCache Redis | Cache API, sessions, pub/sub | Replica |
| **Stockage média** | S3 Bucket | Images, documents, uploads | Versionné |
| **Registry** | ECR | Images Docker applicatives | Encrypté |
| **Monitoring** | Prometheus + Grafana | Métriques, dashboards, alertes | Persisté |
| **Alerting** | Alertmanager | Routage et notifications d'alertes | Intégré |
| **IaC** | Terraform + S3 + DynamoDB | Provisioning reproductible | State locké |
| **CI/CD** | GitHub Actions | Test, build, scan, deploy | Multi-branch |

### 11.3 Flux réseau et sécurité

| Flux | Source → Destination | Port | Security Group |
|------|---------------------|------|----------------|
| Public → ALB | Internet → ALB | 80, 443 | sg_alb |
| ALB → EKS | ALB → Node Group | 8000 | sg_eks |
| EKS → RDS | Pods → PostgreSQL | 5432 | sg_rds |
| EKS → Redis | Pods → ElastiCache | 6379 | sg_elasticache |
| EKS → S3 | Pods → S3 API | 443 | IAM Role |
| Prometheus → Exporters | Prometheus → Targets | 9100,9187,9121 | sg_monitoring |
| Alertmanager → SMTP | Alertmanager → Email | 587 | Outbound |

### 11.4 Schéma d'architecture

Le schéma d'architecture détaillé est disponible dans deux formats :
- **`architecture.drawio`** : Format éditable (draw.io/diagrams.net)
- **`architecture.svg`** : Format image vectoriel pour visualisation directe

**Le schéma montre :**
- VPC avec segmentation en 3 tiers de subnets (Public / Private App / Private DB)
- EKS Cluster avec 3 worker nodes et HPA
- RDS PostgreSQL en Multi-AZ avec chiffrement
- ElastiCache Redis avec replica
- Application Load Balancer avec SSL termination
- Stack de monitoring (Prometheus + Grafana + Alertmanager) - ✅ **Fonctionnel en local**
- Flux CI/CD (GitHub Actions → ECR → EKS)
- Terraform IaC avec S3 backend

> **Statut du monitoring local :** Prometheus, Grafana (http://127.0.0.1:3001) et Alertmanager sont fonctionnels avec Node Exporter pour les métriques système.

## 12. CONTRAINTES ET LIMITES

### 12.1 Contraintes techniques

| Contrainte | Impact | Mitigation |
|------------|--------|------------|
| **Free Tier AWS** | RDS db.t3.micro limité (20 Go, pas de Multi-AZ) | Upgrade quand le trafic le nécessite |
| **EKS AMI** | Version 1.28 non supportée en eu-west-3 pour node group | Utiliser AMI custom ou eksctl |
| **RDS versions** | PostgreSQL 13.x non disponible en eu-west-3 | Utiliser version 15.x validée par AWS |
| **Mémoire Redis** | cache.t3.micro = ~300 Mo | Surveiller via alerte RedisHighMemoryUsage |
| **EKS coût minimum** | ~$73/mois pour le control plane | Accepté pour la certification |

### 12.2 Contraintes organisationnelles

| Contrainte | Description |
|------------|-------------|
| **Équipe réduite** | 1 DevOps, pas de team dédiée 24/7 |
| **Budget limité** | Free Tier AWS + ressources minimales |
| **Délai** | Déploiement fonctionnel en 6 semaines |
| **Certification** | Démontrer les compétences DevOps (IaC, CI/CD, monitoring, sécurité) |

### 12.3 Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Dépassement Free Tier | Moyen | Financier | Alerttes CloudWatch sur coûts |
| Version EKS obsolète | Faible | Technique | Upgrade planifié chaque trimestre |
| Perte de données RDS | Faible | Critique | Backup quotidien + snapshot |
| Fuite de credentials | Faible | Critique | .env gitignoré + GitHub Secrets + scan Trivy |

## 13. JUSTIFICATION DES CHOIX TECHNIQUES

Les choix techniques détaillés sont documentés dans `CHOIX_TECHNIQUES.md`. Résumé :

- **EKS vs ECS** : Portabilité Kubernetes, écosystème Helm/Kustomize, standard industrie
- **ElastiCache Redis vs Memcached** : Persistance, pub/sub (WebSocket), structures avancées
- **RDS PostgreSQL vs Aurora** : Compatibilité Django ORM, Free Tier, maturité
- **Terraform vs CloudFormation** : Multi-cloud, communauté, workflow plan/apply
- **GitHub Actions vs Jenkins** : Intégration native, marketplace, coût gratuit
- **Prometheus/Grafana vs CloudWatch** : Standard CNCF, open source, portabilité
- **Nginx vs Traefik** : Performance static files, recommandation Django

## 14. COHÉRENCE AVEC LES BLOCS REAC

| Bloc REAC | Couverture dans le projet | Preuves |
|-----------|--------------------------|---------|
| **Script** | Dockerfile multi-stage, docker-compose.yml, scripts Terraform | `Dockerfile`, `docker-compose.yml` |
| **IaC** | Terraform complet (VPC, EKS, RDS, ElastiCache, ALB, S3, ECR) | `terraform/main.tf`, `variables.tf` |
| **Sécurité** | Credentials via .env, scan Trivy + Bandit, SG restrictifs, containers non-root | `.env.example`, `.github/workflows/ci-cd.yml` |
| **Mise en production** | CI/CD GitHub Actions + Terraform apply | `.github/workflows/ci-cd.yml` |
| **Environnement de test** | CI lance tests unitaires + intégration, staging via Kustomize overlay | `k8s/overlays/staging/` |
| **Stockage** | RDS PostgreSQL + ElastiCache Redis + S3 media + Docker volumes | `terraform/main.tf` |
| **Containers** | Dockerfile multi-stage + docker-compose 7 services | `Dockerfile`, `docker-compose.yml` |
| **CI/CD** | GitHub Actions multi-branches (test → build → scan → deploy) | `.github/workflows/ci-cd.yml` |
| **Métriques** | Prometheus configuré + 14 alertes définies + Alertmanager | `monitoring/prometheus/`, `monitoring/alertmanager/` |
| **Supervision** | Prometheus + Grafana + Alertmanager + Exporters | `monitoring/` |
| **Anglais** | Non évaluable dans ce livrable | - |
