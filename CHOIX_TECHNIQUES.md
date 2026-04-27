# MultiServe - Justification des Choix Techniques

## 1. Orchestration : Pourquoi EKS et non ECS ?

| Critère | EKS (choisi) | ECS | Justification |
|---------|-------------|-----|---------------|
| **Portabilité** | Standard Kubernetes (k8s) | Propriétaire AWS | EKS permet de migrer vers GKE/AKS sans réécriture |
| **Écosystème** | Helm, Kustomize, Istio, ArgoCD | Task Definitions AWS | L'écosystème K8s est plus riche et standard industrie |
| **Auto-scaling** | HPA + Cluster Autoscaler | Service Auto Scaling | HPA K8s offre un contrôle plus granulaire |
| **CI/CD** | kubectl apply, Helm, GitOps | AWS CLI, Copilot | K8s s'intègre nativement avec les pipelines GitOps |
| **Communauté** | CNCF, large communauté | AWS uniquement | EKS bénéficie de la communauté Kubernetes mondiale |
| **Multi-cloud** | Possible (GKE, AKS) | Verrouillé AWS | EKS prépare une stratégie multi-cloud future |

**Décision** : EKS pour la portabilité, l'écosystème riche et l'alignement avec les standards du marché.

## 2. Cache : Pourquoi ElastiCache Redis ?

| Critère | ElastiCache Redis (choisi) | Memcached | DynamoDB DAX | Justification |
|---------|---------------------------|-----------|--------------|---------------|
| **Persistance** | Oui (AOF/RDB) | Non | Non | Redis persiste les données même en cas de redémarrage |
| **Pub/Sub** | Oui | Non | Non | Nécessaire pour Django Channels (WebSocket temps réel) |
| **Structures** | Hash, List, Set, Sorted Set | Key-Value uniquement | Key-Value | Structures avancées pour sessions, cache, files d'attente |
| **Haute disponibilité** | Multi-AZ + Replica | Non | Oui | Redis supporte le failover automatique |
| **Sessions Django** | Natif | Limité | Non | Backend de sessions Django recommandé pour Redis |

**Décision** : ElastiCache Redis pour la persistance, le pub/sub (WebSocket), et les structures de données avancées.

## 3. Base de données : Pourquoi RDS PostgreSQL ?

| Critère | RDS PostgreSQL (choisi) | Aurora PostgreSQL | DynamoDB | Justification |
|---------|------------------------|-------------------|----------|---------------|
| **Compatibilité Django** | ORM natif | Compatible | Non | Django ORM supporte PostgreSQL nativement |
| **ACID** | Oui | Oui | Éventuel | Transactions fiables pour commandes et paiements |
| **JSON Support** | JSONB | JSONB | Natif | Stockage flexible pour produits variables |
| **Coût** | Modéré (Free Tier) | Élevé | Pay per request | RDS t3.micro éligible Free Tier AWS |
| **Recherche** | Full-text search | Full-text search | Scan | Recherche textuelle intégrée pour catalogue |

**Décision** : RDS PostgreSQL pour la maturité Django, le support ACID, et l'éligibilité Free Tier.

## 4. Infrastructure as Code : Pourquoi Terraform ?

| Critère | Terraform (choisi) | CloudFormation | Pulumi | CDK | Justification |
|---------|-------------------|----------------|--------|-----|---------------|
| **Multi-cloud** | Oui | AWS uniquement | Oui | AWS uniquement | Terraform est cloud-agnostic |
| **Langage** | HCL déclaratif | YAML/JSON | Python/JS | Python/TS | HCL est lisible et déclaratif |
| **State** | S3 + DynamoDB (remote) | Automatique | Automatique | Automatique | State management explicite et contrôlable |
| **Communauté** | Très large | AWS uniquement | Croissante | AWS | Plus de modules et d'exemples disponibles |
| **Plan** | `terraform plan` | Change sets | Preview | Diff | Visualisation des changements avant application |

**Décision** : Terraform pour la portabilité multi-cloud, la communauté, et le workflow plan/apply.

## 5. CI/CD : Pourquoi GitHub Actions ?

| Critère | GitHub Actions (choisi) | GitLab CI | Jenkins | CircleCI | Justification |
|---------|------------------------|-----------|---------|----------|---------------|
| **Intégration** | Native GitHub | Native GitLab | Plugin | API | Le code est hébergé sur GitHub |
| **Marketplace** | 20 000+ actions | Templates limités | Plugins | Orbs | Réutilisation massive d'actions |
| **Coût** | Gratuit (public/2000min privé) | Gratuit (limité) | Self-hosted | Payant | GitHub Actions gratuit pour les dépôts publics |
| **Configuration** | YAML dans `.github/` | `.gitlab-ci.yml` | Jenkinsfile | `.circleci/` | Configuration versionnée avec le code |

**Décision** : GitHub Actions pour l'intégration native, le marketplace riche, et le coût.

## 6. Monitoring : Pourquoi Prometheus + Grafana ?

| Critère | Prometheus + Grafana (choisi) | CloudWatch | Datadog | Justification |
|---------|-------------------------------|------------|---------|---------------|
| **Coût** | Gratuit (OSS) | Inclus AWS | Payant | Prometheus/Grafana sont open source |
| **Alerting** | Alertmanager natif | Alarms | Monitors | Alertmanager offre un routing sophistiqué |
| **Dashboards** | Communauté massive | Basique | Riche | Grafana a la plus grande bibliothèque de dashboards |
| **Portabilité** | Standard industrie | AWS uniquement | SaaS | Prometheus est le standard CNCF de fait |
| **Pull model** | Oui (scrape) | Push | Push/Agent | Pull model plus simple et plus fiable |

**Décision** : Prometheus + Grafana pour le standard industrie, le coût, et la portabilité.

## 7. Reverse Proxy : Pourquoi Nginx ?

| Critère | Nginx (choisi) | Traefik | HAProxy | Envoy | Justification |
|---------|---------------|---------|---------|-------|---------------|
| **Performance** | Très haute | Bonne | Haute | Haute | Nginx est le standard pour servir Django |
| **SSL Termination** | Natif | Automatique | Natif | Natif | SSL/TLS simple et bien documenté |
| **Static Files** | Excellent | Non prévu | Non | Non | Nginx sert les fichiers static/media efficacement |
| **Intégration Django** | Standard | Docker-only | Général | K8s | Nginx est la recommandation officielle Django |

**Décision** : Nginx pour la performance, le service de fichiers statiques, et la recommandation Django.

## 8. Sécurité : Mesures Implémentées

| Couche | Mesure | Implémentation |
|--------|--------|---------------|
| **Code** | Scan vulnérabilités | Bandit (Python) + Trivy (Docker) dans CI/CD |
| **Images** | Scan CVE | Trivy action avec seuil CRITICAL/HIGH |
| **Secrets** | Pas de credentials en clair | `.env` (gitignoré) + GitHub Secrets + AWS Secrets Manager |
| **Réseau** | Segmentation | VPC + Security Groups par couche (ALB/App/DB/Redis) |
| **Containers** | Non-root | Utilisateur `django` (UID 1000) dans Dockerfile |
| **Base de données** | Chiffrement | RDS gp3 encrypted at rest + TLS in transit |
| **Cache** | Authentification | Redis `requirepass` obligatoire |
