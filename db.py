"""
Модуль для работы с базой данных SQLite системы учёта заказов.
"""

import sqlite3
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import Client, Product, Order, OrderItem


class Database:
    """Класс для работы с базой данных SQLite."""

    def __init__(self, db_name: str = "online_store.db"):
        """
        Инициализация подключения к базе данных.

        Parameters
        ----------
        db_name : str, optional
            Имя файла базы данных, по умолчанию "online_store.db"
        """
        self.db_name = db_name
        self._init_database()

    def _init_database(self):
        """Инициализировать таблицы базы данных."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Таблица клиентов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clients (
                        client_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT NOT NULL,
                        address TEXT
                    )
                ''')

                # Таблица товаров
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        product_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        category TEXT,
                        description TEXT
                    )
                ''')

                # Таблица заказов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY,
                        client_id INTEGER,
                        order_date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        total_amount REAL NOT NULL,
                        FOREIGN KEY (client_id) REFERENCES clients (client_id)
                    )
                ''')

                # Таблица позиций заказов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS order_items (
                        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER,
                        product_id INTEGER,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES orders (order_id),
                        FOREIGN KEY (product_id) REFERENCES products (product_id)
                    )
                ''')

                conn.commit()

        except sqlite3.Error as e:
            print(f"Ошибка инициализации базы данных: {e}")

    def save_client(self, client: Client) -> bool:
        """
        Сохранить клиента в базу данных.

        Parameters
        ----------
        client : Client
            Объект клиента для сохранения

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO clients (client_id, name, email, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (client.client_id, client.name, client.email, client.phone, client.address))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка сохранения клиента: {e}")
            return False

    def save_product(self, product: Product) -> bool:
        """
        Сохранить товар в базу данных.

        Parameters
        ----------
        product : Product
            Объект товара для сохранения

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO products (product_id, name, price, category, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product.product_id, product.name, product.price, product.category, product.description))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка сохранения товара: {e}")
            return False

    def save_order(self, order: Order) -> bool:
        """
        Сохранить заказ в базу данных.

        Parameters
        ----------
        order : Order
            Объект заказа для сохранения

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Сохраняем заказ
                cursor.execute('''
                    INSERT OR REPLACE INTO orders (order_id, client_id, order_date, status, total_amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order.order_id, order.client.client_id, order.order_date.isoformat(),
                      order.status, order.total_amount))

                # Удаляем старые позиции заказа
                cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order.order_id,))

                # Сохраняем новые позиции заказа
                for item in order.items:
                    cursor.execute('''
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                    ''', (order.order_id, item.product.product_id, item.quantity, item.product.price))

                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка сохранения заказа: {e}")
            return False

    def load_clients(self) -> List[Client]:
        """
        Загрузить всех клиентов из базы данных.

        Returns
        -------
        List[Client]
            Список объектов клиентов
        """
        clients = []
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM clients')
                rows = cursor.fetchall()

                for row in rows:
                    client_id, name, email, phone, address = row
                    client = Client(name, email, phone, address)
                    client._client_id = client_id
                    clients.append(client)

        except sqlite3.Error as e:
            print(f"Ошибка загрузки клиентов: {e}")

        return clients

    def load_products(self) -> List[Product]:
        """
        Загрузить все товары из базы данных.

        Returns
        -------
        List[Product]
            Список объектов товаров
        """
        products = []
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products')
                rows = cursor.fetchall()

                for row in rows:
                    product_id, name, price, category, description = row
                    product = Product(name, price, category, description)
                    product._product_id = product_id
                    products.append(product)

        except sqlite3.Error as e:
            print(f"Ошибка загрузки товаров: {e}")

        return products

    def load_orders(self) -> List[Order]:
        """
        Загрузить все заказы из базы данных.

        Returns
        -------
        List[Order]
            Список объектов заказов
        """
        orders = []
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Загружаем клиентов и товары для связей
                clients = {client.client_id: client for client in self.load_clients()}
                products = {product.product_id: product for product in self.load_products()}

                # Загружаем заказы
                cursor.execute('SELECT * FROM orders')
                order_rows = cursor.fetchall()

                for order_row in order_rows:
                    order_id, client_id, order_date_str, status, total_amount = order_row

                    if client_id not in clients:
                        continue

                    client = clients[client_id]
                    order_date = datetime.fromisoformat(order_date_str)
                    order = Order(client, order_date)
                    order._order_id = order_id
                    order.status = status

                    # Загружаем позиции заказа
                    cursor.execute('''
                        SELECT product_id, quantity FROM order_items 
                        WHERE order_id = ?
                    ''', (order_id,))

                    item_rows = cursor.fetchall()

                    for product_id, quantity in item_rows:
                        if product_id in products:
                            product = products[product_id]
                            order.add_item(product, quantity)

                    orders.append(order)

        except sqlite3.Error as e:
            print(f"Ошибка загрузки заказов: {e}")

        return orders

    def export_to_csv(self, filename: str, data_type: str) -> bool:
        """
        Экспортировать данные в CSV файл.

        Parameters
        ----------
        filename : str
            Имя файла для экспорта
        data_type : str
            Тип данных ('clients', 'products', 'orders')

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            if data_type == 'clients':
                data = self.load_clients()
                fieldnames = ['client_id', 'name', 'email', 'phone', 'address', 'total_orders', 'total_spent']
            elif data_type == 'products':
                data = self.load_products()
                fieldnames = ['product_id', 'name', 'price', 'category', 'description']
            elif data_type == 'orders':
                data = self.load_orders()
                fieldnames = ['order_id', 'client_id', 'order_date', 'status', 'total_amount']
            else:
                raise ValueError("Неверный тип данных")

            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for item in data:
                    writer.writerow(item.to_dict())

            return True

        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False

    def import_from_csv(self, filename: str, data_type: str) -> bool:
        """
        Импортировать данные из CSV файла.

        Parameters
        ----------
        filename : str
            Имя файла для импорта
        data_type : str
            Тип данных ('clients', 'products', 'orders')

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    if data_type == 'clients':
                        client = Client(
                            name=row['name'],
                            email=row['email'],
                            phone=row['phone'],
                            address=row.get('address', '')
                        )
                        self.save_client(client)

                    elif data_type == 'products':
                        product = Product(
                            name=row['name'],
                            price=float(row['price']),
                            category=row.get('category', ''),
                            description=row.get('description', '')
                        )
                        self.save_product(product)

                    elif data_type == 'orders':
                        # Для заказов нужна более сложная логика
                        pass

            return True

        except Exception as e:
            print(f"Ошибка импорта из CSV: {e}")
            return False

    def export_to_json(self, filename: str, data_type: str) -> bool:
        """
        Экспортировать данные в JSON файл.

        Parameters
        ----------
        filename : str
            Имя файла для экспорта
        data_type : str
            Тип данных ('clients', 'products', 'orders')

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            if data_type == 'clients':
                data = [client.to_dict() for client in self.load_clients()]
            elif data_type == 'products':
                data = [product.to_dict() for product in self.load_products()]
            elif data_type == 'orders':
                data = [order.to_dict() for order in self.load_orders()]
            else:
                raise ValueError("Неверный тип данных")

            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
            return False

    def import_from_json(self, filename: str, data_type: str) -> bool:
        """
        Импортировать данные из JSON файла.

        Parameters
        ----------
        filename : str
            Имя файла для импорта
        data_type : str
            Тип данных ('clients', 'products', 'orders')

        Returns
        -------
        bool
            True если успешно, иначе False
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for item_data in data:
                    if data_type == 'clients':
                        client = Client(
                            name=item_data['name'],
                            email=item_data['email'],
                            phone=item_data['phone'],
                            address=item_data.get('address', '')
                        )
                        self.save_client(client)

                    elif data_type == 'products':
                        product = Product(
                            name=item_data['name'],
                            price=item_data['price'],
                            category=item_data.get('category', ''),
                            description=item_data.get('description', '')
                        )
                        self.save_product(product)

            return True

        except Exception as e:
            print(f"Ошибка импорта из JSON: {e}")
            return False