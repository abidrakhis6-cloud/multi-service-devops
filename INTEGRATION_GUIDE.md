# 🔧 Guide d'Intégration - Glo-Service

## 1️⃣ Intégration Stripe (Paiement par Carte)

### Étape 1 : Créer un compte Stripe
1. Aller sur https://stripe.com/fr
2. Cliquer sur "Commencer"
3. S'enregistrer avec email professionnel
4. Vérifier l'email

### Étape 2 : Récupérer les clés API
1. Dashboard Stripe → Développeurs → Clés API
2. Copier :
   - **Clé publié test** (pk_test_...)
   - **Clé secrète test** (sk_test_...)
3. Coller dans `.env` :
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Étape 3 : Configuration Django
```python
# Dans settings.py
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

# Dans requirements.txt (déjà installé)
stripe==5.4.0
```

### Étape 4 : Implémenter le traitement
```python
# Dans core/views.py - fonction checkout

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        token = request.POST.get('stripeToken')
        
        if payment_method == 'card':
            try:
                charge = stripe.Charge.create(
                    amount=int(total_amount * 100),  # En centimes
                    currency='eur',
                    source=token,
                    description=f'Order #{order.id}'
                )
                payment.stripe_id = charge.id
                payment.status = 'completed'
                payment.save()
                order.status = 'confirmed'
                order.save()
            except stripe.error.CardError as e:
                messages.error(request, str(e))
    
    return render(request, 'checkout.html', context)
```

### Étape 5 : Tester
- Numéro test : `4242 4242 4242 4242`
- Expiration : `12/25`
- CVC : `123`

---

## 2️⃣ Intégration PayPal

### Étape 1 : Créer un compte PayPal
1. Aller sur https://developer.paypal.com
2. S'enregistrer/Se connecter
3. Accepter les conditions

### Étape 2 : Créer une app Sandbox
1. Dashboard → Apps & Credentials
2. Créer une nouvelle app REST
3. Copier :
   - **Client ID**
   - **Secret**

### Étape 3 : Installation SDK
```html
<!-- Dans core/templates/checkout.html -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID"></script>
```

### Étape 4 : Implémenter les boutons
```javascript
// Dans checkout.html

paypal.Buttons({
    createOrder: (data, actions) => {
        return actions.order.create({
            purchase_units: [{
                amount: {
                    value: totalAmount.toString()
                },
                description: "Commande GloService"
            }]
        });
    },
    
    onApprove: (data, actions) => {
        return actions.order.capture().then(details => {
            // Envoyer au backend pour traitement
            fetch('/api/v1/payments/paypal-capture/', {
                method: 'POST',
                body: JSON.stringify({
                    order_id: data.orderID,
                    order_database_id: orderId
                })
            })
        });
    },
    
    onError: (err) => {
        console.error('PayPal error:', err);
    }
}).render('#paypal-payment');
```

### Étape 5 : Backend - Vérifier le paiement
```python
# Dans core/views.py

@csrf_exempt
@require_POST
def paypal_capture(request):
    import requests
    
    data = json.loads(request.body)
    order_id = data['order_id']
    
    # Vérifier avec PayPal
    response = requests.post(
        f'https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture',
        headers={
            'Authorization': f'Bearer {get_paypal_access_token()}',
            'Content-Type': 'application/json'
        }
    )
    
    if response.status_code == 201:
        # Marquer comme payée
        payment = Payment.objects.get(id=data['order_database_id'])
        payment.status = 'completed'
        payment.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)
```

---

## 3️⃣ Intégration Google Maps

### Étape 1 : Créer un projet Google Cloud
1. Aller sur https://console.cloud.google.com
2. Créer nouveau projet : "Glo-Service"
3. Attendre la création...

### Étape 2 : Activer les APIs
1. APIs et services → Bibliothèque
2. Rechercher et activer :
   - **Maps JavaScript API**
   - **Geolocation API**
   - **Directions API**

### Étape 3 : Créer une clé API
1. Credentials → Créer credential → Clé API
2. Ajouter restrictions :
   - Type : **Clés de navigateur**
   - Affectation à Pages : Cocher Maps JavaScript
3. Copier la clé dans `.env` :
```env
GOOGLE_MAPS_API_KEY=AIzaSy...
```

### Étape 4 : Charger l'API dans le template
```html
<!-- core/templates/checkout.html -->
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places,directions"></script>
```

### Étape 5 : Initialiser la carte
```javascript
// Dans checkout.html

let map;
let directionsService;
let directionsRenderer;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13,
        center: { lat: 48.8566, lng: 2.3522 } // Paris défaut
    });
    
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
    
    // Obtenir position utilisateur
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            
            map.setCenter(userLocation);
            
            // Ajouter marqueur utilisateur
            new google.maps.Marker({
                position: userLocation,
                map: map,
                title: 'Votre position'
            });
        });
    }
}

// Calculer trajet livreur
function drawDriverRoute(driverLat, driverLng, clientLat, clientLng) {
    directionsService.route({
        origin: { lat: parseFloat(driverLat), lng: parseFloat(driverLng) },
        destination: { lat: parseFloat(clientLat), lng: parseFloat(clientLng) },
        travelMode: google.maps.TravelMode.DRIVING
    }, (result, status) => {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsRenderer.setDirections(result);
            
            // Afficher durée estimée
            const duration = result.routes[0].legs[0].duration.text;
            document.getElementById('eta').textContent = `ETA: ${duration}`;
        }
    });
}

// Initialiser au chargement
window.addEventListener('load', initMap);
```

### Étape 6 : WebSocket temps réel
```javascript
// Mettre à jour la position livreur en temps réel

const socket = new WebSocket('ws://localhost:8000/ws/location/' + orderId + '/');

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Mettre à jour marqueur livreur
    drawDriverRoute(data.latitude, data.longitude, clientLat, clientLng);
};
```

---

## 4️⃣ Intégration Apple Pay

### Étape 1 : Configuration Apple Developer
1. Aller sur https://developer.apple.com
2. Créer Merchant ID dans Certificates
3. Télécharger le certificat

### Étape 2 : Implémenter dans le frontend
```javascript
// Dans checkout.html

const canMakePayment = await ApplePaySession.canMakePaymentsWithActiveCard('merchant.fr.gloservice');

if (canMakePayment) {
    document.getElementById('apple-pay').style.display = 'block';
}

async function applePayClicked() {
    const paymentRequest = {
        countryCode: 'FR',
        currencyCode: 'EUR',
        supportedNetworks: ['visa', 'masterCard'],
        merchantCapabilities: ['supports3DS'],
        total: {
            label: 'GloService - Commande',
            amount: totalAmount.toString()
        },
        lineItems: [{
            label: 'Produits',
            amount: subtotal.toString()
        }, {
            label: 'Livraison',
            amount: '5.00'
        }]
    };
    
    const session = new ApplePaySession(3, paymentRequest);
    
    session.onpaymentauthorized = (event) => {
        // Envoyer au backend
        fetch('/api/v1/payments/apple-pay/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: event.payment.token,
                order_id: orderId
            })
        });
    };
    
    session.begin();
}
```

---

## 5️⃣ Intégration Google Pay

### Étape 1 : Configuration Google Pay
```javascript
// Dans checkout.html

const googlePayClient = new google.payments.api.PaymentsClient({
    environment: 'TEST' // 'PRODUCTION' pour prod
});

const isReadyToPayRequest = {
    apiVersion: 2,
    apiVersionMinor: 0,
    allowedPaymentMethods: [{
        type: 'CARD',
        parameters: {
            allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
            allowedCardNetworks: ['MASTERCARD', 'VISA']
        }
    }]
};

googlePayClient.isReadyToPay(isReadyToPayRequest).then(response => {
    if (response.result) {
        document.getElementById('google-pay').style.display = 'block';
    }
});
```

### Étape 2 : Bouton Google Pay
```javascript
const transactionInfo = {
    totalPriceStatus: 'FINAL',
    totalPriceLabel: 'Total',
    totalPrice: totalAmount.toString(),
    currencyCode: 'EUR',
    countryCode: 'FR'
};

const paymentDataRequest = Object.assign({}, isReadyToPayRequest);
paymentDataRequest.transactionInfo = transactionInfo;

async function googlePayClicked() {
    try {
        const paymentData = await googlePayClient.loadPaymentData(paymentDataRequest);
        
        // Envoyer au backend
        fetch('/api/v1/payments/google-pay/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                payment_token: paymentData.paymentMethodData.tokenizationData.token,
                order_id: orderId
            })
        });
    } catch (err) {
        console.error('Google Pay error:', err);
    }
}
```

---

## 6️⃣ Intégration WebSocket (Django Channels)

### Étape 1 : Installation
```bash
pip install channels channels-redis
```

### Étape 2 : Configuration Django
```python
# settings.py

INSTALLED_APPS = [
    ...,
    'daphne',
    'channels',
]

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### Étape 3 : Créer asgi.py
```python
# config/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
```

### Étape 4 : Configurations WebSocket
```python
# core/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:order_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/location/<int:order_id>/', consumers.DriverLocationConsumer.as_asgi()),
    path('ws/notifications/<int:order_id>/', consumers.NotificationConsumer.as_asgi()),
]
```

### Étape 5 : Lancer avec Daphne
```bash
# Au lieu de runserver
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

---

## 7️⃣ Mise en Production

### Étape 1 : Configurer réellement les services
Remplacer les clés **test** par les clés **production**

### Étape 2 : Base de données PostgreSQL
```python
# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gloservice',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Étape 3 : Gunicorn + Nginx
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Étape 4 : Redis pour WebSocket
```bash
# Docker
docker run -d -p 6379:6379 redis:latest
```

### Étape 5 : SSL/HTTPS
```bash
# Avec Let's Encrypt
certbot certonly --standalone -d yourdomain.com
```

---

## 🧪 Tester Localement

### Stripe Test
```javascript
// Utiliser numéro 4242 4242 4242 4242
```

### PayPal Sandbox
```
Email: sb-nftqh+personal@business.example.com
Mot de passe: aH+JZ4v$
```

### Google Maps
```
Latitude: 48.8566
Longitude: 2.3522
```

---

## 📚 Ressources

- **Stripe** : https://stripe.com/docs
- **PayPal** : https://developer.paypal.com/docs
- **Google Maps** : https://developers.google.com/maps
- **Django Channels** : https://channels.readthedocs.io
- **Apple Pay** : https://developer.apple.com/apple-pay
- **Google Pay** : https://pay.google.com/about

---

✨ **Bon intégration!**
