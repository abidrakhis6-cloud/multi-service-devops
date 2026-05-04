# 🚀 Déploiement Automatique MultiServe sur AWS

Ce Terraform configure et déploie automatiquement MultiServe sur l'instance EC2 existante `glo-service`.

---

## 📋 Prérequis

### 1. **Terraform CLI**
Télécharger : https://developer.hashicorp.com/terraform/downloads

### 2. **AWS CLI** (optionnel mais recommandé)
```bash
aws configure
# Entrer:
# - Access Key ID
# - Secret Access Key
# - Region: eu-north-1
# - Output format: json
```

### 3. **Clé SSH**
Avoir `~/.ssh/id_rsa` pour se connecter à l'instance.

---

## 🚀 Commandes de Déploiement

### Étape 1 : Initialiser Terraform
```bash
cd terraform
terraform init
```

### Étape 2 : Vérifier ce qui va être créé
```bash
terraform plan
```

### Étape 3 : Déployer !
```bash
terraform apply
```

> ⚠️ **Important** : Cela va:
> - Créer un Security Group avec ports 80, 443, 8000, 3001
> - Allouer une IP Elastic (fixe)
> - **Installer automatiquement** Docker et MultiServe via SSH

### Étape 4 : Attendre l'installation
L'installation automatique prend **5-10 minutes**.

---

## 📊 Outputs (affichés après `terraform apply`)

```
elastic_ip        = "13.49.xxx.xxx"     🌐 IP Publique Fixe
application_url  = "http://13.49.xxx.xxx:8000"
admin_url        = "http://13.49.xxx.xxx:8000/admin/"
api_url          = "http://13.49.xxx.xxx:8000/api/v1/"
grafana_url      = "http://13.49.xxx.xxx:3001"
ssh_command      = "ssh -i ~/.ssh/id_rsa ubuntu@13.49.xxx.xxx"
status           = "Installation automatique en cours..."
```

---

## 🔧 Commandes Utiles

### Se connecter au serveur
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<IP_AFFICHÉE>
```

### Voir les logs d'installation
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<IP>
sudo tail -f /var/log/multiserve-install.log
```

### Vérifier que Docker tourne
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<IP>
docker ps
```

### Redémarrer l'application
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<IP>
cd /opt/multiserve
docker-compose -f docker-compose.prod.yml restart
```

---

## 🆘 Dépannage

### "Connection refused" sur le navigateur
- Attendre 5-10 minutes que l'installation termine
- Vérifier: `docker ps` doit montrer `multiserve` et `redis`

### Terraform erreur "SSH connection refused"
- Attendre 2-3 minutes que l'instance finisse son boot
- Réessayer: `terraform apply`

### Port 8000 déjà utilisé
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<IP>
docker stop multiserve redis
docker rm multiserve redis
cd /opt/multiserve && docker-compose -f docker-compose.prod.yml up -d
```

---

## 🧹 Nettoyer (supprimer tout)

```bash
cd terraform
terraform destroy
```

⚠️ Cela supprime:
- Le Security Group
- L'IP Elastic
- Mais **PAS** l'instance EC2 (glo-service)

---

## 📞 Support

Voir les logs d'installation sur le serveur:
```bash
sudo cat /var/log/multiserve-install.log
```
