#!/bin/bash
# ==========================================
# Script de test des alertes Prometheus
# MultiServe - Session Juin-Juillet 2026
# Auteur: ABID RAKHIS AHMAT
# ==========================================

set -e

echo "=========================================="
echo "🧪 TEST DES ALERTES PROMETHEUS"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier que Prometheus est accessible
echo "1️⃣  Vérification de Prometheus..."
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus est accessible${NC}"
else
    echo -e "${RED}❌ Prometheus n'est pas accessible sur localhost:9090${NC}"
    echo "    Démarrez d'abord: docker-compose up -d prometheus"
    exit 1
fi

echo ""
echo "2️⃣  Vérification des règles d'alertes..."

# Vérifier que les règles sont chargées
RULES_COUNT=$(curl -s http://localhost:9090/api/v1/rules | grep -o '"name":"[^"]*"' | wc -l)
echo "    📊 Nombre de groupes de règles chargés: $RULES_COUNT"

# Afficher les alertes actives
echo ""
echo "3️⃣  Alertes actuellement actives:"
curl -s http://localhost:9090/api/v1/alerts | python3 -m json.tool 2>/dev/null | grep -E '"labels"|"annotations"|"state"' | head -20 || echo "    Aucune alerte active"

echo ""
echo "4️⃣  Test de l'endpoint Alertmanager..."
if curl -s http://localhost:9093/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Alertmanager est accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Alertmanager n'est pas accessible sur localhost:9093${NC}"
fi

echo ""
echo "5️⃣  Simulation d'une alerte (test manuel)..."
echo "    Pour tester une alerte de bout en bout:"
echo ""
echo "    🔥 Méthode 1 - Arrêter un service:"
echo "       docker-compose stop app"
echo "       # Attendre 1 minute, l'alerte 'DjangoDown' doit se déclencher"
echo "       docker-compose start app"
echo ""
echo "    🔥 Méthode 2 - Stress test CPU:"
echo "       stress --cpu 8 --timeout 60s"
echo "       # L'alerte 'HighCPUUsage' doit se déclencher"
echo ""
echo "    🔥 Méthode 3 - Remplir le disque:"
echo "       dd if=/dev/zero of=/tmp/fill-disk bs=1M count=10000"
echo "       # L'alerte 'DiskSpaceLow' doit se déclencher"
echo "       rm /tmp/fill-disk"
echo ""

echo "6️⃣  Vérification des canaux de notification..."
echo "    📧 Email: Vérifier alertmanager.yml"
echo "    💬 Slack: Vérifier alertmanager.yml"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Test des alertes terminé${NC}"
echo "=========================================="
echo ""
echo "📋 Pour voir les alertes en temps réel:"
echo "   http://localhost:9090/alerts"
echo ""
echo "📋 Pour tester le webhook manuellement:"
echo "   curl -X POST http://localhost:9093/-/reload"
echo ""
