"""
Модуль тестирования для analysis.py
"""

import unittest
from models import Client, Product, Order
from analysis import DataAnalyzer
from datetime import datetime, timedelta


class TestDataAnalyzer(unittest.TestCase):
    """Тесты для класса DataAnalyzer."""

    def setUp(self):
        """Настройка тестовых данных."""
        # Создаем клиентов
        self.client1 = Client("Иван Иванов", "ivan@example.com", "+7-111-111-11-11")
        self.client2 = Client("Петр Петров", "petr@example.com", "+7-222-222-22-22")
        self.client3 = Client("Сергей Сергеев", "sergey@example.com", "+7-333-333-33-33")

        # Создаем товары
        self.product1 = Product("Ноутбук", 50000.0, "Электроника")
        self.product2 = Product("Мышь", 1500.0, "Электроника")
        self.product3 = Product("Клавиатура", 3000.0, "Электроника")
        self.product4 = Product("Книга", 500.0, "Книги")

        # Создаем заказы
        self.orders = []

        # Заказы для client1
        order1 = Order(self.client1, datetime.now() - timedelta(days=3))
        order1.add_item(self.product1, 1)
        order1.add_item(self.product2, 2)
        self.orders.append(order1)

        order2 = Order(self.client1, datetime.now() - timedelta(days=1))
        order2.add_item(self.product3, 1)
        self.orders.append(order2)

        # Заказы для client2
        order3 = Order(self.client2, datetime.now() - timedelta(days=2))
        order3.add_item(self.product4, 5)
        self.orders.append(order3)

        # Заказы для client3 (нет заказов)

        self.clients = [self.client1, self.client2, self.client3]
        self.products = [self.product1, self.product2, self.product3, self.product4]

        self.analyzer = DataAnalyzer(self.clients, self.products, self.orders)

    def test_get_top_clients_by_orders(self):
        """Тест получения топ клиентов по заказам."""
        top_clients = self.analyzer.get_top_clients_by_orders(2)

        self.assertEqual(len(top_clients), 2)

        # client1 должен быть первым (2 заказа)
        self.assertEqual(top_clients[0]['client'], self.client1)
        self.assertEqual(top_clients[0]['order_count'], 2)

        # client2 должен быть вторым (1 заказ)
        self.assertEqual(top_clients[1]['client'], self.client2)
        self.assertEqual(top_clients[1]['order_count'], 1)

    def test_get_top_products_by_sales(self):
        """Тест получения топ товаров по продажам."""
        top_products = self.analyzer.get_top_products_by_sales(3)

        self.assertEqual(len(top_products), 3)

        # product4 должен быть первым (5 продаж)
        self.assertEqual(top_products[0]['product'], self.product4)
        self.assertEqual(top_products[0]['quantity_sold'], 5)

        # product2 должен быть вторым (2 продажи)
        self.assertEqual(top_products[1]['product'], self.product2)
        self.assertEqual(top_products[1]['quantity_sold'], 2)

    def test_get_orders_dynamics(self):
        """Тест получения динамики заказов."""
        dynamics = self.analyzer.get_orders_dynamics()

        self.assertIsInstance(dynamics, dict)
        self.assertIn('order_count', dynamics)
        self.assertIn('revenue', dynamics)

        # Должно быть 3 дня с заказами
        self.assertEqual(len(dynamics['order_count']), 3)
        self.assertEqual(len(dynamics['revenue']), 3)

    def test_recursive_date_sort(self):
        """Тест рекурсивной сортировки дат."""
        dates = ['2023-01-03', '2023-01-01', '2023-01-02']
        sorted_dates = self.analyzer._recursive_date_sort(dates)

        expected = ['2023-01-01', '2023-01-02', '2023-01-03']
        self.assertEqual(sorted_dates, expected)

    def test_generate_sales_report(self):
        """Тест генерации отчета о продажах."""
        report = self.analyzer.generate_sales_report()

        self.assertIsInstance(report, dict)
        self.assertIn('total_orders', report)
        self.assertIn('total_revenue', report)
        self.assertIn('total_clients', report)
        self.assertIn('top_clients', report)
        self.assertIn('top_products', report)

        self.assertEqual(report['total_orders'], 3)
        self.assertEqual(report['total_clients'], 3)

        # Проверяем расчет общей выручки
        expected_revenue = (
                50000.0 + (1500.0 * 2) +  # order1
                3000.0 +  # order2
                (500.0 * 5)  # order3
        )
        self.assertEqual(report['total_revenue'], expected_revenue)


if __name__ == "__main__":
    unittest.main()