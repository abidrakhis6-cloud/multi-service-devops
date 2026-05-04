#!/bin/bash
# ==========================================
# Script d'Installation Initiale - Production
# multi-serve.fr
# ==========================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# ==========================================
# Configuration
# ==========================================
DOMAIN="multi-serve.fr"
PROJECT_DIR="/opt/multiserve"
GITHUB_REPO="https://github.com/abidrakhis6-cloud/multi-service-devops.git"

clear
echo "=========================================="
echo "🚀 Installation MultiServe Production"
echo "   Domaine: $DOMAIN"
echo "=========================================="
echo ""

# Vérifier si root
if [ "$EUID" -ne 0 ]; then
    error "Ce script doit être exécuté en tant que root (sudo)"
fi

# ==========================================
# 1. Mise à jour du système
# ==========================================
log "📦 Mise à jour du système..."

apt-get update
apt-get upgrade -y
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    nginx-full

# ==========================================
# 2. Installation de Docker
# ==========================================
log "🐳 Installation de Docker..."

if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    usermod -aG docker $SUDO_USER || usermod -aG docker ubuntu || true
    systemctl enable docker
    systemctl start docker
    log "✅ Docker installé"
else
    log "✅ Docker déjà installé"
fi

# Installation de Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log "📦 Installation de Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    log "✅ Docker Compose installé"
else
    log "✅ Docker Compose déjà installé"
fi

# ==========================================
# 3. Création des répertoires
# ==========================================
log "📁 Création des répertoires..."

mkdir -p "$PROJECT_DIR"
mkdir -p /backup
mkdir -p /etc/letsencrypt
mkdir -p /var/log/multiserve

# ==========================================
# 4. Clonage du repository
# ==========================================
log "📥 Téléchargement du projet..."

if [ -d "$PROJECT_DIR/.git" ]; then
    cd "$PROJECT_DIR"
    git pull origin master
else
    git clone "$GITHUB_REPO" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# ==========================================
# 5. Configuration du pare-feu
# ==========================================
log "🛡️ Configuration du pare-feu (UFW)..."

ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 3001/tcp comment 'Grafana' || true

# Activer UFW (sans confirmation)
ufw --force enable
ufw status verbose

# ==========================================
# 6. Configuration Fail2Ban
# ==========================================
log "🛡️ Configuration Fail2Ban..."

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
EOF

systemctl restart fail2ban
systemctl enable fail2ban

# ==========================================
# 7. Création du fichier .env
# ==========================================
log "⚙️ Configuration de l'environnement..."

info "Nous allons créer le fichier de configuration .env"
echo ""

# Générer une clé secrète
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Demander les informations
read -p "Email admin (pour notifications): " ADMIN_EMAIL
read -p "Mot de passe PostgreSQL [auto]: " DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -base64 32)}

read -p "Mot de passe Redis [auto]: " REDIS_PASSWORD
REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 32)}

read -p "Mot de passe Grafana [admin]: " GRAFANA_PASSWORD
GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-admin}

# Créer le fichier .env
cat > "$PROJECT_DIR/.env" << EOF
# ==========================================
# PRODUCTION - multi-serve.fr
# ==========================================

# Django
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=multi-serve.fr,www.multi-serve.fr,localhost,127.0.0.1

# Database
DB_NAME=multiserve_prod
DB_USER=multiserve
DB_PASSWORD=$DB_PASSWORD
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://multiserve:$DB_PASSWORD@db:5432/multiserve_prod

# Redis
REDIS_URL=redis://:redis:$REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=$REDIS_PASSWORD

# Email (SendGrid) - À configurer manuellement après installation
SENDGRID_API_KEY=
DEFAULT_FROM_EMAIL=noreply@multi-serve.fr
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=

# SMS (Twilio) - À configurer manuellement après installation
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# OAuth - À configurer manuellement après installation
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=

# Frontend URL (IMPORTANT)
FRONTEND_URL=https://multi-serve.fr

# Security
CSRF_TRUSTED_ORIGINS=https://multi-serve.fr,https://www.multi-serve.fr
CORS_ALLOWED_ORIGINS=https://multi-serve.fr,https://www.multi-serve.fr
SECURE_SSL_REDIRECT=True

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASSWORD

# ==========================================
# Installation le $(date)
# ==========================================
EOF

log "✅ Fichier .env créé dans $PROJECT_DIR/.env"

# ==========================================
# 8. Permissions
# ==========================================
log "🔐 Configuration des permissions..."

chown -R $SUDO_USER:$SUDO_USER "$PROJECT_DIR" 2>/dev/null || chown -R ubuntu:ubuntu "$PROJECT_DIR" 2>/dev/null || true
chmod +x "$PROJECT_DIR/deploy.sh"

# ==========================================
# 9. Installation initiale des certificats SSL
# ==========================================
log "🔒 Obtention des certificats SSL (Let's Encrypt)..."

# Ouvrir temporairement le port 80 pour certbot
ufw allow 80/tcp

# Obtenir les certificats
certbot certonly --standalone \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --agree-tos \
    --email "$ADMIN_EMAIL" \
    --non-interactive \
    || warn "Échec de l'obtention du certificat - sera réessayé au déploiement"

# ==========================================
# 10. Création du renouvellement automatique SSL
# ==========================================
log "🔄 Configuration du renouvellement SSL automatique..."

cat > /etc/cron.daily/renew-ssl << EOF
#!/bin/bash
certbot renew --quiet --nginx
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T nginx nginx -s reload 2>/dev/null || true
EOF

chmod +x /etc/cron.daily/renew-ssl

# ==========================================
# 11. Premier déploiement
# ==========================================
log "🚀 Premier déploiement..."

cd "$PROJECT_DIR"
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build

sleep 15

# Migrations
docker-compose -f docker-compose.prod.yml exec -T app python manage.py migrate --noinput || warn "Migrations échouées"

# Collecte des statics
docker-compose -f docker-compose.prod.yml exec -T app python manage.py collectstatic --noinput || warn "Collecte des statics échouée"

# Création du superutilisateur
log "📝 Création du superutilisateur Django..."
echo ""
docker-compose -f docker-compose.prod.yml exec app python manage.py createsuperuser

# ==========================================
# 12. Vérification finale
# ==========================================
log "🏥 Vérification de l'installation..."

sleep 5

# Test de santé
if curl -sf -o /dev/null "http://localhost:8000/health/" 2>/dev/null || \
   curl -sf -o /dev/null "https://$DOMAIN/health/" 2>/dev/null; then
    log "✅ Application accessible"
else
    warn "L'application n'est pas encore accessible (peut prendre 1-2 minutes)"
fi

# ==========================================
# Résumé
# ==========================================
echo ""
echo "=========================================="
echo "🎉 INSTALLATION TERMINÉE !"
echo "=========================================="
echo ""
echo -e "${GREEN}URLs de production:${NC}"
echo "  🌐 Site web:     https://$DOMAIN"
echo "  🔧 API:          https://$DOMAIN/api/v1/"
echo "  ⚙️  Admin Django: https://$DOMAIN/admin/"
echo "  📊 Grafana:       https://$DOMAIN:3001"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo "  1. Configurer SendGrid:     nano $PROJECT_DIR/.env (SENDGRID_API_KEY)"
echo "  2. Configurer Twilio:       nano $PROJECT_DIR/.env (TWILIO_*)"
echo "  3. Configurer Google OAuth: https://console.cloud.google.com/apis/credentials"
echo "  4. Configurer Facebook:     https://developers.facebook.com/apps"
echo "  5. Redémarrer:              cd $PROJECT_DIR && ./deploy.sh"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo "  Logs:    docker-compose -f docker-compose.prod.yml logs -f app"
echo "  Restart: docker-compose -f docker-compose.prod.yml restart"
echo "  Update:  cd $PROJECT_DIR && git pull && ./deploy.sh"
echo ""
echo "=========================================="
echo ""

exit 0
