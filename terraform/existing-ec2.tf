# ==========================================
# MultiServe - Déploiement AUTOMATIQUE COMPLET
# Instance: glo-service (i-004c97f25915c1f7e)
# Région: eu-north-1 (Stockholm)
# ==========================================

# Data source pour récupérer l'instance existante
data "aws_instance" "glo_service" {
  filter {
    name   = "tag:Name"
    values = ["glo-service"]
  }

  filter {
    name   = "instance-state-name"
    values = ["running"]
  }
}

# Data source pour le VPC
data "aws_vpc" "existing" {
  default = false
  
  filter {
    name   = "tag:Name"
    values = ["glo-vpc"]
  }
}

# Data source pour le subnet
data "aws_subnet" "public" {
  filter {
    name   = "tag:Name"
    values = ["glo-subnet-public"]
  }
  
  vpc_id = data.aws_vpc.existing.id
}

# Security Group pour MultiServe (ajouter à l'instance existante)
resource "aws_security_group" "multiserve_existing" {
  name_prefix = "multiserve-sg-existing-"
  description = "Security group for MultiServe application - existing instance"
  vpc_id      = data.aws_vpc.existing.id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP - Nginx"
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS - SSL"
  }

  # Django Application (direct)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Django Application"
  }

  # Grafana Monitoring
  ingress {
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Grafana Dashboard"
  }

  # Redis (interne uniquement - à restreindre)
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]
    description = "Redis - Internal only"
  }

  # Sortie complète
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "multiserve-sg-production"
    Project = "multiserve"
  }
}

# Attacher le Security Group à l'instance existante
resource "aws_network_interface_sg_attachment" "multiserve_sg_attach" {
  security_group_id    = aws_security_group.multiserve_existing.id
  network_interface_id = data.aws_instance.glo_service.network_interface_id
}

# Elastic IP (IP fixe publique)
resource "aws_eip" "multiserve" {
  instance = data.aws_instance.glo_service.id
  domain   = "vpc"
  
  tags = {
    Name = "multiserve-eip-production"
  }
  
  depends_on = [data.aws_instance.glo_service]
}

# ==========================================
# USER-DATA : Installation AUTOMATIQUE
# ==========================================

locals {
  user_data = <<-EOF
#!/bin/bash
# ==========================================
# MultiServe - Installation Automatique
# ==========================================
set -e

LOG_FILE="/var/log/multiserve-install.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "🚀 MultiServe Auto-Install - $(date)"
echo "=========================================="

# Fonction de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Attendre que le système soit prêt
log "⏳ Attente du système..."
sleep 30

# Mise à jour système
log "📦 Mise à jour du système..."
apt-get update -y
apt-get upgrade -y

# Installation Docker
log "🐳 Installation de Docker..."
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sh /tmp/get-docker.sh
rm /tmp/get-docker.sh

usermod -aG docker ubuntu
systemctl enable docker
systemctl start docker

# Installation Docker Compose
log "📦 Installation de Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Installation outils supplémentaires
log "🔧 Installation des outils..."
apt-get install -y git curl wget htop ufw fail2ban

# Création du répertoire application
log "📁 Création du répertoire..."
mkdir -p /opt/multiserve
cd /opt/multiserve

# Clone du repository
log "📥 Téléchargement du code..."
if [ -d ".git" ]; then
    log "Repository existant, mise à jour..."
    git pull origin master
else
    git clone https://github.com/abidrakhis6-cloud/multi-service-devops.git .
fi

# Permissions
chown -R ubuntu:ubuntu /opt/multiserve

# Génération de la clé secrète
SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n')
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Création du fichier .env
log "⚙️ Configuration de l'environnement..."
cat > /opt/multiserve/.env << ENVFILE
# ==========================================
# MultiServe - Configuration Auto-Générée (LOCAL/IP)
# ==========================================
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1
FRONTEND_URL=http://$PUBLIC_IP:8000

# Database SQLite (rapide pour démarrer)
DATABASE_URL=sqlite:///db.sqlite3

# Redis local
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis_secure_$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 16)

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# TODO: Configurer manuellement après déploiement
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=

# Local/IP only (no domain)
CSRF_TRUSTED_ORIGINS=http://$PUBLIC_IP:8000,http://localhost:8000
CORS_ALLOWED_ORIGINS=http://$PUBLIC_IP:8000,http://localhost:8000
ENVFILE

# Configuration Fail2Ban
log "🛡️ Configuration Fail2Ban..."
cat > /etc/fail2ban/jail.local << 'FAIL2BAN'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
FAIL2BAN

systemctl restart fail2ban
systemctl enable fail2ban

# Pare-feu UFW
log "🔥 Configuration du pare-feu..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8000/tcp comment 'Django'
ufw allow 3001/tcp comment 'Grafana'
ufw --force enable

# Lancement de l'application
log "🚀 Lancement de MultiServe..."
cd /opt/multiserve

# Démarrer Redis
docker run -d --name redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine \
  redis-server --requirepass $(grep REDIS_PASSWORD .env | cut -d= -f2)

# Build et lancement de l'application
log "🔨 Construction de l'image..."
docker build -t multiserve:latest .

log "▶️ Démarrage des services..."
docker run -d --name multiserve \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /opt/multiserve:/app \
  --link redis:redis \
  -e DJANGO_SETTINGS_MODULE=config.settings \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e REDIS_URL=redis://redis:6379/0 \
  -e SECRET_KEY=$SECRET_KEY \
  multiserve:latest \
  sh -c "python manage.py migrate --noinput && \
         python manage.py collectstatic --noinput && \
         python manage.py createsuperuser --noinput --username admin --email admin@multiserve.fr || true && \
         gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"

# Script de health check
log "🏥 Configuration du health check..."
cat > /usr/local/bin/multiserve-health.sh << 'HEALTH'
#!/bin/bash
if ! curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "[$(date)] Application non accessible - Redémarrage..." >> /var/log/multiserve-health.log
    cd /opt/multiserve && docker-compose restart
fi
HEALTH
chmod +x /usr/local/bin/multiserve-health.sh

# Cron pour health check
log "⏰ Configuration des tâches planifiées..."
echo "*/2 * * * * root /usr/local/bin/multiserve-health.sh" > /etc/cron.d/multiserve-health
echo "0 3 * * * root cd /opt/multiserve && docker exec multiserve python manage.py clearsessions" > /etc/cron.d/multiserve-maintenance

# Créer le flag d'installation
log "✅ Installation terminée !"
touch /opt/multiserve/.auto-install-done

# Log final
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "" >> /var/log/multiserve-install.log
echo "==========================================" >> /var/log/multiserve-install.log
echo "🎉 MultiServe déployé avec succès !" >> /var/log/multiserve-install.log
echo "📱 URL: http://$PUBLIC_IP:8000" >> /var/log/multiserve-install.log
echo "🔧 Admin: http://$PUBLIC_IP:8000/admin/" >> /var/log/multiserve-install.log
echo "📊 Grafana: http://$PUBLIC_IP:3001" >> /var/log/multiserve-install.log
echo "🔑 SSH: ssh -i ~/.ssh/id_rsa ubuntu@$PUBLIC_IP" >> /var/log/multiserve-install.log
echo "==========================================" >> /var/log/multiserve-install.log
EOF
}

# ==========================================
# User Data pour redémarrage avec installation auto
# ==========================================

resource "null_resource" "multiserve_setup" {
  triggers = {
    instance_id = data.aws_instance.glo_service.id
    user_data   = local.user_data
  }

  provisioner "local-exec" {
    command = <<-EOT
      echo "⏳ Attente de l'instance..."
      sleep 10
      
      # Copier le script via SSH
      echo "📤 Envoi du script d'installation..."
      ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
          -i ~/.ssh/id_rsa \
          ubuntu@${aws_eip.multiserve.public_ip} \
          "echo '${local.user_data}' | sudo tee /tmp/setup.sh && sudo chmod +x /tmp/setup.sh"
      
      # Exécuter le script
      echo "🚀 Exécution de l'installation..."
      ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
          -i ~/.ssh/id_rsa \
          ubuntu@${aws_eip.multiserve.public_ip} \
          "sudo /tmp/setup.sh" || true
      
      echo "✅ Déploiement initié !"
      echo "   URL: http://${aws_eip.multiserve.public_ip}:8000"
      echo "   L'installation continue en arrière-plan (~5-10 minutes)"
    EOT
  }

  depends_on = [aws_eip.multiserve, aws_security_group.multiserve_existing]
}
output "elastic_ip" {
  description = "🌐 IP Publique Fixe (utilise celle-ci !)"
  value       = aws_eip.multiserve.public_ip
}

output "application_url" {
  description = "🔗 URL de l'application"
  value       = "http://${aws_eip.multiserve.public_ip}:8000"
}

output "admin_url" {
  description = "⚙️ URL Admin Django"
  value       = "http://${aws_eip.multiserve.public_ip}:8000/admin/"
}

output "api_url" {
  description = "🔧 URL API"
  value       = "http://${aws_eip.multiserve.public_ip}:8000/api/v1/"
}

output "grafana_url" {
  description = "📊 URL Grafana"
  value       = "http://${aws_eip.multiserve.public_ip}:3001"
}

output "ssh_command" {
  description = "💻 Commande SSH"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_eip.multiserve.public_ip}"
}

output "status" {
  description = "📋 Status du déploiement"
  value       = "Installation automatique en cours. Attendre 5-10 minutes, puis accéder à: http://${aws_eip.multiserve.public_ip}:8000"
}
