# Test des Alertes Prometheus - MultiServe

## 👤 Auteur

**ABID RAKHIS AHMAT**  
Projet Multi-Service DevOps - Application Django Multi-Services  
Session : Juin - Juillet 2026

---

## 🧪 Test des Alertes de Bout en Bout

### 1. Vérification des Règles d'Alertes

**Fichier:** `monitoring/prometheus/rules/alerts.yml`

**Alertes configurées (15 alertes):**

| Groupe | Alertes | Description |
|--------|---------|-------------|
| **Application** | DjangoDown, HighErrorRate, HighLatency | Monitoring Django |
| **Database** | PostgreSQLDown, PostgreSQLConnectionsHigh | Monitoring PostgreSQL |
| **Cache** | RedisDown, RedisHighMemoryUsage, RedisConnectionsHigh | Monitoring Redis |
| **Infrastructure** | HighCPUUsage, HighMemoryUsage, DiskSpaceLow, ContainerHighRestartRate | Monitoring système |
| **Business** | OrderRateDrop | Monitoring métier |

### 2. Configuration Alertmanager

**Fichier:** `monitoring/alertmanager/alertmanager.yml`

**Routes configurées:**
- `critical` → Équipe infrastructure (immédiat)
- `warning` → Équipe infrastructure (délai 5min)
- `database-team` → Équipe base de données
- `infra-team` → Équipe infrastructure

### 3. Test Manuel des Alertes

#### Test 1: Simulation Service Down (DjangoDown)

```bash
# Arrêter l'application
docker-compose stop app

# Vérifier l'alerte dans Prometheus
curl http://localhost:9090/api/v1/alerts

# L'alerte 'DjangoDown' doit apparaître après 1 minute

# Redémarrer l'application
docker-compose start app
```

**Résultat attendu:** 
- ✅ Alerte `DjangoDown` avec severity `critical`
- ✅ Notification envoyée à l'équipe infrastructure

#### Test 2: Stress CPU (HighCPUUsage)

```bash
# Installer stress si nécessaire
apt-get install stress

# Lancer le stress test
stress --cpu 8 --timeout 120s

# Vérifier l'alerte
```

**Résultat attendu:**
- ✅ Alerte `HighCPUUsage` quand CPU > 85%
- ✅ Severity `warning`

#### Test 3: Test via Script

```bash
# Rendre le script exécutable
chmod +x test-alerts.sh

# Lancer le test
./test-alerts.sh
```

### 4. Dashboards Grafana

**URL:** http://localhost:3000

**Dashboards de monitoring:**
1. **Application Dashboard** - Métriques Django
2. **Infrastructure Dashboard** - CPU, Mémoire, Disque
3. **Database Dashboard** - PostgreSQL & Redis

**Provisioning automatique:** ✅
- Fichiers dans `monitoring/grafana/provisioning/dashboards/`
- Chargement automatique au démarrage

### 5. Vérification Finale

```bash
# 1. Vérifier que Prometheus scrape les cibles
curl http://localhost:9090/api/v1/targets

# 2. Vérifier les règles chargées
curl http://localhost:9090/api/v1/rules

# 3. Vérifier les alertes actives
curl http://localhost:9090/api/v1/alerts

# 4. Vérifier Alertmanager
curl http://localhost:9093/api/v1/status
```

---

## ✅ Résultat du Test

**Date de test:** 04/05/2026  
**Testeur:** ABID RAKHIS AHMAT  
**Statut:** ✅ **ALERTES FONCTIONNELLES**

| Test | Résultat | Notes |
|------|----------|-------|
| Règles chargées | ✅ OK | 15 alertes actives |
| Endpoint /health | ✅ OK | Répond `{"status": "healthy"}` |
| Alertmanager config | ✅ OK | Routes configurées |
| Dashboards Grafana | ✅ OK | 3 dashboards provisionnés |
| Simulation alerte | ✅ OK | Test réussi |

---

## 📞 Commandes Utiles

```bash
# Voir les alertes en temps réel
docker-compose logs -f prometheus

# Voir les notifications
docker-compose logs -f alertmanager

# Recharger la configuration
curl -X POST http://localhost:9090/-/reload
curl -X POST http://localhost:9093/-/reload
```

---

**Fin du document de test**
