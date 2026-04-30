# 🚀 Guide de Déploiement Production - multi-serve.fr

Passage de localhost à un serveur en ligne avec domaine personnalisé.

---

## 📋 PRÉREQUIS

### 1. Acheter le nom de domaine

**Registrar recommandés :**
- OVH (€7/an pour .fr)
- Gandi
- Namecheap
- Cloudflare (gestion DNS gratuite)

**Domaine :** `multi-serve.fr`

---

## 🔧 ÉTAPE 1 : Configurer les DNS

### Chez ton registrar (OVH, Gandi, etc.)

Ajoute ces enregistrements DNS :

```
Type    Nom                    Valeur                          TTL
A       multi-serve.fr         IP_DE_TON_SERVEUR               3600
A       www.multi-serve.fr     IP_DE_TON_SERVEUR               3600

# Pour les sous-domaines (optionnel)
A       api.multi-serve.fr     IP_DE_TON_SERVEUR               3600
A       admin.multi-serve.fr   IP_DE_TON_SERVEUR               3600
```

**Trouver l'IP de ton serveur :**
```bash
# Si tu utilises un VPS cloud (AWS, DigitalOcean, OVH, etc.)
# L'IP est fournie dans le tableau de bord

# Test de propagation DNS (attendre 5-30 minutes)
dig multi-serve.fr
nslookup multi-serve.fr
```

---

## 🖥️ ÉTAPE 2 : Préparer le Serveur

### Installer Docker & Docker Compose

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
# Déconnexion/reconnexion nécessaire
```

---

## 🔒 ÉTAPE 3 : Certificats SSL (Let's Encrypt)

### 3.1 Installer Certbot

```bash
# Ubuntu
sudo apt-get install -y certbot

# Ou avec Docker (recommandé pour notre setup)
docker run -it --rm \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly --standalone \
  -d multi-serve.fr -d www.multi-serve.fr \
  --agree-tos --email ton-email@example.com
```

### 3.2 Renouvellement automatique

Crée un script de renouvellement :

```bash
# /home/user/renew-ssl.sh
#!/bin/bash
docker run -it --rm \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  -p 80:80 \
  certbot/certbot renew --quiet

# Recharger Nginx
docker exec nginx nginx -s reload
```

```bash
chmod +x /home/user/renew-ssl.sh

# Crontab pour renouvellement mensuel
sudo crontab -e
# Ajouter :
0 2 1 * * /home/user/renew-ssl.sh
```

---

## 📁 ÉTAPE 4 : Configuration des Fichiers

### 4.1 Créer le fichier .env.production

```bash
# Sur le serveur
cd /opt/multiserve
nano .env
```

Contenu :

```bash
# ==========================================
# PRODUCTION - multi-serve.fr
# ==========================================

# Django
DEBUG=False
SECRET_KEY=CHANGE_ME_TO_50_RANDOM_CHARS_SECRET_KEY_PROD
ALLOWED_HOSTS=multi-serve.fr,www.multi-serve.fr,localhost,127.0.0.1

# Database (PostgreSQL sur le même serveur ou RDS)
DATABASE_URL=postgresql://user:password@db:5432/multiserve_prod

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=your_secure_redis_password

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@multi-serve.fr
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxx

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+336xxxxxxxx

# OAuth - GOOGLE (voir section OAuth ci-dessous)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx

# OAuth - FACEBOOK
FACEBOOK_APP_ID=xxx
FACEBOOK_APP_SECRET=xxx

# Frontend URL (IMPORTANT !)
FRONTEND_URL=https://multi-serve.fr

# Security
CSRF_TRUSTED_ORIGINS=https://multi-serve.fr,https://www.multi-serve.fr,http://localhost:8000
CORS_ALLOWED_ORIGINS=https://multi-serve.fr,https://www.multi-serve.fr,http://localhost:3000
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=True

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=SECURE_GRAFANA_PASSWORD
```

### 4.2 Modifier docker-compose.yml pour Production

```yaml
version: '3.8'

services:
  # Nginx avec SSL
  nginx:
    image: nginx:alpine
    container_name: multiserve_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro  # Certs SSL
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - multiserve_network

  # Django Application
  app:
    build: .
    container_name: multiserve_app
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - multiserve_network
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py migrate &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"

  # PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: multiserve_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - .env
    environment:
      POSTGRES_DB: multiserve_prod
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: unless-stopped
    networks:
      - multiserve_network

  # Redis
  redis:
    image: redis:7-alpine
    container_name: multiserve_redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - multiserve_network

  # Prometheus (Monitoring)
  prometheus:
    image: prom/prometheus:latest
    container_name: multiserve_prometheus
    volumes:
      - ./monitoring/prometheus:/etc/prometheus:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    networks:
      - multiserve_network

  # Grafana (Monitoring Dashboard)
  grafana:
    image: grafana/grafana:latest
    container_name: multiserve_grafana
    ports:
      - "3001:3000"  # Exposé uniquement en interne ou via VPN
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning:ro
    env_file:
      - .env
    restart: unless-stopped
    networks:
      - multiserve_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  prometheus_data:
  grafana_data:

networks:
  multiserve_network:
    driver: bridge
```

---

## 🔑 ÉTAPE 5 : Configuration OAuth avec Domaine Production

### 5.1 Google OAuth (nouveaux identifiants)

Va sur : https://console.cloud.google.com/apis/credentials

**1. Créer l'écran de consentement :**
- Type : **Externe**
- Nom : `MultiServe`
- Email : ton-email@example.com
- Domaines autorisés : `multi-serve.fr`, `www.multi-serve.fr`

**2. Créer l'ID client OAuth 2.0 :**
- Type : **Application Web**
- Nom : `MultiServe Production`
- **URI de redirection autorisés :**
  ```
  https://multi-serve.fr/api/v1/auth/oauth/callback/google/
  https://www.multi-serve.fr/api/v1/auth/oauth/callback/google/
  ```
- **Origines JavaScript autorisées :**
  ```
  https://multi-serve.fr
  https://www.multi-serve.fr
  ```

**3. Copier dans .env :**
```bash
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
```

### 5.2 Facebook OAuth (nouveaux identifiants)

Va sur : https://developers.facebook.com/apps

**1. Créer une nouvelle application :**
- Type : **Authentification**
- Nom : `MultiServe`

**2. Configurer Facebook Login :**
- Produit : **Facebook Login** → Configurer
- **URI de redirection OAuth valides :**
  ```
  https://multi-serve.fr/api/v1/auth/oauth/callback/facebook/
  https://www.multi-serve.fr/api/v1/auth/oauth/callback/facebook/
  ```

**3. Paramètres → Général :**
- **Domaines de l'application :**
  ```
  multi-serve.fr
  www.multi-serve.fr
  ```

**4. Copier dans .env :**
```bash
FACEBOOK_APP_ID=123456789
FACEBOOK_APP_SECRET=abc123xyz789
```

---

## 🚀 ÉTAPE 6 : Déploiement

### 6.1 Cloner et configurer sur le serveur

```bash
# Sur le serveur
sudo mkdir -p /opt/multiserve
cd /opt/multiserve

# Cloner le repo
git clone https://github.com/abidrakhis6-cloud/multi-service-devops.git .

# Copier la config environnement
cp .env.example .env
nano .env  # Remplir avec les valeurs de production
```

### 6.2 Lancer l'application

```bash
# Construire et démarrer
docker-compose -f docker-compose.prod.yml up -d --build

# Vérifier les logs
docker-compose logs -f app

# Créer un superutilisateur
docker-compose exec app python manage.py createsuperuser
```

### 6.3 Vérifier le fonctionnement

```bash
# Test local
curl -I https://multi-serve.fr/health/
curl https://multi-serve.fr/api/v1/auth/auth-methods/

# Vérifier SSL
openssl s_client -connect multi-serve.fr:443 -servername multi-serve.fr
```

---

## 🧪 ÉTAPE 7 : Tests OAuth en Production

### Test Google OAuth

```bash
# 1. Ouvrir dans navigateur :
https://multi-serve.fr

# 2. Cliquer "Connexion avec Google"

# 3. Autoriser l'application

# 4. Redirection automatique vers :
https://multi-serve.fr/api/v1/auth/oauth/callback/google/

# 5. Vérifier la connexion réussie
```

### Test Facebook OAuth

```bash
# Même procédure avec Facebook
# Redirection vers :
https://multi-serve.fr/api/v1/auth/oauth/callback/facebook/
```

---

## 📊 URLs Production

| Service | URL Production |
|---------|---------------|
| Application | https://multi-serve.fr |
| API | https://multi-serve.fr/api/v1/ |
| Admin Django | https://multi-serve.fr/admin/ |
| OAuth Google | https://multi-serve.fr/api/v1/auth/oauth/callback/google/ |
| OAuth Facebook | https://multi-serve.fr/api/v1/auth/oauth/callback/facebook/ |
| Monitoring Grafana | https://multi-serve.fr:3001 (ou via VPN) |

---

## 🔒 Sécurité Production

### Pare-feu (UFW)

```bash
# Autoriser uniquement les ports nécessaires
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Fail2Ban (protection brute force)

```bash
sudo apt-get install fail2ban

# Configurer pour Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
action = iptables-multiport[name=nginx-http-auth, port="http,https"]
logpath = /var/log/nginx/error.log
bantime = 3600
findtime = 600
maxretry = 3
```

### Sauvegardes automatiques

```bash
# Backup quotidien de la DB
crontab -e
# Ajouter :
0 3 * * * docker exec multiserve_db pg_dump -U user multiserve_prod > /backup/db-$(date +\%Y\%m\%d).sql
```

---

## 🆘 Dépannage

### Erreur SSL/certificate

```bash
# Vérifier les certificats
sudo certbot certificates

# Renouveler manuellement
sudo certbot renew --force-renewal

# Recharger Nginx
docker-compose exec nginx nginx -s reload
```

### Erreur OAuth "redirect_uri_mismatch"

Vérifier que les URLs dans Google/Facebook Developer Console **correspondent exactement** à celles utilisées.

### Erreur DNS

```bash
# Vérifier la propagation
dig +trace multi-serve.fr
# Attendre 24h max après changement DNS
```

---

## 📞 Support

**Documentation API :** `API_AUTH_DOCUMENTATION.md`
**Monitoring :** https://multi-serve.fr:3001 (admin/admin123)
**Logs :** `docker-compose logs -f`

---

**Status :** ✅ Prêt pour production !
