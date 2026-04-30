# 📱 API Documentation - Authentification Avancée

Documentation complète des endpoints d'authentification avec SMS OTP, OAuth et notifications.

## 🔐 Endpoints d'Authentification

Base URL: `/api/v1/auth/`

---

## 1️⃣ Inscription Classique

### `POST /api/v1/auth/register/`

Inscription avec email et mot de passe.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+33612345678"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile": {
      "phone_number": "+33612345678",
      "phone_verified": false,
      "preferred_auth_method": "password"
    }
  },
  "token": "abc123xyz789",
  "message": "Inscription réussie"
}
```

---

## 2️⃣ Connexion Classique

### `POST /api/v1/auth/login/`

Connexion avec username/email et mot de passe.

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "user": { ... },
  "token": "abc123xyz789",
  "message": "Connexion réussie"
}
```

**Response (429 Too Many Requests):**
```json
{
  "error": "Trop de tentatives. Veuillez réessayer dans 5 minutes."
}
```

---

## 3️⃣ Authentification par Téléphone (SMS OTP)

### Étape 1: Demander un code OTP

### `POST /api/v1/auth/phone/request-otp/`

**Request:**
```json
{
  "phone_number": "+33612345678"
}
```

**Response (200 OK):**
```json
{
  "message": "Code envoyé par SMS",
  "expires_in": 600,
  "phone_masked": "+336****78"
}
```

**Rate Limit:** 3 requêtes / 10 minutes par numéro

---

### Étape 2: Vérifier le code et se connecter

### `POST /api/v1/auth/phone/verify-otp/`

**Request:**
```json
{
  "phone_number": "+33612345678",
  "otp_code": "123456"
}
```

**Response (200 OK):**
```json
{
  "user": { ... },
  "token": "abc123xyz789",
  "message": "Connexion réussie"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Code incorrect. 2 tentatives restantes."
}
```

**Sécurité:**
- Code à 6 chiffres
- Expire après 10 minutes
- 3 tentatives maximum par code
- Nouveau code = anciens codes invalidés

---

## 4️⃣ Connexion OAuth

### `POST /api/v1/auth/oauth/login/`

Connexion rapide via Google ou Facebook.

### Google OAuth

**Request:**
```json
{
  "provider": "google",
  "access_token": "ya29.a0AfH6SMB..."
}
```

### Facebook OAuth

**Request:**
```json
{
  "provider": "facebook",
  "access_token": "EAAGm0PX4ZCpsBA..."
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 2,
    "username": "john_google",
    "email": "john@gmail.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile": {
      "google_id": "123456789",
      "avatar_url": "https://lh3.googleusercontent.com/...",
      "preferred_auth_method": "google"
    }
  },
  "token": "abc123xyz789",
  "message": "Connexion google réussie"
}
```

**Comportement:**
- Crée un compte automatiquement si l'utilisateur n'existe pas
- Lie le compte OAuth à un compte existant si l'email correspond
- Stocke le token OAuth pour les appels API ultérieurs

---

## 5️⃣ Gestion du Profil

### Récupérer le profil

### `GET /api/v1/auth/profile/`

**Headers:**
```
Authorization: Token abc123xyz789
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "phone_number": "+33612345678",
    "phone_verified": true,
    "google_id": null,
    "facebook_id": null,
    "avatar_url": null,
    "preferred_auth_method": "phone"
  }
}
```

---

### Mettre à jour le profil

### `PUT /api/v1/auth/profile/`

**Request:**
```json
{
  "first_name": "Johnny",
  "last_name": "Doe",
  "email": "johnny@example.com",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

---

### Mettre à jour le numéro de téléphone

### `POST /api/v1/auth/profile/phone/`

**Request:**
```json
{
  "phone_number": "+33698765432",
  "otp_code": "654321"
}
```

Nécessite la vérification OTP du nouveau numéro.

---

### Changer le mot de passe

### `POST /api/v1/auth/profile/password/`

**Request:**
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

Envoie automatiquement une notification email de sécurité.

---

### Voir les méthodes d'authentification disponibles

### `GET /api/v1/auth/profile/auth-methods/`

**Response (200 OK):**
```json
{
  "password": true,
  "phone": {
    "enabled": true,
    "phone_masked": "+336****78"
  },
  "google": {
    "enabled": true,
    "connected": true
  },
  "facebook": {
    "enabled": false,
    "connected": false
  }
}
```

---

## 6️⃣ Mot de Passe Oublié

### `POST /api/v1/auth/password/forgot/`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Un email de réinitialisation a été envoyé si l'adresse existe"
}
```

> 🔒 **Sécurité:** La réponse est identique que l'email existe ou non pour éviter l'énumération.

---

## 7️⃣ Gestion des Sessions

### Lister les sessions actives

### `GET /api/v1/auth/sessions/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "session_key": "abc123...",
    "ip_address": "192.168.1.1",
    "device_info": "Chrome on Windows",
    "location_city": "Paris",
    "location_country": "France",
    "is_active": true,
    "is_trusted": true,
    "is_current": true,
    "created_at": "2026-01-15T10:30:00Z",
    "last_activity": "2026-01-15T14:20:00Z"
  }
]
```

---

### Terminer une session spécifique

### `POST /api/v1/auth/sessions/{id}/terminate/`

**Response (200 OK):**
```json
{
  "message": "Session terminée avec succès"
}
```

---

### Terminer toutes les autres sessions

### `POST /api/v1/auth/sessions/terminate-all/`

**Response (200 OK):**
```json
{
  "message": "3 session(s) terminée(s) avec succès"
}
```

---

## 8️⃣ Journal de Sécurité

### `GET /api/v1/auth/security/logs/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "event_type": "login_success",
    "event_type_display": "Connexion réussie",
    "ip_address": "192.168.1.1",
    "created_at": "2026-01-15T10:30:00Z",
    "details": {
      "method": "phone_otp"
    }
  },
  {
    "id": 2,
    "event_type": "password_change",
    "event_type_display": "Changement de mot de passe",
    "ip_address": "192.168.1.1",
    "created_at": "2026-01-15T11:00:00Z",
    "details": null
  }
]
```

Affiche les 50 derniers événements de sécurité.

---

## 9️⃣ Notifications

### Lister les notifications

### `GET /api/v1/auth/notifications/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "notification_type": "new_message",
    "notification_type_display": "Nouveau message",
    "channel": "both",
    "title": "Nouveau message de Jane",
    "message": "Vous avez reçu un nouveau message: Bonjour, ...",
    "status": "sent",
    "status_display": "Envoyé",
    "sent_at": "2026-01-15T10:30:00Z",
    "delivered_at": "2026-01-15T10:30:05Z",
    "read_at": null,
    "created_at": "2026-01-15T10:30:00Z"
  }
]
```

---

### Marquer comme lu

### `POST /api/v1/auth/notifications/mark-read/`

**Request (spécifique):**
```json
{
  "notification_ids": [1, 2, 3]
}
```

**Request (toutes):**
```json
{}
```

**Response:**
```json
{
  "message": "3 notification(s) marquée(s) comme lue(s)"
}
```

---

### Nombre de notifications non lues

### `GET /api/v1/auth/notifications/unread-count/`

**Response (200 OK):**
```json
{
  "unread_count": 5
}
```

---

## 🔒 Mesures de Sécurité

### Rate Limiting (Limitation de débit)

| Endpoint | Limite | Fenêtre |
|----------|--------|---------|
| `/login/` | 5 tentatives | 5 minutes |
| `/phone/request-otp/` | 3 requêtes | 10 minutes par numéro |
| `/phone/verify-otp/` | 5 tentatives | 5 minutes par numéro |
| `/register/` | 3 inscriptions | 1 heure par IP |
| `/password/forgot/` | 3 requêtes | 10 minutes par email |

### Verrouillage de Compte

- **5 échecs de connexion** → Compte verrouillé pendant **30 minutes**
- Notification email automatique envoyée

### Expiration des Codes OTP

- **Durée de validité:** 10 minutes
- **Tentatives max:** 3 par code
- **Invalidation:** Nouveau code = anciens codes invalidés

### Gestion des Sessions

- **Durée de vie:** 30 jours
- **Tracking:** IP, User-Agent, Device
- **Révocation:** Possible à distance via `/sessions/{id}/terminate/`
- **Notifications:** Email envoyé lors de nouvelles connexions

---

## 🔑 Authentification API

Tous les endpoints protégés nécessitent un token:

**Header:**
```
Authorization: Token votre-token-ici
```

**Obtenir un token:**
1. Inscription: `POST /api/v1/auth/register/`
2. Connexion: `POST /api/v1/auth/login/`
3. Connexion OTP: `POST /api/v1/auth/phone/verify-otp/`
4. Connexion OAuth: `POST /api/v1/auth/oauth/login/`

---

## 📧 Notifications Automatiques

Le système envoie automatiquement des notifications pour:

| Événement | Canal | Détail |
|-----------|-------|--------|
| Connexion réussie | Email | IP, heure, méthode |
| Changement de mot de passe | Email + SMS | Confirmation de changement |
| Nouveau message | Email + SMS | Expéditeur, aperçu |
| Échec de connexion | Email | Après 3 échecs |
| Compte verrouillé | Email | Durée de verrouillage |

---

## 🛠️ Configuration Requise

### Variables d'Environnement

```bash
# Twilio (SMS)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxx
TWILIO_PHONE_NUMBER=+336xxxxxxxx

# OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
FACEBOOK_APP_ID=xxx
FACEBOOK_APP_SECRET=xxx

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxx
DEFAULT_FROM_EMAIL=noreply@domain.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

---

## 📝 Codes d'Erreur

| Code | Description |
|------|-------------|
| `400` | Requête invalide (validation) |
| `401` | Non authentifié (token manquant/invalid) |
| `403` | Interdit (compte verrouillé) |
| `404` | Ressource non trouvée |
| `429` | Trop de requêtes (rate limit) |
| `500` | Erreur serveur |

---

## 🔄 Workflow Typique

### Nouvel Utilisateur

1. **Inscription:** `POST /register/` → Token créé
2. **Vérification téléphone:** `POST /phone/request-otp/` → SMS envoyé
3. **Confirmer OTP:** `POST /phone/verify-otp/` → Téléphone vérifié

### Connexion Quotidienne

1. **Demander OTP:** `POST /phone/request-otp/`
2. **Recevoir SMS** avec code à 6 chiffres
3. **Vérifier:** `POST /phone/verify-otp/` → Connecté

### Connexion OAuth (Rapide)

1. **Frontend:** Authentification Google/Facebook
2. **Récupérer token:** Access token OAuth
3. **Backend:** `POST /oauth/login/` → Connecté (compte créé si nouveau)

---

**Version:** 1.0  
**Dernière mise à jour:** Janvier 2026
