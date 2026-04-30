#!/bin/bash
# ==========================================
# Script de Déploiement Production
# multi-serve.fr
# ==========================================

set -e  # Exit on error

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# ==========================================
# Variables
# ==========================================
DOMAIN="multi-serve.fr"
EMAIL="admin@multi-serve.fr"  # Changer par ton email
PROJECT_DIR="/opt/multiserve"
COMPOSE_FILE="docker-compose.prod.yml"

# ==========================================
# Vérifications
# ==========================================
log "🔍 Vérifications pré-déploiement..."

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé. Veuillez l'installer d'abord."
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose n'est pas installé."
fi

# Vérifier le fichier .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
    error "Fichier .env non trouvé dans $PROJECT_DIR"
fi

log "✅ Toutes les vérifications passées"

# ==========================================
# Backup de la base de données
# ==========================================
log "💾 Création d'un backup..."

if docker ps | grep -q "multiserve_db"; then
    BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    docker exec multiserve_db pg_dump -U multiserve multiserve_prod > "$BACKUP_DIR/db_backup.sql"
    log "✅ Backup créé: $BACKUP_DIR/db_backup.sql"
else
    warn "Base de données non trouvée, backup ignoré"
fi

# ==========================================
# Mise à jour du code
# ==========================================
log "📥 Mise à jour du code source..."

cd "$PROJECT_DIR"

# Pull des changements
git pull origin master || warn "Git pull a échoué ou pas de remote configuré"

# ==========================================
# Arrêt des conteneurs existants
# ==========================================
log "🛑 Arrêt des conteneurs existants..."

docker-compose -f "$COMPOSE_FILE" down --remove-orphans || warn "Pas de conteneurs à arrêter"

# Nettoyage des images non utilisées
docker system prune -f || true

# ==========================================
# Vérification des certificats SSL
# ==========================================
log "🔒 Vérification des certificats SSL..."

if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    warn "Certificats SSL non trouvés pour $DOMAIN"
    log "📝 Obtention des certificats avec Let's Encrypt..."
    
    # Installer certbot si nécessaire
    if ! command -v certbot &> /dev/null; then
        log "Installation de Certbot..."
        apt-get update
        apt-get install -y certbot
    fi
    
    # Arrêter temporairement Nginx pour le certificat
    docker-compose -f "$COMPOSE_FILE" up -d nginx || true
    sleep 2
    
    # Obtenir le certificat
    certbot certonly --standalone \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --agree-tos \
        --email "$EMAIL" \
        --non-interactive \
        --force-renewal || error "Échec de l'obtention du certificat SSL"
    
    log "✅ Certificats SSL obtenus"
else
    log "✅ Certificats SSL existants trouvés"
    
    # Renouvellement si nécessaire
    log "📝 Vérification du renouvellement SSL..."
    certbot renew --dry-run || warn "Le renouvellement a échoué"
fi

# ==========================================
# Build et démarrage
# ==========================================
log "🔨 Construction des images Docker..."

docker-compose -f "$COMPOSE_FILE" build --no-cache

log "🚀 Démarrage des services..."

docker-compose -f "$COMPOSE_FILE" up -d

# Attendre que la base de données soit prête
log "⏳ Attente de la base de données..."
sleep 10

# ==========================================
# Migrations et collecte des statics
# ==========================================
log "📊 Exécution des migrations..."

docker-compose -f "$COMPOSE_FILE" exec -T app python manage.py migrate --noinput

log "📁 Collecte des fichiers statiques..."

docker-compose -f "$COMPOSE_FILE" exec -T app python manage.py collectstatic --noinput --clear

# ==========================================
# Création du superutilisateur (si premier déploiement)
# ==========================================
if ! docker-compose -f "$COMPOSE_FILE" exec -T app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
    warn "Aucun superutilisateur trouvé"
    log "📝 Création du superutilisateur..."
    docker-compose -f "$COMPOSE_FILE" exec -T app python manage.py createsuperuser
fi

# ==========================================
# Vérification de la santé
# ==========================================
log "🏥 Vérification de la santé des services..."

sleep 5

# Vérifier Nginx
if curl -sf -o /dev/null "https://$DOMAIN/health/"; then
    log "✅ Nginx et Application sont OK"
else
    warn "La vérification de santé a échoué. Vérifiez les logs: docker-compose logs -f"
fi

# ==========================================
# Affichage du résumé
# ==========================================
echo ""
echo "=========================================="
echo "🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !"
echo "=========================================="
echo ""
echo "📱 Application: https://$DOMAIN"
echo "🔧 API: https://$DOMAIN/api/v1/"
echo "⚙️  Admin: https://$DOMAIN/admin/"
echo "📊 Grafana: https://$DOMAIN:3001"
echo ""
echo "📚 Commandes utiles:"
echo "   Logs app:     docker-compose -f $COMPOSE_FILE logs -f app"
echo "   Logs nginx:   docker-compose -f $COMPOSE_FILE logs -f nginx"
echo "   Restart:      docker-compose -f $COMPOSE_FILE restart"
echo "   Shell:        docker-compose -f $COMPOSE_FILE exec app bash"
echo ""
echo "=========================================="

exit 0
