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

## 🔴 RESTE A FAIRE (Bloquant pour le jury)

### Priorite 1 - Connecter services au monitoring
- [ ] Lancer exporters : postgres-exporter (port 9187), redis-exporter (port 9121)
- [ ] Verifier dans Prometheus Targets que tous sont "UP"
- [ ] Lancer l'application Django pour metrics applicatives

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
| PostgreSQL | localhost:5432 | ✅ UP (pas d'exporter) |
| Redis | localhost:6379 | ✅ UP (pas d'exporter) |

---

## 🎯 Prochaine session : Tester les alertes

1. Aller sur Prometheus > Alerts
2. Verifier que les regles sont chargees
3. Lancer stress-ng pour creer une charge CPU
4. Observer le declenchement de l'alerte "HighCPUUsage"
5. Verifier dans Alertmanager que l'alerte est recue
