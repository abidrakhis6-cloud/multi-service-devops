"""
Script de peuplement des données initiales
Place ce script dans le dossier core/
Exécute: python manage.py shell < populate.py
"""

from core.models import Store, Product, Driver

# Supprimer les données existantes
Store.objects.all().delete()
Product.objects.all().delete()
Driver.objects.all().delete()

# ============ RESTAURANTS ============
kfc = Store.objects.create(
    name='KFC - Paris Charlie',
    category='restaurant',
    description='Poulet frit croustillant et délicieux',
    rating=4.8
)

Product.objects.create(name='Bucket 12 pièces', price=24.99, store=kfc, category='Poulet', description='12 pièces de poulet croustillant')
Product.objects.create(name='Combo Poulet + Frites', price=12.99, store=kfc, category='Combo', description='Poulet avec frites et soda')
Product.objects.create(name='Wings 10 pièces', price=8.99, store=kfc, category='Wings', description='Ailes croustillantes')
Product.objects.create(name='Burger Zinger', price=9.99, store=kfc, category='Burger', description='Burger épicé avec poulet')

mcdo = Store.objects.create(
    name='McDonald\'s - Champs Élysées',
    category='restaurant',
    description='Le fast food préféré des français',
    rating=4.5
)

Product.objects.create(name='Big Mac', price=6.49, store=mcdo, category='Burger', description='Double steak, double fromage')
Product.objects.create(name='McChicken', price=5.99, store=mcdo, category='Burger', description='Filet de poulet croustillant')
Product.objects.create(name='Frites Medium', price=2.99, store=mcdo, category='Frites', description='Les meilleures frites')
Product.objects.create(name='Happy Meal', price=8.99, store=mcdo, category='Enfant', description='Jouet inclus')

quick = Store.objects.create(
    name='Quick - République',
    category='restaurant',
    description='Steakburger français de qualité',
    rating=4.3
)

Product.objects.create(name='Steakburger Classic', price=7.99, store=quick, category='Burger', description='Steak haché français')
Product.objects.create(name='Steakburger Bacon Cheese', price=9.49, store=quick, category='Burger', description='Bacon et fromage')
Product.objects.create(name='Chicken Burger', price=6.99, store=quick, category='Burger', description='Poulet mariné')
Product.objects.create(name='Salade César XL', price=8.99, store=quick, category='Salade', description='Salade avec poulet grillé')

# ============ COURSES ============
lidl = Store.objects.create(
    name='Lidl - Châtelet',
    category='courses',
    description='Supermarché à bas prix',
    rating=4.1
)

Product.objects.create(name='Pain complet', price=1.29, store=lidl, category='Boulangerie', description='1 kg')
Product.objects.create(name='Lait entier', price=1.19, store=lidl, category='Laiterie', description='1L')
Product.objects.create(name='Œufs (12)', price=2.49, store=lidl, category='Laiterie', description='Œufs fermiers')
Product.objects.create(name='Riz blanc', price=1.99, store=lidl, category='Épicerie', description='500g')

leclerc = Store.objects.create(
    name='Leclerc - Bercy',
    category='courses',
    description='Hypermarché français',
    rating=4.4
)

Product.objects.create(name='Jambon de Paris', price=5.99, store=leclerc, category='Boucherie', description='400g')
Product.objects.create(name='Fromage Emmental', price=3.49, store=leclerc, category='Laiterie', description='500g')
Product.objects.create(name='Tomates cerises', price=2.99, store=leclerc, category='Fruits Légumes', description='250g')
Product.objects.create(name='Pâtes Panzani', price=0.99, store=leclerc, category='Épicerie', description='500g')

aldi = Store.objects.create(
    name='Aldi - Bastille',
    category='courses',
    description='Discount allemand',
    rating=4.2
)

Product.objects.create(name='Poitrine de poulet', price=6.99, store=aldi, category='Boucherie', description='600g')
Product.objects.create(name='Mozzarella', price=2.99, store=aldi, category='Laiterie', description='200g')
Product.objects.create(name='Pommes Galas', price=1.49, store=aldi, category='Fruits Légumes', description='1kg')
Product.objects.create(name='Beurre doux', price=3.49, store=aldi, category='Laiterie', description='250g')

carrefour = Store.objects.create(
    name='Carrefour - Opéra',
    category='courses',
    description='Grand choix de produits',
    rating=4.6
)

Product.objects.create(name='Escalope de veau', price=12.99, store=carrefour, category='Boucherie', description='400g')
Product.objects.create(name='Yaourt nature', price=2.49, store=carrefour, category='Laiterie', description='Pack de 8')
Product.objects.create(name='Salade verte', price=1.99, store=carrefour, category='Fruits Légumes', description='500g')
Product.objects.create(name='Huile d\'olive', price=5.99, store=carrefour, category='Épicerie', description='500ml')

super_u = Store.objects.create(
    name='Super U - Marais',
    category='courses',
    description='Frais et qualité française',
    rating=4.7
)

Product.objects.create(name='Côte de veau', price=14.99, store=super_u, category='Boucherie', description='500g')
Product.objects.create(name='Crème fraîche', price=1.89, store=super_u, category='Laiterie', description='200ml')
Product.objects.create(name='Poireau', price=1.29, store=super_u, category='Fruits Légumes', description='500g')
Product.objects.create(name='Miel français', price=4.99, store=super_u, category='Épicerie', description='500g')

# ============ BOUTIQUE ============
iphone_store = Store.objects.create(
    name='Apple Store - Montaigne',
    category='boutique',
    description='Téléphones et accessoires Apple',
    rating=4.9
)

Product.objects.create(name='iPhone 16 Pro', price=1199.99, store=iphone_store, category='Téléphone', description='256GB - Titanium')
Product.objects.create(name='iPhone 16', price=899.99, store=iphone_store, category='Téléphone', description='128GB - Noir')
Product.objects.create(name='AirPods Pro', price=249.99, store=iphone_store, category='Accessoire', description='Écouteurs sans fil')
Product.objects.create(name='iPhone Case', price=59.99, store=iphone_store, category='Accessoire', description='Protection premium')

samsung_store = Store.objects.create(
    name='Samsung Store - Rivoli',
    category='boutique',
    description='Téléphones Samsung et électronique',
    rating=4.6
)

Product.objects.create(name='Galaxy S25', price=999.99, store=samsung_store, category='Téléphone', description='256GB')
Product.objects.create(name='Galaxy Buds', price=179.99, store=samsung_store, category='Accessoire', description='Écouteurs')
Product.objects.create(name='Samsung TV 55"', price=699.99, store=samsung_store, category='Électronique', description='4K HDR')

mac_store = Store.objects.create(
    name='MacBook Center - Champs',
    category='boutique',
    description='Ordinateurs Apple - Vente & SAV',
    rating=4.8
)

Product.objects.create(name='MacBook Pro 14"', price=2499.99, store=mac_store, category='Ordinateur', description='M4 Pro - 512GB')
Product.objects.create(name='MacBook Air M3', price=1499.99, store=mac_store, category='Ordinateur', description='256GB')
Product.objects.create(name='Magic Mouse', price=99.99, store=mac_store, category='Accessoire', description='Souris tactile sans fil')

dior_store = Store.objects.create(
    name='Dior Boutique - Faubourg',
    category='boutique',
    description='Mode luxe Dior',
    rating=4.7
)

Product.objects.create(name='T-shirt Dior', price=599.99, store=dior_store, category='T-shirt', description='Coton blanc premium')
Product.objects.create(name='Pantalon Dior', price=1299.99, store=dior_store, category='Pantalon', description='Toile noire')
Product.objects.create(name='Chaussures Dior', price=999.99, store=dior_store, category='Chaussure', description='Sneaker haute')
Product.objects.create(name='Ceinture Dior', price=799.99, store=dior_store, category='Accessoire', description='Cuir avec boucle or')

chanel_store = Store.objects.create(
    name='Chanel - Place Vendôme',
    category='boutique',
    description='Parfums et accessoires Chanel',
    rating=4.9
)

Product.objects.create(name='Chanel No. 5', price=129.99, store=chanel_store, category='Parfum', description='100ml')
Product.objects.create(name='Coco Mademoiselle', price=119.99, store=chanel_store, category='Parfum', description='100ml')
Product.objects.create(name='J12 Montre', price=5999.99, store=chanel_store, category='Montre', description='Céramique noire')

louis_vuitton = Store.objects.create(
    name='Louis Vuitton - Champs',
    category='boutique',
    description='Maroquinerie de luxe Louis Vuitton',
    rating=4.8
)

Product.objects.create(name='Sac Speedy', price=1360.00, store=louis_vuitton, category='Sac', description='Monogram')
Product.objects.create(name='Pochette Métis', price=1080.00, store=louis_vuitton, category='Sac', description='Cuir épi')
Product.objects.create(name='Portefeuille', price=465.00, store=louis_vuitton, category='Accessoire', description='Damier')

# ============ PHARMACIE ============
pharmacie = Store.objects.create(
    name='Pharmacie du Marais',
    category='pharmacie',
    description='Pharmacie généraliste avec beaux produits',
    rating=4.4
)

Product.objects.create(name='Doliprane 500mg', price=5.99, store=pharmacie, category='Médicament', description='12 comprimés')
Product.objects.create(name='Vitamine C 1000mg', price=7.99, store=pharmacie, category='Vitamine', description='20 comprimés')
Product.objects.create(name='Sérum physiologique', price=3.49, store=pharmacie, category='Soin', description='250ml')
Product.objects.create(name='Crème hydratante', price=12.99, store=pharmacie, category='Beauté', description='50ml visage')
Product.objects.create(name='Shampooing cheveux', price=8.99, store=pharmacie, category='Beauté', description='200ml')
Product.objects.create(name='Masque visage', price=15.99, store=pharmacie, category='Beauté', description='100ml hydratant')

# ============ LIVRAISON ============
driver1 = Driver.objects.create(
    name='Jean Dupont',
    phone='+33612345678',
    vehicle='Toyota Prius',
    rating=4.9,
    is_available=True,
    latitude=48.8566,
    longitude=2.3522
)

driver2 = Driver.objects.create(
    name='Marie Bernard',
    phone='+33698765432',
    vehicle='Renault Clio',
    rating=4.8,
    is_available=True,
    latitude=48.8600,
    longitude=2.3500
)

driver3 = Driver.objects.create(
    name='Pierre Martin',
    phone='+33612121212',
    vehicle='Peugeot 206',
    rating=4.7,
    is_available=False,
    latitude=48.8450,
    longitude=2.3680
)

print("✓ Données initialisées avec succès !")
print(f"✓ {Store.objects.count()} magasins créés")
print(f"✓ {Product.objects.count()} produits créés")
print(f"✓ {Driver.objects.count()} livreurs créés")
