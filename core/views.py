from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import Store, Product, Cart, CartItem, Order, Driver, Payment, Message


def home(request):
    return render(request, 'home.html')


def restaurants(request):
    stores_data = [
        {
            'name': 'KFC',
            'image': 'https://placehold.co/200x200/red/white?text=KFC',
            'description': 'Poulet frit croustillant, burgers et buckets',
            'rating': 4.5,
            'delivery_time': '25-35 min',
            'delivery_fee': 2.99,
            'address': '12 Rue de Rivoli, 75004 Paris',
            'lat': 48.8554,
            'lng': 2.3522
        },
        {
            'name': 'McDonald\'s',
            'image': 'https://placehold.co/200x200/daa520/white?text=McDo',
            'description': 'Burgers, frites, menus Happy Meal et plus',
            'rating': 4.3,
            'delivery_time': '20-30 min',
            'delivery_fee': 1.99,
            'address': '45 Avenue des Champs-Élysées, 75008 Paris',
            'lat': 48.8698,
            'lng': 2.3078
        },
        {
            'name': 'Quick',
            'image': 'https://placehold.co/200x200/ff6600/white?text=Quick',
            'description': 'Burgers savoureux et menus gourmands',
            'rating': 4.2,
            'delivery_time': '25-35 min',
            'delivery_fee': 2.49,
            'address': '28 Boulevard de Sébastopol, 75004 Paris',
            'lat': 48.8606,
            'lng': 2.3489
        }
    ]
    return render(request, 'restaurants.html', {'stores': stores_data})


def restaurant_detail(request, name):
    products_data = {
        'KFC': [
            {'name': 'Bucket 8 Tenders', 'price': 15.99, 'image': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400', 'description': '8 tenders croustillants avec 2 sauces au choix'},
            {'name': 'Twister Original', 'price': 7.49, 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 'description': 'Wrap avec tenders, salade, tomate et sauce'},
            {'name': 'Zinger Burger', 'price': 8.99, 'image': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=400', 'description': 'Burger poulet piquant avec salade et mayo'},
            {'name': 'Hot Wings x8', 'price': 8.49, 'image': 'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=400', 'description': '8 ailes de poulet épicées et croustillantes'},
            {'name': 'Colonel Original', 'price': 9.99, 'image': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400', 'description': 'Burger filet de poulet original KFC'},
            {'name': 'Box Master', 'price': 11.99, 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 'description': 'Menu complet avec burger, frites, boisson et dessert'},
        ],
        'McDonald\'s': [
            {'name': 'Big Mac', 'price': 5.79, 'image': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400', 'description': 'Double steak, sauce secrète, salade, fromage'},
            {'name': 'Happy Meal', 'price': 4.99, 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 'description': 'Menu enfant avec jouet surprise inclus'},
            {'name': 'McChicken', 'price': 6.29, 'image': 'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400', 'description': 'Burger poulet pané avec salade et mayo'},
            {'name': 'Filet-O-Fish', 'price': 5.49, 'image': 'https://images.unsplash.com/photo-1547584370-2cc98b8b8dc8?w=400', 'description': 'Filet de poque pané avec fromage et tartare'},
            {'name': '20 McNuggets', 'price': 12.99, 'image': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400', 'description': '20 morceaux de poulet pané avec 4 sauces'},
            {'name': 'McFlurry Oreo', 'price': 3.49, 'image': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400', 'description': 'Glace vanille avec morceaux d\'Oreo'},
        ],
        'Quick': [
            {'name': 'Giant Burger', 'price': 8.99, 'image': 'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400', 'description': 'Burger XXL avec double steak et fromage'},
            {'name': 'Quick N\' Toast', 'price': 6.49, 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 'description': 'Sandwich poulet grillé avec sauce spéciale'},
            {'name': 'Poupan', 'price': 5.99, 'image': 'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400', 'description': 'Burger poulet pané signature Quick'},
            {'name': 'Royal Cheese', 'price': 7.49, 'image': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400', 'description': 'Burger steak fromage avec bacon'},
            {'name': 'Fish Burger', 'price': 6.99, 'image': 'https://images.unsplash.com/photo-1547584370-2cc98b8b8dc8?w=400', 'description': 'Burger poque pané avec sauce tartare'},
            {'name': 'Menu Enfant', 'price': 5.49, 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 'description': 'Menu kids avec jouet et surprise'},
        ]
    }
    
    store_info = {
        'KFC': {'image': 'https://placehold.co/200x200/red/white?text=KFC', 'rating': 4.5},
        'McDonald\'s': {'image': 'https://placehold.co/200x200/daa520/white?text=McDo', 'rating': 4.3},
        'Quick': {'image': 'https://placehold.co/200x200/ff6600/white?text=Quick', 'rating': 4.2}
    }
    
    products = products_data.get(name, [])
    store = store_info.get(name, {})
    store['name'] = name
    
    return render(request, 'restaurant_detail.html', {'store': store, 'products': products})


def courses(request):
    stores_data = [
        {
            'name': 'Lidl',
            'image': 'https://placehold.co/200x200/0050aa/white?text=Lidl',
            'description': 'Supermarché discount avec produits de qualité',
            'rating': 4.3,
            'delivery_time': '30-45 min',
            'delivery_fee': 1.99,
            'address': '89 Rue de la Roquette, 75011 Paris',
            'lat': 48.8534,
            'lng': 2.3788
        },
        {
            'name': 'Leclerc',
            'image': 'https://placehold.co/200x200/0066cc/white?text=Leclerc',
            'description': 'Hypermarché avec large choix de produits',
            'rating': 4.5,
            'delivery_time': '35-50 min',
            'delivery_fee': 2.99,
            'address': '15 Rue Linois, 75015 Paris',
            'lat': 48.8489,
            'lng': 2.2829
        },
        {
            'name': 'Aldi',
            'image': 'https://placehold.co/200x200/0000cc/white?text=Aldi',
            'description': 'Supermarché discount européen',
            'rating': 4.2,
            'delivery_time': '30-45 min',
            'delivery_fee': 1.99,
            'address': '56 Avenue de Clichy, 75017 Paris',
            'lat': 48.8842,
            'lng': 2.3128
        },
        {
            'name': 'Carrefour',
            'image': 'https://placehold.co/200x200/cc0000/white?text=Carrefour',
            'description': 'Hypermarché international leader mondial',
            'rating': 4.4,
            'delivery_time': '35-50 min',
            'delivery_fee': 2.49,
            'address': '1 Rue de Rivoli, 75001 Paris',
            'lat': 48.8565,
            'lng': 2.3522
        },
        {
            'name': 'Super U',
            'image': 'https://placehold.co/200x200/009900/white?text=Super+U',
            'description': 'Supermarché de proximité français',
            'rating': 4.3,
            'delivery_time': '30-45 min',
            'delivery_fee': 1.99,
            'address': '32 Rue des Martyrs, 75009 Paris',
            'lat': 48.8794,
            'lng': 2.3408
        }
    ]
    return render(request, 'courses.html', {'stores': stores_data})


def courses_detail(request, name):
    products_data = {
        'Lidl': [
            {'name': 'Baguette Tradition', 'price': 0.89, 'image': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400', 'description': 'Baguette française traditionnelle'},
            {'name': 'Pâtes Barilla 500g', 'price': 1.29, 'image': 'https://images.unsplash.com/photo-1551462147-37885acc36f1?w=400', 'description': 'Pâtes italiennes de qualité supérieure'},
            {'name': 'Fromage Emmental', 'price': 2.49, 'image': 'https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=400', 'description': 'Emmental français portion 200g'},
            {'name': 'Jus d\'Orange 1L', 'price': 1.79, 'image': 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=400', 'description': 'Jus d\'orange pressé sans pulpe'},
            {'name': 'Poulet Entier', 'price': 6.99, 'image': 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400', 'description': 'Poulet fermier label rouge'},
            {'name': 'Pack Eau 6x1.5L', 'price': 2.99, 'image': 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400', 'description': 'Eau minérale naturelle'},
        ],
        'Leclerc': [
            {'name': 'Filet Mignon de Porc', 'price': 8.99, 'image': 'https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=400', 'description': 'Filet mignon tendre et savoureux 500g'},
            {'name': 'Saumon Frais', 'price': 12.99, 'image': 'https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=400', 'description': 'Saumon atlantique frais 400g'},
            {'name': 'Fromage de Chèvre', 'price': 3.49, 'image': 'https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=400', 'description': 'Fromage de chèvre affiné 200g'},
            {'name': 'Champagne Moët', 'price': 45.99, 'image': 'https://images.unsplash.com/photo-1572566424406-4e955c4a211b?w=400', 'description': 'Champagne brut impérial 75cl'},
            {'name': 'Café Grain 250g', 'price': 4.99, 'image': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400', 'description': 'Café en grains arabica premium'},
            {'name': 'Huile d\'Olive 1L', 'price': 7.99, 'image': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 'description': 'Huile d\'olive extra vierge bio'},
        ],
        'Aldi': [
            {'name': 'Lait Entier 1L', 'price': 0.99, 'image': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400', 'description': 'Lait entier UHT de qualité'},
            {'name': 'Céréales Miel', 'price': 2.19, 'image': 'https://images.unsplash.com/photo-1495214783159-3503fd1b572d?w=400', 'description': 'Céréales au miel croquantes'},
            {'name': 'Pommes Golden 1kg', 'price': 2.49, 'image': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400', 'description': 'Pommes golden délicieuses'},
            {'name': 'Poulet Rôti', 'price': 7.99, 'image': 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400', 'description': 'Poulet rôti prêt à déguster'},
            {'name': 'Yogourt Nature x4', 'price': 1.79, 'image': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400', 'description': 'Yogourt nature onctueux'},
            {'name': 'Pain de Mie', 'price': 1.29, 'image': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400', 'description': 'Pain de mie moelleux'},
        ],
        'Carrefour': [
            {'name': 'Foie Gras 90g', 'price': 18.99, 'image': 'https://images.unsplash.com/photo-1567620904195-4724f6c84539?w=400', 'description': 'Foie gras de canard mi-cuit'},
            {'name': 'Caviar 30g', 'price': 89.99, 'image': 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400', 'description': 'Caviar d\'esturgeon français'},
            {'name': 'Homard Breton', 'price': 24.99, 'image': 'https://images.unsplash.com/photo-1553659971-f01207815844?w=400', 'description': 'Homard breton vivant 600g'},
            {'name': 'Truffe Noire 50g', 'price': 65.99, 'image': 'https://images.unsplash.com/photo-1504545102780-26774c1bb073?w=400', 'description': 'Truffe noire du Périgord'},
            {'name': 'Jambon Bellota', 'price': 89.99, 'image': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400', 'description': 'Jambon ibérique pata negra'},
            {'name': 'Vin Bordeaux 2015', 'price': 35.99, 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=400', 'description': 'Château Margaux grand cru'},
        ],
        'Super U': [
            {'name': 'Comté 12 Mois', 'price': 4.99, 'image': 'https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=400', 'description': 'Comté AOP affiné 12 mois'},
            {'name': 'Saucisson Sec', 'price': 3.49, 'image': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400', 'description': 'Saucisson sec artisanal 200g'},
            {'name': 'Miel de Lavande', 'price': 6.99, 'image': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400', 'description': 'Miel de lavande de Provance 500g'},
            {'name': 'Confiture Fraise', 'price': 3.29, 'image': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400', 'description': 'Confiture de fraises de saison'},
            {'name': 'Madeleines x12', 'price': 2.79, 'image': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400', 'description': 'Madeleines traditionnelles françaises'},
            {'name': 'Cidre Brut', 'price': 4.49, 'image': 'https://images.unsplash.com/photo-1567696911980-2eed69a46042?w=400', 'description': 'Cidre brut artisanal 75cl'},
        ]
    }
    
    store_info = {
        'Lidl': {'image': 'https://placehold.co/200x200/0050aa/white?text=Lidl', 'rating': 4.3},
        'Leclerc': {'image': 'https://placehold.co/200x200/0066cc/white?text=Leclerc', 'rating': 4.5},
        'Aldi': {'image': 'https://placehold.co/200x200/0000cc/white?text=Aldi', 'rating': 4.2},
        'Carrefour': {'image': 'https://placehold.co/200x200/cc0000/white?text=Carrefour', 'rating': 4.4},
        'Super U': {'image': 'https://placehold.co/200x200/009900/white?text=Super+U', 'rating': 4.3}
    }
    
    products = products_data.get(name, [])
    store = store_info.get(name, {})
    store['name'] = name
    
    return render(request, 'courses_detail.html', {'store': store, 'products': products})


def boutiques(request):
    stores_data = [
        {
            'name': 'Apple Store',
            'image': 'https://placehold.co/200x200/333333/white?text=Apple',
            'description': 'iPhone, MacBook, iPad, Apple Watch et accessoires',
            'rating': 4.8,
            'delivery_time': '20-30 min',
            'delivery_fee': 0.00,
            'address': "1 Avenue de l'Opéra, 75001 Paris",
            'lat': 48.8656,
            'lng': 2.3344
        },
        {
            'name': 'Dior',
            'image': 'https://placehold.co/200x200/000000/white?text=Dior',
            'description': 'Mode luxe, chaussures, t-shirts, pantalons',
            'rating': 4.9,
            'delivery_time': '25-35 min',
            'delivery_fee': 5.99,
            'address': '30 Avenue Montaigne, 75008 Paris',
            'lat': 48.8661,
            'lng': 2.3037
        },
        {
            'name': 'Chanel',
            'image': 'https://placehold.co/200x200/000000/white?text=Chanel',
            'description': 'Parfums, maquillage, sacs de luxe',
            'rating': 4.9,
            'delivery_time': '25-35 min',
            'delivery_fee': 5.99,
            'address': '31 Rue Cambon, 75001 Paris',
            'lat': 48.8691,
            'lng': 2.3263
        },
        {
            'name': 'Louis Vuitton',
            'image': 'https://placehold.co/200x200/8B4513/white?text=LV',
            'description': 'Maroquinerie de luxe, sacs, bagages',
            'rating': 4.8,
            'delivery_time': '25-35 min',
            'delivery_fee': 5.99,
            'address': '101 Avenue des Champs-Élysées, 75008 Paris',
            'lat': 48.8700,
            'lng': 2.3035
        }
    ]
    return render(request, 'boutiques.html', {'stores': stores_data})


def boutique_detail(request, name):
    products_data = {
        'Apple Store': [
            {'name': 'iPhone 15 Pro Max', 'price': 1479.00, 'image': 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400', 'description': '256GB - Titane Naturel - Puce A17 Pro'},
            {'name': 'MacBook Air M3', 'price': 1299.00, 'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400', 'description': '13 pouces 256GB SSD - Puce M3'},
            {'name': 'iPad Pro 12.9"', 'price': 1249.00, 'image': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400', 'description': 'M2 128GB WiFi - Écran Liquid Retina XDR'},
            {'name': 'Apple Watch Ultra 2', 'price': 899.00, 'image': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400', 'description': 'GPS + Cellular 49mm - Titane'},
            {'name': 'AirPods Pro 2', 'price': 279.00, 'image': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400', 'description': 'Réduction active du bruit - USB-C'},
            {'name': 'Magic Keyboard', 'price': 119.00, 'image': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400', 'description': 'Clavier sans fil rechargeable - Gris sidéral'},
        ],
        'Dior': [
            {'name': 'Sneakers B23', 'price': 950.00, 'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', 'description': 'Sneakers haut de gamme toile oblique'},
            {'name': 'T-Shirt Logo', 'price': 590.00, 'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400', 'description': 'Coton bio avec logo brodé'},
            {'name': 'Pantalon Tailleur', 'price': 1290.00, 'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400', 'description': 'Laine vierge italienne - Coupe slim'},
            {'name': 'Sac Lady Dior', 'price': 4900.00, 'image': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400', 'description': 'Cuir d\'agneau cannage - Moyen modèle'},
            {'name': 'Ceinture CD', 'price': 650.00, 'image': 'https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=400', 'description': 'Cuir de veau réversible'},
            {'name': 'Lunettes Dior', 'price': 420.00, 'image': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400', 'description': 'Monture or 18K - Verres polarisés'},
        ],
        'Chanel': [
            {'name': 'Chanel N°5', 'price': 135.00, 'image': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=400', 'description': 'Eau de parfum 100ml - Légendaire'},
            {'name': 'Coco Mademoiselle', 'price': 115.00, 'image': 'https://images.unsplash.com/photo-1594035910387-fea47794261f?w=400', 'description': 'Eau de toilette 50ml - Oriental frais'},
            {'name': 'Rouge Allure', 'price': 42.00, 'image': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400', 'description': 'Rouge à lèvres velours - 99 Pirate'},
            {'name': 'Sac Classic Flap', 'price': 8900.00, 'image': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400', 'description': 'Cuir d\'agneau matelassé noir'},
            {'name': 'Vernis Gel', 'price': 28.00, 'image': 'https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?w=400', 'description': 'Vernis à ongles longue tenue'},
            {'name': 'Chance Chanel', 'price': 105.00, 'image': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400', 'description': 'Eau de toilette 50ml - Floral pétillant'},
        ],
        'Louis Vuitton': [
            {'name': 'Neverfull MM', 'price': 1750.00, 'image': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400', 'description': 'Toile monogram classique'},
            {'name': 'Keepall 55', 'price': 2150.00, 'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400', 'description': 'Sac de voyage toile monogram'},
            {'name': 'Portefeuille Zippy', 'price': 595.00, 'image': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=400', 'description': 'Cuir épi - Fermeture zippée'},
            {'name': 'Ceinture LV Initiales', 'price': 495.00, 'image': 'https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=400', 'description': 'Cuir et toile monogram réversible'},
            {'name': 'Écharpe Monogram', 'price': 425.00, 'image': 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=400', 'description': 'Laine et soie - Noir et gris'},
            {'name': 'Lunettes Aviator', 'price': 580.00, 'image': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400', 'description': 'Monture métal doré - Verres dégradés'},
        ]
    }
    
    store_info = {
        'Apple Store': {'image': 'https://placehold.co/200x200/333333/white?text=Apple', 'rating': 4.8},
        'Dior': {'image': 'https://placehold.co/200x200/000000/white?text=Dior', 'rating': 4.9},
        'Chanel': {'image': 'https://placehold.co/200x200/000000/white?text=Chanel', 'rating': 4.9},
        'Louis Vuitton': {'image': 'https://placehold.co/200x200/8B4513/white?text=LV', 'rating': 4.8}
    }
    
    products = products_data.get(name, [])
    store = store_info.get(name, {})
    store['name'] = name
    
    return render(request, 'boutique_detail.html', {'store': store, 'products': products})


def pharmacie(request):
    stores_data = [
        {
            'name': 'Pharmacie Centrale',
            'image': 'https://placehold.co/200x200/00aa44/white?text=Pharmacie',
            'description': 'Médicaments sur ordonnance et sans ordonnance',
            'rating': 4.7,
            'delivery_time': '15-25 min',
            'delivery_fee': 1.99,
            'address': '5 Rue de la Paix, 75002 Paris',
            'lat': 48.8693,
            'lng': 2.3310
        },
        {
            'name': 'Parapharmacie Beauté',
            'image': 'https://placehold.co/200x200/ff69b4/white?text=Beaute',
            'description': 'Produits de beauté, soins et cosmétiques',
            'rating': 4.6,
            'delivery_time': '20-30 min',
            'delivery_fee': 1.99,
            'address': '18 Rue du Commerce, 75015 Paris',
            'lat': 48.8450,
            'lng': 2.2939
        }
    ]
    return render(request, 'pharmacie.html', {'stores': stores_data})


def pharmacie_detail(request, name):
    products_data = {
        'Pharmacie Centrale': [
            {'name': 'Doliprane 1000mg', 'price': 3.49, 'image': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400', 'description': 'Paracétamol - 8 comprimés - Douleurs et fièvre'},
            {'name': 'Advil 400mg', 'price': 4.99, 'image': 'https://placehold.co/200x200/4287f5/white?text=Advil+400mg', 'description': 'Ibuprofène - 20 comprimés - Anti-inflammatoire'},
            {'name': 'Strepsils', 'price': 5.29, 'image': 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400', 'description': 'Pastilles pour la gorge - Miel citron'},
            {'name': 'Vitamine C 1000mg', 'price': 8.99, 'image': 'https://placehold.co/200x200/ff9500/white?text=Vitamine+C', 'description': '60 comprimés effervescents - Immunité'},
            {'name': 'Bandages Assortis', 'price': 4.49, 'image': 'https://images.unsplash.com/photo-1603398938378-e54eab446dde?w=400', 'description': 'Boîte de 40 pansements multi-tailles'},
            {'name': 'Thermomètre Digital', 'price': 12.99, 'image': 'https://placehold.co/200x200/00bcd4/white?text=Thermometre', 'description': 'Mesure rapide en 10 secondes'},
            {'name': 'Désinfectant Mains', 'price': 3.99, 'image': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400', 'description': 'Gel hydroalcoolique 500ml'},
            {'name': 'Antihistaminique', 'price': 6.99, 'image': 'https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400', 'description': 'Cetirizine 10mg - Allergies saisonnières'},
        ],
        'Parapharmacie Beauté': [
            {'name': 'Crème Hydratante Nivea', 'price': 7.99, 'image': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400', 'description': 'Pot 400ml - Peaux sensibles'},
            {'name': 'Sérum Visage', 'price': 24.99, 'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400', 'description': 'Acide hyaluronique - 30ml - Anti-âge'},
            {'name': 'Masque Cheveux', 'price': 12.99, 'image': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=400', 'description': 'Kératin repair - Cheveux abîmés'},
            {'name': 'Dentifrice Blancheur', 'price': 4.49, 'image': 'https://placehold.co/200x200/00d4aa/white?text=Dentifrice', 'description': 'Colgate - 3x75ml - Action blancheur'},
            {'name': 'Déodorant 48h', 'price': 3.99, 'image': 'https://images.unsplash.com/photo-1620916297397-a4a5402a3c6c?w=400', 'description': 'Dove - Sans alcool - Invisible'},
            {'name': 'Shampooing Doux', 'price': 5.99, 'image': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=400', 'description': 'Klorane - Usage quotidien 400ml'},
            {'name': 'Huile Corps Bio', 'price': 14.99, 'image': 'https://placehold.co/200x200/d4a574/white?text=Huile+Bio', 'description': 'Argan bio - Hydratation intense 100ml'},
            {'name': 'Rouge à Lèvres', 'price': 18.99, 'image': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400', 'description': 'Maybelline Super Stay - Tenue 24h'},
        ]
    }
    
    store_info = {
        'Pharmacie Centrale': {'image': 'https://placehold.co/200x200/00aa44/white?text=Pharmacie', 'rating': 4.7},
        'Parapharmacie Beauté': {'image': 'https://placehold.co/200x200/ff69b4/white?text=Beaute', 'rating': 4.6}
    }
    
    products = products_data.get(name, [])
    store = store_info.get(name, {})
    store['name'] = name
    
    return render(request, 'pharmacie_detail.html', {'store': store, 'products': products})


def livraison(request):
    # Get current order info from session or create default
    store = request.session.get('current_store', {
        'name': 'KFC',
        'address': '12 Rue de Rivoli, 75004 Paris',
        'lat': 48.8554,
        'lng': 2.3522
    })
    
    # Get customer address
    customer_address = request.session.get('customer_address', {
        'address': '25 Rue de la Paix, 75002 Paris',
        'lat': 48.8689,
        'lng': 2.3310
    })
    
    context = {
        'store': store,
        'customer': customer_address,
        'driver': {
            'name': 'Ahmed K.',
            'phone': '0612345678',
            'vehicle': '🚲 Vélo électrique',
            'id': 'LVR-2847',
            'rating': 4.9,
            'deliveries': 128
        }
    }
    return render(request, 'livraison.html', context)


def cart_view(request):
    return render(request, 'cart.html')


def checkout_view(request):
    return render(request, 'checkout.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Identifiants invalides')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')


def register(request):
    return render(request, 'register.html')


def bank_setup(request):
    """Bank account setup page"""
    return render(request, 'bank_setup.html')


def user_registration(request):
    """User registration with S3 storage"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email:
            try:
                from .s3_storage import s3_storage
                result = s3_storage.save_user_data(name, email, message)
                
                if result['success']:
                    messages.success(request, f"Inscription réussie ! Vos données ont été enregistrées (ID: {result['user_id'][:8]}...)")
                else:
                    messages.error(request, f"Erreur lors de l'enregistrement: {result['error']}")
                    messages.info(request, "Données sauvegardées localement.")
            except Exception as e:
                messages.error(request, f"Erreur S3: {str(e)}")
                messages.info(request, "Vérifiez la configuration AWS.")
        else:
            messages.error(request, "Nom et email sont obligatoires.")
        
        return redirect('user_registration')
    
    return render(request, 'registration_form.html')


# API Views for SMS and Voice
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def send_sms_api(request):
    """API endpoint to send SMS to driver/customer"""
    try:
        data = json.loads(request.body)
        to = data.get('to')
        message = data.get('message')
        driver_id = data.get('driver_id', 'unknown')
        
        # In production, integrate with Twilio, Vonage, or other SMS provider
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_='+1234567890',
        #     to=f'+33{to}'
        # )
        
        print(f"[SMS] To: {to}, Message: {message}, Driver: {driver_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'SMS sent successfully',
            'to': to,
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_verification_sms(request):
    """API endpoint to send verification code SMS"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')
        
        message = f"Votre code de vérification MultiServe est: {code}. Valide pendant 10 minutes."
        
        # In production, send actual SMS
        print(f"[VERIFICATION SMS] To: {phone}, Code: {code}")
        
        return JsonResponse({
            'success': True,
            'message': 'Verification code sent',
            'phone': phone,
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def make_call_api(request):
    """API endpoint to initiate voice call between two people"""
    try:
        data = json.loads(request.body)
        from_number = data.get('from')
        to_number = data.get('to')
        user_type = data.get('user_type', 'customer')  # 'customer' or 'driver'
        
        # In production, integrate with Twilio Voice or similar
        # This would create a conference call or connect two parties
        
        print(f"[VOICE CALL] From: {from_number}, To: {to_number}, Type: {user_type}")
        
        return JsonResponse({
            'success': True,
            'message': 'Call initiated',
            'call_id': f'call_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'status': 'ringing',
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': str(datetime.now()),
        'service': 'multiserve-app'
    })
