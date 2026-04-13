#!/usr/bin/env python
"""
Script pour configurer le compte bancaire principal de MultiServe
Ce compte recevra tous les paiements des clients
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserBankAccount
import json

# Charger la configuration bancaire
with open('.bank_config.json', 'r') as f:
    bank_config = json.load(f)

# Créer ou récupérer l'utilisateur admin/admin
username = "abidrakhis"
email = "abidrakhis6@gmail.com"

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'first_name': 'Abidrakhis',
        'last_name': ''
    }
)

if created:
    user.set_password('admin123')
    user.save()
    print(f"✅ Utilisateur '{username}' créé avec mot de passe 'admin123'")
else:
    print(f"✅ Utilisateur '{username}' trouvé")

# Créer ou mettre à jour le compte bancaire
bank_account, created = UserBankAccount.objects.get_or_create(
    user=user,
    defaults={
        'account_holder_name': bank_config['account_holder_name'],
        'iban': bank_config['iban'],
        'bic_swift': bank_config['bic_swift'],
        'bank_name': bank_config['bank_name'],
        'is_verified': True  # Marqué comme vérifié car c'est le compte principal
    }
)

if not created:
    # Mettre à jour les informations
    bank_account.account_holder_name = bank_config['account_holder_name']
    bank_account.iban = bank_config['iban']
    bank_account.bic_swift = bank_config['bic_swift']
    bank_account.bank_name = bank_config['bank_name']
    bank_account.is_verified = True
    bank_account.save()
    print("✅ Compte bancaire mis à jour")
else:
    print("✅ Compte bancaire créé")

print("\n" + "="*60)
print("💳 CONFIGURATION BANCAIRE MULTISERVE")
print("="*60)
print(f"👤 Titulaire: {bank_config['account_holder_name']}")
print(f"🏦 Banque: {bank_config['bank_name']}")
print(f"📋 IBAN: {bank_config['iban']}")
print(f"🔑 BIC/SWIFT: {bank_config['bic_swift']}")
print(f"📊 RIB: {bank_config['rib']['banque']} {bank_config['rib']['guichet']} {bank_config['rib']['compte']} {bank_config['rib']['cle']}")
print("="*60)
print("\n✅ Configuration terminée!")
print("\n📝 Prochaines étapes:")
print("1. Appliquer les migrations: python manage.py migrate")
print("2. Exécuter ce script: python setup_bank_account.py")
print("3. Configurer Stripe Connect avec ces informations")
print("\n💰 Une fois Stripe configuré, les paiements arriveront sur ce compte!")
