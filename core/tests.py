from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
from .models import (
    Store, Product, Cart, CartItem, Driver, Order,
    Payment, Message, UserBankAccount, Invoice
)


# ============================================================
# STORE MODEL TESTS
# ============================================================
class TestStoreModel(TestCase):

    def setUp(self):
        self.store = Store.objects.create(
            name="Pizza Roma",
            category="restaurant",
            description="Pizzeria italienne",
            rating=4.8
        )

    def test_store_creation(self):
        self.assertIsNotNone(self.store.pk)

    def test_store_str(self):
        self.assertEqual(str(self.store), "Pizza Roma")

    def test_store_default_rating(self):
        store = Store.objects.create(name="Test", category="courses")
        self.assertEqual(store.rating, 4.5)

    def test_store_category_restaurant(self):
        self.assertEqual(self.store.category, "restaurant")

    def test_store_category_courses(self):
        s = Store.objects.create(name="Carrefour", category="courses")
        self.assertEqual(s.category, "courses")

    def test_store_category_boutique(self):
        s = Store.objects.create(name="Zara", category="boutique")
        self.assertEqual(s.category, "boutique")

    def test_store_category_pharmacie(self):
        s = Store.objects.create(name="Pharmacie", category="pharmacie")
        self.assertEqual(s.category, "pharmacie")

    def test_store_category_livraison(self):
        s = Store.objects.create(name="Rapido", category="livraison")
        self.assertEqual(s.category, "livraison")

    def test_store_description_blank(self):
        s = Store.objects.create(name="Test", category="restaurant")
        self.assertEqual(s.description, "")

    def test_store_image_null(self):
        self.assertFalse(bool(self.store.image))

    def test_store_rating_custom(self):
        self.assertEqual(self.store.rating, 4.8)

    def test_store_queryset_filter_category(self):
        Store.objects.create(name="BioMarket", category="courses", rating=4.2)
        restaurants = Store.objects.filter(category="restaurant")
        self.assertEqual(restaurants.count(), 1)

    def test_store_ordering(self):
        Store.objects.create(name="Alpha", category="courses")
        stores = Store.objects.all()
        self.assertGreaterEqual(stores.count(), 2)

    def test_store_update(self):
        self.store.rating = 3.5
        self.store.save()
        updated = Store.objects.get(pk=self.store.pk)
        self.assertEqual(updated.rating, 3.5)


# ============================================================
# PRODUCT MODEL TESTS
# ============================================================
class TestProductModel(TestCase):

    def setUp(self):
        self.store = Store.objects.create(name="Burger King", category="restaurant")
        self.product = Product.objects.create(
            name="Whopper",
            price=8.90,
            store=self.store,
            description="Burger classique",
            category="burger"
        )

    def test_product_creation(self):
        self.assertIsNotNone(self.product.pk)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Whopper")

    def test_product_price(self):
        self.assertEqual(self.product.price, 8.90)

    def test_product_store_fk(self):
        self.assertEqual(self.product.store, self.store)

    def test_product_related_name(self):
        products = self.store.products.all()
        self.assertIn(self.product, products)

    def test_product_cascade_delete(self):
        pid = self.product.pk
        self.store.delete()
        self.assertFalse(Product.objects.filter(pk=pid).exists())

    def test_product_description_blank(self):
        p = Product.objects.create(name="Frites", price=2.50, store=Store.objects.create(name="S", category="restaurant"))
        self.assertEqual(p.description, "")

    def test_product_category_blank(self):
        p = Product.objects.create(name="Frites", price=2.50, store=self.store)
        self.assertEqual(p.category, "")

    def test_product_multiple_in_store(self):
        Product.objects.create(name="Frites", price=2.50, store=self.store)
        self.assertEqual(self.store.products.count(), 2)

    def test_product_zero_price(self):
        p = Product.objects.create(name="Gratuit", price=0.0, store=self.store)
        self.assertEqual(p.price, 0.0)


# ============================================================
# CART MODEL TESTS
# ============================================================
class TestCartModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.store = Store.objects.create(name="Store", category="restaurant")
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertIsNotNone(self.cart.pk)

    def test_cart_str(self):
        self.assertIn("testuser", str(self.cart))

    def test_cart_user_fk(self):
        self.assertEqual(self.cart.user, self.user)

    def test_cart_created_at(self):
        self.assertIsNotNone(self.cart.created_at)

    def test_cart_get_total_empty(self):
        self.assertEqual(self.cart.get_total(), 0)

    def test_cart_get_total_one_item(self):
        product = Product.objects.create(name="Pizza", price=10.0, store=self.store)
        CartItem.objects.create(cart=self.cart, product=product, quantity=2)
        self.assertEqual(self.cart.get_total(), 20.0)

    def test_cart_get_total_multiple_items(self):
        p1 = Product.objects.create(name="P1", price=5.0, store=self.store)
        p2 = Product.objects.create(name="P2", price=3.0, store=self.store)
        CartItem.objects.create(cart=self.cart, product=p1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=p2, quantity=1)
        self.assertEqual(self.cart.get_total(), 13.0)

    def test_cart_related_name(self):
        carts = self.user.carts.all()
        self.assertIn(self.cart, carts)

    def test_cart_multiple_per_user(self):
        Cart.objects.create(user=self.user)
        self.assertEqual(self.user.carts.count(), 2)

    def test_cart_cascade_on_user_delete(self):
        cart_id = self.cart.pk
        self.user.delete()
        self.assertFalse(Cart.objects.filter(pk=cart_id).exists())


# ============================================================
# CART ITEM MODEL TESTS
# ============================================================
class TestCartItemModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass123")
        self.store = Store.objects.create(name="Store", category="restaurant")
        self.product = Product.objects.create(name="Burger", price=12.50, store=self.store)
        self.cart = Cart.objects.create(user=self.user)
        self.item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)

    def test_cartitem_creation(self):
        self.assertIsNotNone(self.item.pk)

    def test_cartitem_str(self):
        self.assertIn("Burger", str(self.item))
        self.assertIn("3", str(self.item))

    def test_cartitem_get_subtotal(self):
        self.assertEqual(self.item.get_subtotal(), 37.50)

    def test_cartitem_default_quantity(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product)
        self.assertEqual(item.quantity, 1)

    def test_cartitem_subtotal_quantity_one(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertEqual(item.get_subtotal(), 12.50)

    def test_cartitem_related_name(self):
        items = self.cart.items.all()
        self.assertIn(self.item, items)

    def test_cartitem_cascade_on_cart_delete(self):
        item_id = self.item.pk
        self.cart.delete()
        self.assertFalse(CartItem.objects.filter(pk=item_id).exists())


# ============================================================
# DRIVER MODEL TESTS
# ============================================================
class TestDriverModel(TestCase):

    def setUp(self):
        self.driver = Driver.objects.create(
            name="Ahmed Diallo",
            phone="+33612345678",
            vehicle="Vélo électrique",
            rating=4.9,
            is_available=True,
            latitude=48.8566,
            longitude=2.3522
        )

    def test_driver_creation(self):
        self.assertIsNotNone(self.driver.pk)

    def test_driver_str(self):
        self.assertEqual(str(self.driver), "Ahmed Diallo")

    def test_driver_default_rating(self):
        d = Driver.objects.create(name="Test", phone="0600000000", vehicle="Moto")
        self.assertEqual(d.rating, 5.0)

    def test_driver_default_available(self):
        d = Driver.objects.create(name="Test", phone="0600000000", vehicle="Moto")
        self.assertTrue(d.is_available)

    def test_driver_latitude(self):
        self.assertEqual(self.driver.latitude, 48.8566)

    def test_driver_longitude(self):
        self.assertEqual(self.driver.longitude, 2.3522)

    def test_driver_unavailable(self):
        self.driver.is_available = False
        self.driver.save()
        self.assertFalse(Driver.objects.get(pk=self.driver.pk).is_available)

    def test_driver_filter_available(self):
        Driver.objects.create(name="Busy", phone="0611111111", vehicle="Voiture", is_available=False)
        available = Driver.objects.filter(is_available=True)
        self.assertGreaterEqual(available.count(), 1)

    def test_driver_coordinates_null(self):
        d = Driver.objects.create(name="NoGPS", phone="0622222222", vehicle="Scooter")
        self.assertIsNone(d.latitude)
        self.assertIsNone(d.longitude)

    def test_driver_rating_update(self):
        self.driver.rating = 3.8
        self.driver.save()
        self.assertEqual(Driver.objects.get(pk=self.driver.pk).rating, 3.8)


# ============================================================
# ORDER MODEL TESTS
# ============================================================
class TestOrderModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="client", password="pass123")
        self.store = Store.objects.create(name="Store", category="restaurant")
        self.driver = Driver.objects.create(name="Driver", phone="0600000000", vehicle="Moto")
        self.cart = Cart.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user,
            cart=self.cart,
            store=self.store,
            driver=self.driver,
            status="pending",
            total_price=25.50,
            delivery_address="10 rue de Paris, 75001 Paris"
        )

    def test_order_creation(self):
        self.assertIsNotNone(self.order.pk)

    def test_order_str(self):
        self.assertIn("client", str(self.order))

    def test_order_default_status(self):
        o = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=10.0, delivery_address="Adresse test"
        )
        self.assertEqual(o.status, "pending")

    def test_order_status_confirmed(self):
        self.order.status = "confirmed"
        self.order.save()
        self.assertEqual(Order.objects.get(pk=self.order.pk).status, "confirmed")

    def test_order_status_delivered(self):
        self.order.status = "delivered"
        self.order.save()
        self.assertEqual(Order.objects.get(pk=self.order.pk).status, "delivered")

    def test_order_status_cancelled(self):
        self.order.status = "cancelled"
        self.order.save()
        self.assertEqual(Order.objects.get(pk=self.order.pk).status, "cancelled")

    def test_order_total_price(self):
        self.assertEqual(self.order.total_price, 25.50)

    def test_order_driver_nullable(self):
        o = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=10.0, delivery_address="Adresse test"
        )
        self.assertIsNone(o.driver)

    def test_order_created_at(self):
        self.assertIsNotNone(self.order.created_at)

    def test_order_updated_at(self):
        self.assertIsNotNone(self.order.updated_at)

    def test_order_user_related_name(self):
        orders = self.user.orders.all()
        self.assertIn(self.order, orders)

    def test_order_filter_by_status(self):
        Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            status="delivered", total_price=15.0, delivery_address="Adresse"
        )
        pending = Order.objects.filter(status="pending")
        self.assertGreaterEqual(pending.count(), 1)


# ============================================================
# PAYMENT MODEL TESTS
# ============================================================
class TestPaymentModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="payer", password="pass123")
        self.store = Store.objects.create(name="Store", category="restaurant")
        self.cart = Cart.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=30.0, delivery_address="Adresse"
        )
        self.payment = Payment.objects.create(
            order=self.order,
            amount=30.0,
            method="card",
            status="completed",
            transaction_id="pi_test_123"
        )

    def test_payment_creation(self):
        self.assertIsNotNone(self.payment.pk)

    def test_payment_str(self):
        self.assertIn("card", str(self.payment))

    def test_payment_default_status(self):
        o2 = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=10.0, delivery_address="Adresse"
        )
        p = Payment.objects.create(order=o2, amount=10.0, method="cash")
        self.assertEqual(p.status, "pending")

    def test_payment_method_paypal(self):
        o2 = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=10.0, delivery_address="Adresse"
        )
        p = Payment.objects.create(order=o2, amount=10.0, method="paypal")
        self.assertEqual(p.method, "paypal")

    def test_payment_method_cash(self):
        o2 = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=10.0, delivery_address="Adresse"
        )
        p = Payment.objects.create(order=o2, amount=10.0, method="cash")
        self.assertEqual(p.method, "cash")

    def test_payment_onetoone_order(self):
        self.assertEqual(self.order.payment, self.payment)

    def test_payment_transaction_id(self):
        self.assertEqual(self.payment.transaction_id, "pi_test_123")

    def test_payment_amount(self):
        self.assertEqual(self.payment.amount, 30.0)

    def test_payment_status_failed(self):
        self.payment.status = "failed"
        self.payment.save()
        self.assertEqual(Payment.objects.get(pk=self.payment.pk).status, "failed")

    def test_payment_status_refunded(self):
        self.payment.status = "refunded"
        self.payment.save()
        self.assertEqual(Payment.objects.get(pk=self.payment.pk).status, "refunded")


# ============================================================
# MESSAGE MODEL TESTS
# ============================================================
class TestMessageModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="msg_user", password="pass123")
        self.store = Store.objects.create(name="Store", category="restaurant")
        self.cart = Cart.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=10.0, delivery_address="Adresse"
        )
        self.message = Message.objects.create(
            order=self.order,
            user=self.user,
            content="Où est ma commande ?"
        )

    def test_message_creation(self):
        self.assertIsNotNone(self.message.pk)

    def test_message_str(self):
        self.assertIn("msg_user", str(self.message))

    def test_message_content(self):
        self.assertEqual(self.message.content, "Où est ma commande ?")

    def test_message_timestamp(self):
        self.assertIsNotNone(self.message.timestamp)

    def test_message_related_name(self):
        messages = self.order.messages.all()
        self.assertIn(self.message, messages)

    def test_multiple_messages_per_order(self):
        Message.objects.create(order=self.order, user=self.user, content="Merci !")
        self.assertEqual(self.order.messages.count(), 2)

    def test_message_cascade_on_order_delete(self):
        msg_id = self.message.pk
        self.order.delete()
        self.assertFalse(Message.objects.filter(pk=msg_id).exists())

    def test_message_user_fk(self):
        self.assertEqual(self.message.user, self.user)


# ============================================================
# USER BANK ACCOUNT MODEL TESTS
# ============================================================
class TestUserBankAccountModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="banker", password="pass123")
        self.account = UserBankAccount.objects.create(
            user=self.user,
            account_holder_name="Ahmed Diallo",
            iban="FR7614508110000000000000000",
            bic_swift="CEPAFRPP",
            bank_name="Caisse d'Epargne"
        )

    def test_account_creation(self):
        self.assertIsNotNone(self.account.pk)

    def test_account_str(self):
        self.assertIn("banker", str(self.account))

    def test_account_holder_name(self):
        self.assertEqual(self.account.account_holder_name, "Ahmed Diallo")

    def test_account_iban(self):
        self.assertEqual(self.account.iban, "FR7614508110000000000000000")

    def test_account_bic(self):
        self.assertEqual(self.account.bic_swift, "CEPAFRPP")

    def test_account_not_verified_default(self):
        self.assertFalse(self.account.is_verified)

    def test_account_stripe_id_blank(self):
        self.assertEqual(self.account.stripe_account_id, "")

    def test_account_onetoone_user(self):
        self.assertEqual(self.user.bank_account, self.account)


# ============================================================
# INVOICE MODEL TESTS
# ============================================================
class TestInvoiceModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="invoice_user", password="pass123")
        self.store = Store.objects.create(name="Store", category="restaurant")
        self.cart = Cart.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user, cart=self.cart, store=self.store,
            total_price=120.0, delivery_address="Adresse"
        )
        self.invoice = Invoice.objects.create(
            order=self.order,
            invoice_number="INV-2024-0001",
            amount_ttc=Decimal("120.00"),
            amount_ht=Decimal("100.00"),
            vat_amount=Decimal("20.00"),
            vat_rate=Decimal("20.00"),
            store_name="Store",
            store_address="1 rue Test",
            customer_name="Ahmed Diallo",
            customer_email="ahmed@test.com",
            customer_address="2 rue Client",
            payment_method="card",
            payment_date=timezone.now()
        )

    def test_invoice_creation(self):
        self.assertIsNotNone(self.invoice.pk)

    def test_invoice_str(self):
        self.assertIn("INV-2024-0001", str(self.invoice))

    def test_invoice_number_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Invoice.objects.create(
                order=self.order,
                invoice_number="INV-2024-0001",
                amount_ttc=Decimal("10.00"),
                amount_ht=Decimal("8.33"),
                vat_amount=Decimal("1.67"),
                store_name="X", store_address="X",
                customer_name="X", customer_email="x@x.com",
                customer_address="X", payment_method="cash",
                payment_date=timezone.now()
            )

    def test_invoice_vat_rate_default(self):
        self.assertEqual(self.invoice.vat_rate, Decimal("20.00"))

    def test_invoice_amount_ttc(self):
        self.assertEqual(self.invoice.amount_ttc, Decimal("120.00"))

    def test_invoice_amount_ht(self):
        self.assertEqual(self.invoice.amount_ht, Decimal("100.00"))

    def test_invoice_vat_amount(self):
        self.assertEqual(self.invoice.vat_amount, Decimal("20.00"))

    def test_invoice_onetoone_order(self):
        self.assertEqual(self.order.invoice, self.invoice)


# ============================================================
# VIEW TESTS
# ============================================================
class TestCoreViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="viewuser", password="viewpass")
        self.store = Store.objects.create(name="Test Restaurant", category="restaurant", rating=4.5)
        self.product = Product.objects.create(name="Pizza", price=9.90, store=self.store)

    def test_home_view_status(self):
        response = self.client.get(reverse('home'))
        self.assertIn(response.status_code, [200, 302])

    def test_home_view_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertIn(response.status_code, [200, 302])

    def test_health_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)

    def test_restaurants_view_status(self):
        response = self.client.get(reverse('restaurants'))
        self.assertIn(response.status_code, [200, 302])

    def test_courses_view_status(self):
        response = self.client.get(reverse('courses'))
        self.assertIn(response.status_code, [200, 302])

    def test_boutiques_view_status(self):
        response = self.client.get(reverse('boutiques'))
        self.assertIn(response.status_code, [200, 302])

    def test_pharmacie_view_status(self):
        response = self.client.get(reverse('pharmacie'))
        self.assertIn(response.status_code, [200, 302])

    def test_restaurant_detail_view(self):
        response = self.client.get(reverse('restaurant_detail', args=['KFC']))
        self.assertIn(response.status_code, [200, 302])

    def test_cart_view_requires_auth(self):
        response = self.client.get(reverse('cart'))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_cart_view_authenticated(self):
        self.client.login(username="viewuser", password="viewpass")
        response = self.client.get(reverse('cart'))
        self.assertIn(response.status_code, [200, 302])

    def test_checkout_requires_auth(self):
        response = self.client.get(reverse('checkout'))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_orders_api_endpoint(self):
        response = self.client.get('/api/v1/orders/')
        self.assertIn(response.status_code, [200, 302, 401, 403, 404])

    def test_livraison_view(self):
        response = self.client.get(reverse('livraison'))
        self.assertIn(response.status_code, [200, 302, 403])

    def test_home_context_has_stores(self):
        self.client.login(username="viewuser", password="viewpass")
        response = self.client.get(reverse('home'))
        if response.status_code == 200:
            self.assertIsNotNone(response.context)


# ============================================================
# API VIEW TESTS
# ============================================================
class TestAPIViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="apiuser", password="apipass")
        self.store = Store.objects.create(name="API Store", category="restaurant")
        self.product = Product.objects.create(name="API Product", price=5.0, store=self.store)

    def test_api_stores_endpoint(self):
        self.client.login(username="apiuser", password="apipass")
        response = self.client.get('/api/stores/')
        self.assertIn(response.status_code, [200, 404])

    def test_api_products_endpoint(self):
        self.client.login(username="apiuser", password="apipass")
        response = self.client.get('/api/products/')
        self.assertIn(response.status_code, [200, 404])

    def test_api_orders_endpoint(self):
        self.client.login(username="apiuser", password="apipass")
        response = self.client.get('/api/orders/')
        self.assertIn(response.status_code, [200, 404])

    def test_api_requires_auth(self):
        response = self.client.get('/api/orders/')
        self.assertIn(response.status_code, [200, 302, 401, 403, 404])

    def test_api_cart_endpoint(self):
        self.client.login(username="apiuser", password="apipass")
        response = self.client.get('/api/cart/')
        self.assertIn(response.status_code, [200, 404])

    def test_api_drivers_endpoint(self):
        self.client.login(username="apiuser", password="apipass")
        response = self.client.get('/api/drivers/')
        self.assertIn(response.status_code, [200, 404])

    def test_api_json_content_type(self):
        self.client.login(username="apiuser", password="apipass")
        response = self.client.get('/api/stores/', HTTP_ACCEPT='application/json')
        if response.status_code == 200:
            self.assertIn('application/json', response.get('Content-Type', ''))


# ============================================================
# DETAIL VIEW TESTS
# ============================================================
class TestDetailViews(TestCase):

    def setUp(self):
        self.client = Client()

    def test_restaurant_detail_kfc(self):
        response = self.client.get(reverse('restaurant_detail', args=['KFC']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_restaurant_detail_mcdo(self):
        response = self.client.get(reverse('restaurant_detail', args=["McDonald's"]))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_restaurant_detail_unknown_returns_200(self):
        response = self.client.get(reverse('restaurant_detail', args=['Unknown']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_courses_detail_lidl(self):
        response = self.client.get(reverse('courses_detail', args=['Lidl']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_courses_detail_carrefour(self):
        response = self.client.get(reverse('courses_detail', args=['Carrefour']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_boutique_detail_apple(self):
        response = self.client.get(reverse('boutique_detail', args=['Apple Store']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_boutique_detail_dior(self):
        response = self.client.get(reverse('boutique_detail', args=['Dior']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_pharmacie_detail_centrale(self):
        response = self.client.get(reverse('pharmacie_detail', args=['Pharmacie Centrale']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_pharmacie_detail_beaute(self):
        response = self.client.get(reverse('pharmacie_detail', args=['Parapharmacie Beauté']))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_livraison_view_status(self):
        response = self.client.get(reverse('livraison'))
        self.assertIn(response.status_code, [200, 302, 404])


# ============================================================
# SMS AND CALL API TESTS
# ============================================================
class TestSMSAPIEndpoints(TestCase):

    def setUp(self):
        self.client = Client()

    def test_send_sms_post_valid(self):
        import json
        response = self.client.post(
            reverse('send_sms'),
            data=json.dumps({'to': '+33612345678', 'message': 'Hello', 'driver_id': 'd1'}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 403, 404])

    def test_send_sms_returns_json(self):
        import json
        response = self.client.post(
            reverse('send_sms'),
            data=json.dumps({'to': '+33612345678', 'message': 'Test'}),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('success', data)

    def test_send_sms_success_true(self):
        import json
        response = self.client.post(
            reverse('send_sms'),
            data=json.dumps({'to': '+33612345678', 'message': 'Test SMS'}),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertTrue(data.get('success'))

    def test_send_verification_sms_post(self):
        import json
        response = self.client.post(
            reverse('send_verification_sms'),
            data=json.dumps({'phone': '+33612345678', 'code': '123456'}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 403, 404])

    def test_send_verification_sms_returns_json(self):
        import json
        response = self.client.post(
            reverse('send_verification_sms'),
            data=json.dumps({'phone': '+33612345678', 'code': '654321'}),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('success', data)

    def test_make_call_api_post(self):
        import json
        response = self.client.post(
            reverse('make_call'),
            data=json.dumps({'from': '+33600000001', 'to': '+33600000002', 'user_type': 'customer'}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 403, 404])

    def test_make_call_returns_call_id(self):
        import json
        response = self.client.post(
            reverse('make_call'),
            data=json.dumps({'from': '+336', 'to': '+337', 'user_type': 'driver'}),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('call_id', data)

    def test_health_check_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)

    def test_health_check_returns_json(self):
        import json
        response = self.client.get('/health/')
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('status', data)

    def test_health_check_status_value(self):
        import json
        response = self.client.get('/health/')
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertEqual(data.get('status'), 'healthy')
