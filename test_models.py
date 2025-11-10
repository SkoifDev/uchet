"""
Модуль тестирования для models.py
"""

import unittest
from models import Client, Product, Order, OrderItem
from datetime import datetime


class TestClient(unittest.TestCase):
    """Тесты для класса Client."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.valid_client = Client("Иван Иванов", "ivan@example.com", "+7-123-456-78-90", "Москва")

    def test_client_creation(self):
        """Тест создания клиента."""
        self.assertEqual(self.valid_client.name, "Иван Иванов")
        self.assertEqual(self.valid_client.email, "ivan@example.com")
        self.assertEqual(self.valid_client.phone, "+7-123-456-78-90")
        self.assertEqual(self.valid_client.address, "Москва")

    def test_email_validation(self):
        """Тест валидации email."""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]

        for email in valid_emails:
            client = Client("Test", email, "+7-123-456-78-90")
            self.assertEqual(client.email, email)

        # Invalid emails
        invalid_emails = [
            "invalid",
            "invalid@",
            "@domain.com",
            "invalid@domain"
        ]

        for email in invalid_emails:
            with self.assertRaises(ValueError):
                Client("Test", email, "+7-123-456-78-90")

    def test_phone_validation(self):
        """Тест валидации телефона."""
        # Valid phones
        valid_phones = [
            "+7-123-456-78-90",
            "8-123-456-78-90",
            "+71234567890"
        ]

        for phone in valid_phones:
            client = Client("Test", "test@example.com", phone)
            self.assertEqual(client.phone, phone)

    def test_add_order(self):
        """Тест добавления заказа клиенту."""
        product = Product("Тестовый товар", 1000.0)
        order = Order(self.valid_client)
        order.add_item(product, 2)

        self.assertEqual(len(self.valid_client.orders), 1)
        self.assertEqual(self.valid_client.orders[0], order)

    def test_total_spent(self):
        """Тест расчета общей суммы потраченных средств."""
        product1 = Product("Товар 1", 500.0)
        product2 = Product("Товар 2", 300.0)

        order1 = Order(self.valid_client)
        order1.add_item(product1, 1)

        order2 = Order(self.valid_client)
        order2.add_item(product2, 2)

        expected_total = 500.0 + 600.0  # 500 + (300 * 2)
        self.assertEqual(self.valid_client.get_total_spent(), expected_total)


class TestProduct(unittest.TestCase):
    """Тесты для класса Product."""

    def test_product_creation(self):
        """Тест создания товара."""
        product = Product("Ноутбук", 50000.0, "Электроника", "Мощный ноутбук")

        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.price, 50000.0)
        self.assertEqual(product.category, "Электроника")
        self.assertEqual(product.description, "Мощный ноутбук")

    def test_product_price_validation(self):
        """Тест валидации цены товара."""
        # Valid price
        product = Product("Товар", 100.0)
        self.assertEqual(product.price, 100.0)

        # Invalid price (negative)
        with self.assertRaises(ValueError):
            Product("Товар", -50.0)

        # Setting invalid price
        product = Product("Товар", 100.0)
        with self.assertRaises(ValueError):
            product.price = -10.0


class TestOrder(unittest.TestCase):
    """Тесты для класса Order."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = Client("Тест Клиент", "test@example.com", "+7-123-456-78-90")
        self.product1 = Product("Товар 1", 100.0)
        self.product2 = Product("Товар 2", 200.0)

    def test_order_creation(self):
        """Тест создания заказа."""
        order = Order(self.client)

        self.assertEqual(order.client, self.client)
        self.assertEqual(order.status, "Новый")
        self.assertEqual(len(order.items), 0)
        self.assertEqual(order.total_amount, 0.0)

    def test_add_items(self):
        """Тест добавления товаров в заказ."""
        order = Order(self.client)

        order.add_item(self.product1, 2)
        order.add_item(self.product2, 1)

        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.total_amount, 400.0)  # (100 * 2) + (200 * 1)

    def test_remove_item(self):
        """Тест удаления товара из заказа."""
        order = Order(self.client)

        order.add_item(self.product1, 2)
        order.add_item(self.product2, 1)

        self.assertEqual(len(order.items), 2)

        order.remove_item(self.product1)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].product, self.product2)


class TestOrderItem(unittest.TestCase):
    """Тесты для класса OrderItem."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.product = Product("Тестовый товар", 150.0)

    def test_order_item_creation(self):
        """Тест создания позиции заказа."""
        item = OrderItem(self.product, 3)

        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.total_price, 450.0)  # 150 * 3

    def test_quantity_validation(self):
        """Тест валидации количества."""
        # Valid quantity
        item = OrderItem(self.product, 5)
        self.assertEqual(item.quantity, 5)

        # Invalid quantity
        with self.assertRaises(ValueError):
            OrderItem(self.product, 0)

        # Setting invalid quantity
        item = OrderItem(self.product, 2)
        with self.assertRaises(ValueError):
            item.quantity = -1


if __name__ == "__main__":
    unittest.main()