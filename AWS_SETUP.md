# AWS Setup Guide - MultiServe

## 🔑 Identifiants AWS

### Access Keys (IAM User: Aboudi)
⚠️ **NE PAS COMMITTER LES VRAIES CLÉS** - Utilise GitHub Secrets
```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=eu-west-3
```

### Bucket S3 (Terraform State)
```
S3_STATE_BUCKET=multiserve-terraform-state
DYNAMODB_LOCK_TABLE=multiserve-terraform-locks
```
✅ **Créés avec succès** (Europe - Paris)

---

## 🚀 Architecture AWS - EKS Kubernetes

**Choix retenu : EKS (Kubernetes)** — voir justification dans `CHOIX_TECHNIQUES.md`

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │ Push
         ▼
┌─────────────────┐     ┌──────────────┐
│  GitHub Actions │────▶│  Amazon ECR  │
│   CI/CD Pipeline│     │ (Docker Image)│
│   + Trivy Scan  │     └──────────────┘
└────────┬────────┘
         │ kubectl apply
         ▼
┌─────────────────┐     ┌──────────────┐
│  Amazon EKS     │────▶│   AWS RDS    │
│  (Kubernetes    │     │ (PostgreSQL) │
│   3x t3.medium) │     └──────────────┘
└────────┬────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌──────┐┌──────┐┌──────┐
│ S3   ││Elasti││AWS   │
│Media ││Cache ││Secrets│
│Bucket││Redis ││Mgr   │
└──────┘└──────┘└──────┘
```

### Terraform IaC

L'infrastructure complète est provisionnée via Terraform (`terraform/main.tf`) :

| Ressource | Type | Statut |
|-----------|------|--------|
| **VPC** | 10.0.0.0/16, 6 subnets | ✅ Déployé |
| **EKS Cluster** | v1.28, 3 nodes t3.medium | ✅ Déployé |
| **RDS PostgreSQL** | db.t3.micro, encrypted | ⏳ Version à corriger |
| **ElastiCache Redis** | cache.t3.micro | ✅ Déployé |
| **ALB** | Application Load Balancer | ✅ Configuré |
| **S3** | Media + Terraform State | ✅ Déployé |
| **ECR** | Docker Registry | ✅ Déployé |
| **Security Groups** | ALB/EKS/RDS/Redis/Monitoring | ✅ Déployé |

---

## 🔧 GitHub Secrets à Configurer

Va dans ton repo GitHub → Settings → Secrets and variables → Actions

| Secret | Valeur |
|--------|--------|
| `AWS_ACCESS_KEY_ID` | `your-access-key-id` |
| `AWS_SECRET_ACCESS_KEY` | `your-secret-access-key` |
| `AWS_REGION` | `eu-west-3` |

---

## 📝 Pourquoi EKS et non ECS Fargate ?

EKS (Kubernetes) a été retenu pour trois raisons : **portabilité** — les manifests Kubernetes et le workflow CI/CD sont réutilisables sur GKE, AKS ou tout cluster k8s sans réécriture ; **écosystème** — Helm, Kustomize, HPA et les ServiceMonitors offrent un contrôle granulaire du déploiement, du scaling et du monitoring que ECS ne propose pas nativement ; **compétences** — Kubernetes est le standard industrie (CNCF) et démontre une maîtrise plus large de l'orchestration conteneurisée, ce qui est attendu dans une certification DevOps.

---

## 🎯 Prochaines Étapes

1. ✅ Terraform IaC déployé (VPC, EKS, Redis, S3, ECR)
2. ⏳ Corriger version RDS PostgreSQL compatible eu-west-3
3. ⏳ Réactiver EKS Node Group (AMI compatible)
4. ✅ CI/CD GitHub Actions configuré (test → build → scan Trivy → deploy)
5. ✅ Monitoring Prometheus + Grafana + Alertmanager configuré
