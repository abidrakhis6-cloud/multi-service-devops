# MultiServe - Justification des Choix Techniques

## 1. Orchestration : Pourquoi EKS et non ECS ?

EKS (Kubernetes) a été retenu pour trois raisons : **portabilité** — les manifests Kubernetes et le workflow CI/CD sont réutilisables sur GKE, AKS ou tout cluster k8s sans réécriture ; **écosystème** — Helm, Kustomize, HPA et les ServiceMonitors offrent un contrôle granulaire du déploiement, du scaling et du monitoring que ECS ne propose pas nativement ; **compétences** — Kubernetes est le standard industrie (CNCF) et démontre une maîtrise plus large de l'orchestration conteneurisée, ce qui est attendu dans une certification DevOps.

| Critère | EKS (choisi) | ECS Fargate | EC2 | Justification |
|---------|-------------|-------------|-----|---------------|
| **Portabilité** | Standard K8s | Propriétaire AWS | N/A | EKS permet de migrer vers GKE/AKS |
| **Écosystème** | Helm, Kustomize, Istio | Task Definitions | AMI | K8s offre un contrôle granulaire |
| **Auto-scaling** | HPA + Cluster Autoscaler | Service Auto Scaling | ASG | HPA plus précis sur les métriques |
| **Monitoring** | ServiceMonitor + Prom Operator | CloudWatch + Container Insights | CloudWatch | K8s intègre nativement Prometheus |
| **CI/CD** | kubectl, Helm, GitOps | AWS CLI, Copilot | SSH/Ansible | GitOps est le standard DevOps |
| **Coût** | ~$73/mois control plane | Pay per task | Pay per instance | ECS moins cher mais moins flexible |

## 2. Cache : Pourquoi ElastiCache Redis ?

| Critère | ElastiCache Redis (choisi) | Memcached | DynamoDB DAX | Justification |
|---------|---------------------------|-----------|--------------|---------------|
| **Persistance** | Oui (AOF/RDB) | Non | Non | Redis persiste les données |
| **Pub/Sub** | Oui | Non | Non | Nécessaire pour Django Channels (WebSocket) |
| **Structures** | Hash, List, Set, Sorted Set | Key-Value | Key-Value | Structures avancées pour sessions/cache |
| **Haute disponibilité** | Multi-AZ + Replica | Non | Oui | Redis supporte le failover |

## 3. Base de données : Pourquoi RDS PostgreSQL ?

| Critère | RDS PostgreSQL (choisi) | Aurora | DynamoDB | Justification |
|---------|------------------------|--------|----------|---------------|
| **Compatibilité Django** | ORM natif | Compatible | Non | Django ORM supporte PostgreSQL |
| **ACID** | Oui | Oui | Éventuel | Transactions fiables pour paiements |
| **Coût** | Free Tier (db.t3.micro) | Élevé | Pay/request | RDS éligible Free Tier |

## 4. Infrastructure as Code : Pourquoi Terraform ?

| Critère | Terraform (choisi) | CloudFormation | Justification |
|---------|-------------------|----------------|---------------|
| **Multi-cloud** | Oui | AWS uniquement | Portabilité |
| **State** | S3 + DynamoDB (contrôlé) | Automatique | State management explicite |
| **Plan** | `terraform plan` | Change sets | Visualisation avant application |

## 5. CI/CD : Pourquoi GitHub Actions ?

| Critère | GitHub Actions (choisi) | Jenkins | Justification |
|---------|------------------------|---------|---------------|
| **Intégration** | Native GitHub | Plugin | Code hébergé sur GitHub |
| **Marketplace** | 20 000+ actions | Plugins | Réutilisation massive |
| **Coût** | Gratuit (public) | Self-hosted | Coût nul |

## 6. Monitoring : Pourquoi Prometheus + Grafana ?

| Critère | Prometheus + Grafana (choisi) | CloudWatch | Justification |
|---------|-------------------------------|------------|---------------|
| **Coût** | Gratuit (OSS) | Inclus AWS | Open source |
| **Alerting** | Alertmanager natif | Alarms | Routing sophistiqué |
| **Portabilité** | Standard CNCF | AWS uniquement | Standard industrie |

### Monitoring sur EKS : Comment Prometheus scrape-t-il les conteneurs ?

En production EKS, Prometheus est déployé dans le cluster via la Prometheus Operator. Le scraping fonctionne ainsi :

1. **ServiceMonitor** : Un objet K8s (`k8s/base/servicemonitor.yaml`) déclare automatiquement les cibles à scraper en sélectionnant les pods par labels (`app: multiserve`). Pas de configuration manuelle.
2. **kubernetes_sd_configs** : Prometheus découvre les pods via l'API Kubernetes (voir `monitoring/prometheus/prometheus.yml` section `kubernetes-pods`). Les pods annotés avec `prometheus.io/scrape: "true"` sont automatiquement scrapés.
3. **CloudWatch comme complément** : Container Insights fournit les métriques infrastructure (CPU/mémoire node) que Prometheus ne voit pas, via l'exporter `cloudwatch-exporter`.

En local (docker-compose), les cibles sont définies via `static_configs` avec les noms DNS Docker (`app:8000`, `node-exporter:9100`).

## 7. Reverse Proxy : Pourquoi Nginx ?

| Critère | Nginx (choisi) | Traefik | Justification |
|---------|---------------|---------|---------------|
| **Static Files** | Excellent | Non prévu | Nginx sert les fichiers statiques |
| **Intégration Django** | Standard | Docker-only | Recommandation officielle Django |

## 8. Sécurité : Mesures Implémentées

| Couche | Mesure | Implémentation |
|--------|--------|---------------|
| **Code** | Scan vulnérabilités | Bandit + Trivy dans CI/CD |
| **Secrets** | Pas de credentials en clair | `.env` (gitignoré) + GitHub Secrets + AWS Secrets Manager |
| **Réseau** | Segmentation | VPC + Security Groups par couche (ALB seul en 0.0.0.0/0:80,443) |
| **Containers** | Non-root | Utilisateur `django` (UID 1000) dans Dockerfile |
| **Base de données** | Chiffrement | RDS gp3 encrypted at rest + TLS in transit |
| **Cache** | Authentification | Redis `requirepass` obligatoire |
