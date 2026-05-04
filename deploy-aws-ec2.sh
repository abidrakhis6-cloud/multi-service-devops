#!/bin/bash
# ==========================================
# Script de déploiement sur EC2 existante
# IP: 13.49.183.244
# ==========================================

set -e

IP="13.49.183.244"
SSH_KEY="~/.ssh/id_rsa"  # Modifier selon ta clé

echo "🚀 Déploiement MultiServe sur AWS EC2 ($IP)"
echo "=========================================="

# Vérifier la connexion SSH
echo "🔌 Test de connexion SSH..."
ssh -o ConnectTimeout=10 -i "$SSH_KEY" "ubuntu@$IP" "echo '✅ Connexion SSH OK'" || {
    echo "❌ Erreur: Impossible de se connecter en SSH"
    echo "Vérifie:"
    echo "  1. La clé SSH: $SSH_KEY"
    echo "  2. Le Security Group autorise le port 22"
    echo "  3. L'instance est en cours d'exécution"
    exit 1
}

# Copier les fichiers
echo "📁 Copie des fichiers sur le serveur..."
ssh -i "$SSH_KEY" "ubuntu@$IP" "mkdir -p /opt/multiserve"

# Rsync des fichiers (exclure venv, .git, etc.)
rsync -avz --exclude='venv' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    -e "ssh -i $SSH_KEY" \
    ./ "ubuntu@$IP:/opt/multiserve/"

# Installation et démarrage
echo "🔧 Installation sur le serveur..."
ssh -i "$SSH_KEY" "ubuntu@$IP" << 'REMOTE_COMMANDS'
    cd /opt/multiserve
    
    # Rendre les scripts exécutables
    chmod +x *.sh
    
    # Exécuter le setup si c'est la première fois
    if [ ! -f ".setup-done" ]; then
        echo "🆕 Premier déploiement - Installation complète..."
        sudo ./setup-production.sh 2>&1 | tee /var/log/multiserve-setup.log
        touch .setup-done
    else
        echo "🔄 Mise à jour - Redémarrage des services..."
        sudo ./deploy.sh 2>&1 | tee /var/log/multiserve-deploy.log
    fi
    
    echo "✅ Terminé!"
REMOTE_COMMANDS

echo ""
echo "=========================================="
echo "🎉 Déploiement terminé!"
echo "=========================================="
echo ""
echo "🔗 URLs:"
echo "  Application: http://$IP:8000"
echo "  Admin:       http://$IP:8000/admin/"
echo "  API:         http://$IP:8000/api/v1/"
echo "  Grafana:     http://$IP:3001"
echo ""
echo "🔧 Commandes utiles:"
echo "  SSH:  ssh -i ~/.ssh/id_rsa ubuntu@$IP"
echo "  Logs: ssh -i ~/.ssh/id_rsa ubuntu@$IP 'docker logs -f multiserve'"
echo ""
