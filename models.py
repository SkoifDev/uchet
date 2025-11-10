"""
Модуль с классами данных для системы учёта заказов интернет-магазина.
"""

import re
from datetime import datetime
from typing import List, Optional


class Person:
    """Базовый класс для представления человека."""

    def __init__(self, name: str, email: str, phone: str):
        """
        Инициализация объекта Person.

        Parameters
        ----------
        name : str
            Имя человека
        email : str
            Email адрес
        phone : str
            Номер телефона
        """
        self._name = name
        self._email = email
        self._phone = phone

    @property
    def name(self) -> str:
        """Получить имя."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Установить имя."""
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._name = value

    @property
    def email(self) -> str:
        """Получить email."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Установить email с проверкой формата."""
        if not self._validate_email(value):
            raise ValueError("Неверный формат email")
        self._email = value

    @property
    def phone(self) -> str:
        """Получить номер телефона."""
        return self._phone

    @phone.setter
    def phone(self, value: str):
        """Установить номер телефона с проверкой формата."""
        if not self._validate_phone(value):
            raise ValueError("Неверный формат номера телефона")
        self._phone = value

    def _validate_email(self, email: str) -> bool:
        """
        Проверить валидность email с помощью регулярного выражения.

        Parameters
        ----------
        email : str
            Email для проверки

        Returns
        -------
        bool
            True если email валиден, иначе False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _validate_phone(self, phone: str) -> bool:
        """
        Проверить валидность номера телефона с помощью регулярного выражения.

        Parameters
        ----------
        phone : str
            Номер телефона для проверки

        Returns
        -------
        bool
            True если номер валиден, иначе False
        """
        # Поддержка форматов: +7-XXX-XXX-XX-XX, 8-XXX-XXX-XX-XX, etc.
        pattern = r'^(\+7|8)[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}$'
        return re.match(pattern, phone) is not None

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return f"{self.name} ({self.email}, {self.phone})"

    def to_dict(self) -> dict:
        """
        Преобразовать объект в словарь.

        Returns
        -------
        dict
            Словарь с данными объекта
        """
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }


class Client(Person):
    """Класс для представления клиента интернет-магазина."""

    def __init__(self, name: str, email: str, phone: str, address: str = ""):
        """
        Инициализация объекта Client.

        Parameters
        ----------
        name : str
            Имя клиента
        email : str
            Email адрес
        phone : str
            Номер телефона
        address : str, optional
            Адрес клиента, по умолчанию ""
        """
        super().__init__(name, email, phone)
        self._address = address
        self._orders = []
        self._client_id = id(self)

    @property
    def address(self) -> str:
        """Получить адрес."""
        return self._address

    @address.setter
    def address(self, value: str):
        """Установить адрес."""
        self._address = value

    @property
    def client_id(self) -> int:
        """Получить ID клиента."""
        return self._client_id

    @property
    def orders(self) -> List['Order']:
        """Получить список заказов клиента."""
        return self._orders.copy()

    def add_order(self, order: 'Order'):
        """
        Добавить заказ клиенту.

        Parameters
        ----------
        order : Order
            Заказ для добавления
        """
        if order not in self._orders:
            self._orders.append(order)

    def get_total_spent(self) -> float:
        """
        Рассчитать общую сумму всех заказов клиента.

        Returns
        -------
        float
            Общая сумма потраченных средств
        """
        return sum(order.total_amount for order in self._orders)

    def to_dict(self) -> dict:
        """
        Преобразовать объект в словарь.

        Returns
        -------
        dict
            Словарь с данными клиента
        """
        data = super().to_dict()
        data.update({
            'client_id': self.client_id,
            'address': self.address,
            'total_orders': len(self.orders),
            'total_spent': self.get_total_spent()
        })
        return data

    def __str__(self) -> str:
        """Строковое представление клиента."""
        return f"Клиент: {self.name} (Заказов: {len(self.orders)})"


class Product:
    """Класс для представления товара."""

    def __init__(self, name: str, price: float, category: str = "", description: str = ""):
        """
        Инициализация объекта Product.

        Parameters
        ----------
        name : str
            Название товара
        price : float
            Цена товара
        category : str, optional
            Категория товара, по умолчанию ""
        description : str, optional
            Описание товара, по умолчанию ""
        """
        self._name = name
        self._price = price
        self._category = category
        self._description = description
        self._product_id = id(self)

    @property
    def name(self) -> str:
        """Получить название товара."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Установить название товара."""
        if not value.strip():
            raise ValueError("Название товара не может быть пустым")
        self._name = value

    @property
    def price(self) -> float:
        """Получить цену товара."""
        return self._price

    @price.setter
    def price(self, value: float):
        """Установить цену товара."""
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._price = value

    @property
    def category(self) -> str:
        """Получить категорию товара."""
        return self._category

    @category.setter
    def category(self, value: str):
        """Установить категорию товара."""
        self._category = value

    @property
    def description(self) -> str:
        """Получить описание товара."""
        return self._description

    @description.setter
    def description(self, value: str):
        """Установить описание товара."""
        self._description = value

    @property
    def product_id(self) -> int:
        """Получить ID товара."""
        return self._product_id

    def to_dict(self) -> dict:
        """
        Преобразовать объект в словарь.

        Returns
        -------
        dict
            Словарь с данными товара
        """
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'description': self.description
        }

    def __str__(self) -> str:
        """Строковое представление товара."""
        return f"{self.name} - {self.price} руб."


class OrderItem:
    """Класс для представления позиции в заказе."""

    def __init__(self, product: Product, quantity: int = 1):
        """
        Инициализация объекта OrderItem.

        Parameters
        ----------
        product : Product
            Товар
        quantity : int, optional
            Количество товара, по умолчанию 1
        """
        self._product = product
        self._quantity = quantity

    @property
    def product(self) -> Product:
        """Получить товар."""
        return self._product

    @property
    def quantity(self) -> int:
        """Получить количество."""
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        """Установить количество."""
        if value < 1:
            raise ValueError("Количество не может быть меньше 1")
        self._quantity = value

    @property
    def total_price(self) -> float:
        """Рассчитать общую стоимость позиции."""
        return self.product.price * self.quantity

    def to_dict(self) -> dict:
        """
        Преобразовать объект в словарь.

        Returns
        -------
        dict
            Словарь с данными позиции заказа
        """
        product_data = self.product.to_dict()
        return {
            'product': product_data,
            'quantity': self.quantity,
            'total_price': self.total_price
        }

    def __str__(self) -> str:
        """Строковое представление позиции заказа."""
        return f"{self.product.name} x {self.quantity} = {self.total_price} руб."


class Order:
    """Класс для представления заказа."""

    def __init__(self, client: Client, order_date: Optional[datetime] = None):
        """
        Инициализация объекта Order.

        Parameters
        ----------
        client : Client
            Клиент, сделавший заказ
        order_date : datetime, optional
            Дата заказа, по умолчанию текущая дата
        """
        self._client = client
        self._order_date = order_date or datetime.now()
        self._items = []
        self._order_id = id(self)
        self._status = "Новый"

        # Добавляем заказ клиенту
        client.add_order(self)

    @property
    def order_id(self) -> int:
        """Получить ID заказа."""
        return self._order_id

    @property
    def client(self) -> Client:
        """Получить клиента."""
        return self._client

    @property
    def order_date(self) -> datetime:
        """Получить дату заказа."""
        return self._order_date

    @property
    def status(self) -> str:
        """Получить статус заказа."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Установить статус заказа."""
        self._status = value

    @property
    def items(self) -> List[OrderItem]:
        """Получить список позиций заказа."""
        return self._items.copy()

    @property
    def total_amount(self) -> float:
        """Рассчитать общую сумму заказа."""
        return sum(item.total_price for item in self._items)

    def add_item(self, product: Product, quantity: int = 1):
        """
        Добавить товар в заказ.

        Parameters
        ----------
        product : Product
            Товар для добавления
        quantity : int, optional
            Количество товара, по умолчанию 1
        """
        # Проверяем, есть ли уже такой товар в заказе
        for item in self._items:
            if item.product.product_id == product.product_id:
                item.quantity += quantity
                return

        # Если товара нет, добавляем новую позицию
        self._items.append(OrderItem(product, quantity))

    def remove_item(self, product: Product):
        """
        Удалить товар из заказа.

        Parameters
        ----------
        product : Product
            Товар для удаления
        """
        self._items = [item for item in self._items if item.product.product_id != product.product_id]

    def to_dict(self) -> dict:
        """
        Преобразовать объект в словарь.

        Returns
        -------
        dict
            Словарь с данными заказа
        """
        return {
            'order_id': self.order_id,
            'client': self.client.to_dict(),
            'order_date': self.order_date.isoformat(),
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'total_amount': self.total_amount
        }

    def __str__(self) -> str:
        """Строковое представление заказа."""
        return f"Заказ #{self.order_id} от {self.order_date.strftime('%d.%m.%Y')} - {self.total_amount} руб."