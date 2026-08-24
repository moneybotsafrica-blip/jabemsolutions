from django.test import TestCase
from django.urls import reverse

from .models import Brand, Category, Product, Stock


class ProductStockTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Terminals", kind="hardware")
        self.brand = Brand.objects.create(name="TestBrand")
        self.product = Product.objects.create(
            name="Test Terminal",
            sku="TT-001",
            category=self.category,
            brand=self.brand,
            product_type="hardware",
            price=10000,
            reorder_level=3,
        )
        self.stock = Stock.objects.create(product=self.product, quantity_on_hand=10)

    def test_stock_out_reduces_quantity_and_logs_movement(self):
        self.stock.adjust(-4, "out", reference="Sale #1")
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity_on_hand, 6)
        self.assertEqual(self.product.movements.count(), 1)
        self.assertEqual(self.product.movements.first().resulting_quantity, 6)

    def test_stock_in_increases_quantity(self):
        self.stock.adjust(5, "in", reference="PO #1")
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity_on_hand, 15)

    def test_oversell_is_blocked(self):
        with self.assertRaises(ValueError):
            self.stock.adjust(-999, "out", reference="Bad sale")
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity_on_hand, 10)
        self.assertEqual(self.product.movements.count(), 0)

    def test_low_stock_flag(self):
        self.stock.adjust(-8, "out", reference="Big sale")
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_low_stock)


class ProductViewTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Software", kind="software")
        self.product = Product.objects.create(
            name="POS Suite",
            sku="SW-001",
            category=category,
            product_type="software",
            price=5000,
            track_inventory=False,
        )

    def test_product_list_returns_200(self):
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "POS Suite")

    def test_product_detail_returns_200(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_inactive_product_returns_404(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 404)
