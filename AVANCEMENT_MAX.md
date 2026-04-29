# Avancement selon retour Max - 29/04/2026

## ✅ TRAITE (Fait ce soir)

### 1. CI/CD corrigee
- [x] Retire `continue-on-error` sur **flake8** et **black** 
- [x] Ajoute commentaires explicatifs pour Bandit/Safety (gardes pour faux positifs)
- [x] Le pipeline sera maintenant ROUGE si code non conforme

### 2. Manifests K8s verifies
- [x] `deployment.yaml` - Deja complet (replicas, probes, resources, security)
- [x] `service.yaml` - Deja complet (ClusterIP + LoadBalancer)  
- [x] `servicemonitor.yaml` - Deja present pour Prometheus K8s SD
- [x] `ingress.yaml` - Deja present (ALB Ingress Controller)
- [x] `secret.yaml.template` - Deja present

### 3. Dashboards Grafana crees + Provisioning
- [x] **infrastructure.json** - CPU/RAM/Disk/Network (Node Exporter)
- [x] **application.json** - RPS, Latence p95/p99, Erreurs 5xx/4xx (Django)
- [x] **database.json** - Connexions, Transactions, Lock waits, Cache hit (PostgreSQL)
- [x] **provisioning/dashboards/dashboard.yml** - Chargement automatique au demarrage

### 4. Documentation Monitoring mise a jour
- [x] README.md - URLs fonctionnels (Grafana 127.0.0.1:3001, Prometheus 9090, Alertmanager 9093)
- [x] CDC.md - Section 7.0 URLs d'acces ajoutee

---

## ✅ TRAITE CONTINUATION

### 5. Services connectes au monitoring - TERMINE
- [x] Lancer postgres-exporter (port 9187) - **UP**
- [x] Lancer redis-exporter (port 9121) - **UP**
- [x] Tous les exporters sont fonctionnels (node, postgres, redis)

### 6. Git cleanup - TERMINE
- [x] Supprimer branches obsolètes : feature/images, hotfix/pharmacy-images, staging, master
- [x] Standardiser sur : main + develop uniquement

### 7. Alertes configurees - TERMINE
- [x] Ajouter alerte test `TestAlertAlwaysFiring` pour demo
- [x] Corriger connexion Prometheus → Alertmanager (host.docker.internal)
- [x] Configurer webhook de test (httpbin.org)

## 🔴 RESTE A FAIRE (Bloquant pour le jury)

### Priorite 1 - Tester les alertes de bout en bout
- [ ] **Test manuel obligatoire** : Lancer stress-ng pour saturer CPU
- [ ] Verifier que l'alerte "HighCPUUsage" se déclenche dans Prometheus
- [ ] Verifier que l'alerte arrive dans Alertmanager (http://localhost:9093)
- [ ] Verifier que le webhook reçoit la notification

### Priorite 2 - Tester les alertes
- [ ] Verifier regles d'alerte dans `monitoring/prometheus/rules/`
- [ ] Configurer recepteur Alertmanager (webhook Discord/Slack si besoin)
- [ ] **Tester un declenchement** : stress-ng pour saturer CPU et voir l'alerte partir

### Priorite 3 - Nettoyage Git
- [ ] Merger/supprimer branches : develop, feature/images, hotfix/pharmacy-images, master, staging
- [ ] Standardiser sur : main + develop + feature/*

### Priorite 4 - Securite EKS
- [ ] Restreindre `public_access_cidrs` dans terraform/eks.tf
- [ ] Auditer secrets Django (Stripe, SMS, Google Maps) dans .env.example

---

## 📊 URLs Monitoring (Fonctionnels)

| Service | URL | Status |
|---------|-----|--------|
| Grafana | http://127.0.0.1:3001 | ✅ UP |
| Prometheus | http://localhost:9090 | ✅ UP |
| Alertmanager | http://localhost:9093 | ✅ UP |
| Node Exporter | http://localhost:9100/metrics | ✅ UP |
| PostgreSQL Exporter | http://localhost:9187/metrics | ✅ UP |
| Redis Exporter | http://localhost:9121/metrics | ✅ UP |
| PostgreSQL | localhost:5432 | ✅ UP |
| Redis | localhost:6379 | ✅ UP |

---

## 🎯 TEST CRITIQUE A FAIRE IMMEDIATEMENT

**Max a insisté : "Une alerte définie sans test = aucune valeur au jury"**

### Procedure de test d'alerte CPU :

1. **Installer stress-ng** (si pas déjà fait) :
   ```bash
   # Linux/WSL
   sudo apt-get install stress-ng
   
   # Ou utiliser Docker
   docker run --rm -it polinux/stress-ng:latest --cpu 4 --timeout 60s
   ```

2. **Lancer le test** (dans un terminal séparé) :
   ```bash
   stress-ng --cpu 4 --timeout 120s
   ```

3. **Observer dans Prometheus** (http://localhost:9090) :
   - Menu : Alerts
   - L'alerte "HighCPUUsage" doit passer de "Pending" à "Firing"

4. **Verifier dans Alertmanager** (http://localhost:9093) :
   - L'alerte doit apparaître dans la liste
   - Le statut doit être "active"

5. **Capturer des screenshots** pour le jury :
   - Prometheus Alerts en état "Firing"
   - Alertmanager avec l'alerte reçue

## 🔴 PRIORITE 2 - Securite EKS (avant jury)

### Restreindre EKS public access
- [ ] Modifier `terraform/eks.tf` : `public_access_cidrs = ["YOUR_IP/32"]`
- [ ] Auditer `.env.example` : confirmer que Stripe/SMS/Google Maps keys sont externalisées
