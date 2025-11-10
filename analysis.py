"""
Модуль для анализа и визуализации данных системы учёта заказов.
"""

import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from models import Client, Product, Order
import seaborn as sns
import networkx as nx


class DataAnalyzer:
    """Класс для анализа данных заказов и клиентов."""

    def __init__(self, clients: List[Client], products: List[Product], orders: List[Order]):
        """
        Инициализация анализатора данных.

        Parameters
        ----------
        clients : List[Client]
            Список клиентов
        products : List[Product]
            Список товаров
        orders : List[Order]
            Список заказов
        """
        self.clients = clients
        self.products = products
        self.orders = orders

    def get_top_clients_by_orders(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Получить топ клиентов по количеству заказов.

        Parameters
        ----------
        top_n : int, optional
            Количество клиентов в топе, по умолчанию 5

        Returns
        -------
        List[Dict[str, Any]]
            Список словарей с данными клиентов
        """
        client_orders = []
        for client in self.clients:
            client_orders.append({
                'client': client,
                'order_count': len(client.orders),
                'total_spent': client.get_total_spent()
            })

        # Сортировка по количеству заказов (лямбда-функция)
        sorted_clients = sorted(client_orders, key=lambda x: x['order_count'], reverse=True)
        return sorted_clients[:top_n]

    def get_top_products_by_sales(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Получить топ товаров по продажам.

        Parameters
        ----------
        top_n : int, optional
            Количество товаров в топе, по умолчанию 5

        Returns
        -------
        List[Dict[str, Any]]
            Список словарей с данными товаров
        """
        product_sales = {}

        for order in self.orders:
            for item in order.items:
                product_id = item.product.product_id
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'product': item.product,
                        'quantity_sold': 0,
                        'revenue': 0.0
                    }

                product_sales[product_id]['quantity_sold'] += item.quantity
                product_sales[product_id]['revenue'] += item.total_price

        # Сортировка по выручке (лямбда-функция)
        sorted_products = sorted(product_sales.values(), key=lambda x: x['revenue'], reverse=True)
        return sorted_products[:top_n]

    def get_orders_dynamics(self) -> pd.DataFrame:
        """
        Получить динамику заказов по датам.

        Returns
        -------
        pd.DataFrame
            DataFrame с динамикой заказов
        """
        dates = []
        order_counts = []
        revenues = []

        # Группировка заказов по дате
        orders_by_date = {}
        for order in self.orders:
            date_str = order.order_date.strftime('%Y-%m-%d')
            if date_str not in orders_by_date:
                orders_by_date[date_str] = {
                    'count': 0,
                    'revenue': 0.0
                }

            orders_by_date[date_str]['count'] += 1
            orders_by_date[date_str]['revenue'] += order.total_amount

        # Сортировка по дате (рекурсивный подход для демонстрации)
        sorted_dates = self._recursive_date_sort(list(orders_by_date.keys()))

        for date in sorted_dates:
            dates.append(date)
            order_counts.append(orders_by_date[date]['count'])
            revenues.append(orders_by_date[date]['revenue'])

        return pd.DataFrame({
            'date': dates,
            'order_count': order_counts,
            'revenue': revenues
        })

    def _recursive_date_sort(self, dates: List[str]) -> List[str]:
        """
        Рекурсивная сортировка дат.

        Parameters
        ----------
        dates : List[str]
            Список дат в формате 'YYYY-MM-DD'

        Returns
        -------
        List[str]
            Отсортированный список дат
        """
        if len(dates) <= 1:
            return dates

        pivot = dates[len(dates) // 2]
        left = [x for x in dates if x < pivot]
        middle = [x for x in dates if x == pivot]
        right = [x for x in dates if x > pivot]

        return self._recursive_date_sort(left) + middle + self._recursive_date_sort(right)

    def plot_orders_dynamics(self, save_path: str = None):
        """
        Построить график динамики заказов.

        Parameters
        ----------
        save_path : str, optional
            Путь для сохранения графика, по умолчанию None
        """
        dynamics = self.get_orders_dynamics()

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.plot(dynamics['date'], dynamics['order_count'], marker='o', linewidth=2)
        plt.title('Динамика количества заказов')
        plt.xlabel('Дата')
        plt.ylabel('Количество заказов')
        plt.xticks(rotation=45)

        plt.subplot(1, 2, 2)
        plt.plot(dynamics['date'], dynamics['revenue'], marker='o', color='orange', linewidth=2)
        plt.title('Динамика выручки')
        plt.xlabel('Дата')
        plt.ylabel('Выручка (руб)')
        plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def plot_top_clients(self, save_path: str = None):
        """
        Построить график топ клиентов.

        Parameters
        ----------
        save_path : str, optional
            Путь для сохранения графика, по умолчанию None
        """
        top_clients = self.get_top_clients_by_orders(8)

        if not top_clients:
            print("Нет данных для построения графика")
            return

        names = [client['client'].name for client in top_clients]
        order_counts = [client['order_count'] for client in top_clients]
        total_spent = [client['total_spent'] for client in top_clients]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # График количества заказов
        bars1 = ax1.bar(names, order_counts, color='skyblue', alpha=0.7)
        ax1.set_title('Топ клиентов по количеству заказов')
        ax1.set_xlabel('Клиенты')
        ax1.set_ylabel('Количество заказов')
        ax1.tick_params(axis='x', rotation=45)

        # Добавление значений на столбцы
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}', ha='center', va='bottom')

        # График потраченных сумм
        bars2 = ax2.bar(names, total_spent, color='lightgreen', alpha=0.7)
        ax2.set_title('Топ клиентов по потраченной сумме')
        ax2.set_xlabel('Клиенты')
        ax2.set_ylabel('Сумма (руб)')
        ax2.tick_params(axis='x', rotation=45)

        # Добавление значений на столбцы
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.2f}', ha='center', va='bottom')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def plot_top_products(self, save_path: str = None):
        """
        Построить график топ товаров.

        Parameters
        ----------
        save_path : str, optional
            Путь для сохранения графика, по умолчанию None
        """
        top_products = self.get_top_products_by_sales(8)

        if not top_products:
            print("Нет данных для построения графика")
            return

        names = [product['product'].name for product in top_products]
        quantities = [product['quantity_sold'] for product in top_products]
        revenues = [product['revenue'] for product in top_products]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # График количества продаж
        bars1 = ax1.bar(names, quantities, color='lightcoral', alpha=0.7)
        ax1.set_title('Топ товаров по количеству продаж')
        ax1.set_xlabel('Товары')
        ax1.set_ylabel('Количество продаж')
        ax1.tick_params(axis='x', rotation=45)

        # Добавление значений на столбцы
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}', ha='center', va='bottom')

        # График выручки
        bars2 = ax2.bar(names, revenues, color='gold', alpha=0.7)
        ax2.set_title('Топ товаров по выручке')
        ax2.set_xlabel('Товары')
        ax2.set_ylabel('Выручка (руб)')
        ax2.tick_params(axis='x', rotation=45)

        # Добавление значений на столбцы
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.2f}', ha='center', va='bottom')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def create_clients_network(self, save_path: str = None):
        """
        Создать граф связей клиентов по общим товарам.

        Parameters
        ----------
        save_path : str, optional
            Путь для сохранения графа, по умолчанию None
        """
        try:
            G = nx.Graph()

            # Добавляем клиентов как узлы
            for client in self.clients:
                G.add_node(client.client_id, label=client.name, orders=len(client.orders))

            # Создаем связи между клиентами, которые покупали одинаковые товары
            client_products = {}
            for client in self.clients:
                products_bought = set()
                for order in client.orders:
                    for item in order.items:
                        products_bought.add(item.product.product_id)
                client_products[client.client_id] = products_bought

            # Добавляем ребра между клиентами с общими товарами
            client_ids = list(client_products.keys())
            for i in range(len(client_ids)):
                for j in range(i + 1, len(client_ids)):
                    common_products = client_products[client_ids[i]] & client_products[client_ids[j]]
                    if common_products:
                        weight = len(common_products)
                        G.add_edge(client_ids[i], client_ids[j], weight=weight)

            # Визуализация графа
            plt.figure(figsize=(12, 8))

            pos = nx.spring_layout(G, k=1, iterations=50)

            # Размер узлов зависит от количества заказов
            node_sizes = [G.nodes[node].get('orders', 1) * 100 for node in G.nodes()]

            # Толщина ребер зависит от веса
            edge_widths = [G.edges[edge].get('weight', 1) for edge in G.edges()]

            nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                   node_color='lightblue', alpha=0.7)
            nx.draw_networkx_edges(G, pos, width=edge_widths,
                                   alpha=0.5, edge_color='gray')
            nx.draw_networkx_labels(G, pos,
                                    {node: G.nodes[node].get('label', '') for node in G.nodes()},
                                    font_size=8)

            plt.title('Граф связей клиентов по общим товарам')
            plt.axis('off')

            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()

        except ImportError:
            print("Для построения графа необходимо установить networkx: pip install networkx")
        except Exception as e:
            print(f"Ошибка при построении графа: {e}")

    def generate_sales_report(self) -> Dict[str, Any]:
        """
        Сгенерировать полный отчет о продажах.

        Returns
        -------
        Dict[str, Any]
            Словарь с данными отчета
        """
        total_orders = len(self.orders)
        total_revenue = sum(order.total_amount for order in self.orders)
        total_clients = len(self.clients)
        total_products = len(self.products)

        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        avg_orders_per_client = total_orders / total_clients if total_clients > 0 else 0

        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_clients': total_clients,
            'total_products': total_products,
            'avg_order_value': avg_order_value,
            'avg_orders_per_client': avg_orders_per_client,
            'top_clients': self.get_top_clients_by_orders(5),
            'top_products': self.get_top_products_by_sales(5)
        }