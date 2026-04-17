# AWS Setup Guide - MultiServe

## 🔑 Vos Identifiants AWS

### Access Keys (IAM User: Aboudi)
⚠️ **NE PAS COMMITTE LES VRAIES CLÉS** - Utilise GitHub Secrets
```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=eu-west-3
```

### Bucket S3
```
AWS_STORAGE_BUCKET_NAME=multiserve-user-data
```
✅ **Créé avec succès** (Europe - Paris)

---

## 📋 Les ARNs - Lesquels utiliser ?

### ❌ ARN Utilisateur IAM (PAS utilisé pour GitHub Actions)
```
arn:aws:iam::987569578101:user/Aboudi
```
> C'est juste l'identifiant de ton utilisateur. **On ne l'utilise pas** dans le code.

### ❌ ARN Instance EC2 (PAS utilisé pour GitHub Actions)
```
arn:aws:ec2:eu-north-1:987569578101:instance/i-004c97f25915c1f7e
```
> C'est l'identifiant de ton serveur virtuel existant. **On n'en a pas besoin** car on déploie sur **ECS Fargate** (serverless), pas sur EC2.

### ✅ Ce qu'on utilise pour GitHub Actions
On utilise les **Access Keys directement** dans GitHub Secrets. Pas besoin de Role ARN !

---

## 🔧 GitHub Secrets à Configurer

Va dans ton repo GitHub → Settings → Secrets and variables → Actions

| Secret | Valeur |
|--------|--------|
| `AWS_ACCESS_KEY_ID` | `your-access-key-id` |
| `AWS_SECRET_ACCESS_KEY` | `your-secret-access-key` |
| `AWS_REGION` | `eu-west-3` |
| `AWS_STORAGE_BUCKET_NAME` | `multiserve-user-data` |

---

## 🚀 Architecture AWS

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │ Push
         ▼
┌─────────────────┐     ┌──────────────┐
│  GitHub Actions │────▶│  Amazon ECR  │
│   CI/CD Pipeline│     │ (Docker Image)│
└─────────────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   Amazon ECS    │────▶│   AWS RDS    │
│   (Fargate)     │     │ (PostgreSQL) │
│  Ton Application│     └──────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  Amazon S3      │◀───│ AWS Secrets  │
│ (User Data JSON)│     │  Manager     │
└─────────────────┘     └──────────────┘
```

---

## 📦 Services AWS Utilisés

| Service | Usage | Statut |
|---------|-------|--------|
| **IAM** | Gestion des accès | ✅ User + Keys créés |
| **S3** | Stockage données utilisateurs | ✅ Bucket créé |
| **ECR** | Registry Docker | ⏳ À créer |
| **ECS** | Hébergement conteneurs | ⏳ À créer |
| **RDS** | Base de données PostgreSQL | ⏳ À créer |
| **ElastiCache** | Cache Redis | ⏳ À créer |

---

## 📝 Récapitulatif

- ✅ **Access Keys** : Utilisées pour GitHub Actions
- ✅ **Bucket S3** : `multiserve-user-data` créé
- ❌ **Role ARN** : **PAS nécessaire** avec les Access Keys
- ❌ **EC2 ARN** : **PAS utilisé** (on utilise ECS, pas EC2)

---

## 🎯 Prochaines Étapes

1. ✅ Ajouter les 4 secrets dans GitHub
2. ⏳ Créer ECR Repository
3. ⏳ Créer ECS Cluster + Service
4. ⏳ Créer RDS PostgreSQL
5. 🚀 Push sur main → Déploiement automatique !
