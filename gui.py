"""
Модуль графического интерфейса системы учёта заказов.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional
from models import Client, Product, Order
from db import Database
from analysis import DataAnalyzer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import csv


class OnlineStoreApp:
    """Главный класс графического интерфейса приложения."""

    def __init__(self, root):
        """
        Инициализация главного окна приложения.

        Parameters
        ----------
        root : tk.Tk
            Корневое окно Tkinter
        """
        self.root = root
        self.root.title("Система учёта заказов интернет-магазина")
        self.root.geometry("1200x700")

        # Инициализация базы данных
        self.db = Database()

        # Загрузка данных
        self.clients = self.db.load_clients()
        self.products = self.db.load_products()
        self.orders = self.db.load_orders()

        # Создание интерфейса
        self._create_widgets()
        self._refresh_data()

    def _create_widgets(self):
        """Создание виджетов интерфейса."""
        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка клиентов
        self.clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_frame, text="Клиенты")
        self._create_clients_tab()

        # Вкладка товаров
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Товары")
        self._create_products_tab()

        # Вкладка заказов
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self._create_orders_tab()

        # Вкладка анализа
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Аналитика")
        self._create_analysis_tab()

        # Вкладка импорта/экспорта
        self.import_export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_export_frame, text="Импорт/Экспорт")
        self._create_import_export_tab()

    def _create_clients_tab(self):
        """Создание вкладки управления клиентами."""
        # Фрейм для формы добавления клиента
        form_frame = ttk.LabelFrame(self.clients_frame, text="Добавить клиента")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Поля формы
        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_name_entry = ttk.Entry(form_frame, width=30)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_email_entry = ttk.Entry(form_frame, width=30)
        self.client_email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_phone_entry = ttk.Entry(form_frame, width=30)
        self.client_phone_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Адрес:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_address_entry = ttk.Entry(form_frame, width=30)
        self.client_address_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить клиента",
                   command=self._add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить форму",
                   command=self._clear_client_form).pack(side=tk.LEFT, padx=5)

        # Таблица клиентов
        table_frame = ttk.LabelFrame(self.clients_frame, text="Список клиентов")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание Treeview
        columns = ("ID", "Имя", "Email", "Телефон", "Адрес", "Заказов", "Потрачено")
        self.clients_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Настройка колонок
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=100)

        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Кнопки управления
        control_frame = ttk.Frame(self.clients_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Обновить",
                   command=self._refresh_clients).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить выделенного",
                   command=self._delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Поиск по имени",
                   command=self._search_clients).pack(side=tk.LEFT, padx=5)

        # Поле поиска
        self.client_search_entry = ttk.Entry(control_frame, width=30)
        self.client_search_entry.pack(side=tk.LEFT, padx=5)
        self.client_search_entry.bind('<Return>', lambda e: self._search_clients())

    def _create_products_tab(self):
        """Создание вкладки управления товарами."""
        # Фрейм для формы добавления товара
        form_frame = ttk.LabelFrame(self.products_frame, text="Добавить товар")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Поля формы
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.product_name_entry = ttk.Entry(form_frame, width=30)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Цена:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.product_price_entry = ttk.Entry(form_frame, width=30)
        self.product_price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Категория:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.product_category_entry = ttk.Entry(form_frame, width=30)
        self.product_category_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Описание:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.product_description_entry = ttk.Entry(form_frame, width=30)
        self.product_description_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить товар",
                   command=self._add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить форму",
                   command=self._clear_product_form).pack(side=tk.LEFT, padx=5)

        # Таблица товаров
        table_frame = ttk.LabelFrame(self.products_frame, text="Список товаров")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание Treeview
        columns = ("ID", "Название", "Цена", "Категория", "Описание")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Настройка колонок
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)

        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Кнопки управления
        control_frame = ttk.Frame(self.products_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Обновить",
                   command=self._refresh_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить выделенный",
                   command=self._delete_product).pack(side=tk.LEFT, padx=5)

    def _create_orders_tab(self):
        """Создание вкладки управления заказами."""
        # Фрейм для формы создания заказа
        form_frame = ttk.LabelFrame(self.orders_frame, text="Создать заказ")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Выбор клиента
        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(form_frame, textvariable=self.client_var, width=27)
        self.client_combo.grid(row=0, column=1, padx=5, pady=5)

        # Выбор товара
        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(form_frame, textvariable=self.product_var, width=27)
        self.product_combo.grid(row=1, column=1, padx=5, pady=5)

        # Количество
        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.quantity_entry = ttk.Entry(form_frame, width=30)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить товар в заказ",
                   command=self._add_product_to_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Создать заказ",
                   command=self._create_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить заказ",
                   command=self._clear_current_order).pack(side=tk.LEFT, padx=5)

        # Текущий заказ
        self.current_order_frame = ttk.LabelFrame(self.orders_frame, text="Текущий заказ")
        self.current_order_frame.pack(fill=tk.X, padx=5, pady=5)

        self.current_order_text = tk.Text(self.current_order_frame, height=6, width=80)
        self.current_order_text.pack(padx=5, pady=5)

        # Таблица заказов
        table_frame = ttk.LabelFrame(self.orders_frame, text="История заказов")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание Treeview
        columns = ("ID", "Клиент", "Дата", "Статус", "Сумма", "Товары")
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Настройка колонок
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100)

        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Текущий заказ (в памяти)
        self.current_order = None
        self.current_order_items = []

    def _create_analysis_tab(self):
        """Создание вкладки анализа данных."""
        # Фрейм для кнопок анализа
        button_frame = ttk.Frame(self.analysis_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Топ клиентов",
                   command=self._show_top_clients).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Топ товаров",
                   command=self._show_top_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Динамика заказов",
                   command=self._show_orders_dynamics).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Граф клиентов",
                   command=self._show_clients_network).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Общий отчет",
                   command=self._show_sales_report).pack(side=tk.LEFT, padx=5)

        # Фрейм для отображения графиков
        self.analysis_display_frame = ttk.Frame(self.analysis_frame)
        self.analysis_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_import_export_tab(self):
        """Создание вкладки импорта/экспорта."""
        # Экспорт
        export_frame = ttk.LabelFrame(self.import_export_frame, text="Экспорт данных")
        export_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(export_frame, text="Тип данных:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.export_type = tk.StringVar(value="clients")
        export_combo = ttk.Combobox(export_frame, textvariable=self.export_type,
                                    values=["clients", "products", "orders"], width=15)
        export_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(export_frame, text="Формат:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.export_format = tk.StringVar(value="CSV")
        format_combo = ttk.Combobox(export_frame, textvariable=self.export_format,
                                    values=["CSV", "JSON"], width=10)
        format_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(export_frame, text="Экспортировать",
                   command=self._export_data).grid(row=0, column=4, padx=5, pady=5)

        # Импорт
        import_frame = ttk.LabelFrame(self.import_export_frame, text="Импорт данных")
        import_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(import_frame, text="Тип данных:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.import_type = tk.StringVar(value="clients")
        import_combo = ttk.Combobox(import_frame, textvariable=self.import_type,
                                    values=["clients", "products"], width=15)
        import_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(import_frame, text="Формат:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.import_format = tk.StringVar(value="CSV")
        import_format_combo = ttk.Combobox(import_frame, textvariable=self.import_format,
                                           values=["CSV", "JSON"], width=10)
        import_format_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(import_frame, text="Импортировать",
                   command=self._import_data).grid(row=0, column=4, padx=5, pady=5)

    # Методы для работы с клиентами
    def _add_client(self):
        """Добавить нового клиента."""
        try:
            name = self.client_name_entry.get().strip()
            email = self.client_email_entry.get().strip()
            phone = self.client_phone_entry.get().strip()
            address = self.client_address_entry.get().strip()

            if not name or not email or not phone:
                messagebox.showerror("Ошибка", "Заполните обязательные поля: Имя, Email, Телефон")
                return

            client = Client(name, email, phone, address)

            if self.db.save_client(client):
                self.clients.append(client)
                self._refresh_clients()
                self._clear_client_form()
                messagebox.showinfo("Успех", "Клиент успешно добавлен")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить клиента")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _clear_client_form(self):
        """Очистить форму добавления клиента."""
        self.client_name_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)
        self.client_address_entry.delete(0, tk.END)

    def _refresh_clients(self):
        """Обновить список клиентов."""
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        for client in self.clients:
            self.clients_tree.insert("", tk.END, values=(
                client.client_id,
                client.name,
                client.email,
                client.phone,
                client.address,
                len(client.orders),
                f"{client.get_total_spent():.2f}"
            ))

    def _delete_client(self):
        """Удалить выделенного клиента."""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return

        client_id = int(self.clients_tree.item(selected[0])['values'][0])

        if messagebox.askyesno("Подтверждение", "Удалить выбранного клиента?"):
            # Здесь должна быть логика удаления из БД
            self.clients = [c for c in self.clients if c.client_id != client_id]
            self._refresh_clients()

    def _search_clients(self):
        """Поиск клиентов по имени."""
        search_term = self.client_search_entry.get().strip().lower()
        if not search_term:
            self._refresh_clients()
            return

        filtered_clients = [c for c in self.clients if search_term in c.name.lower()]

        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        for client in filtered_clients:
            self.clients_tree.insert("", tk.END, values=(
                client.client_id,
                client.name,
                client.email,
                client.phone,
                client.address,
                len(client.orders),
                f"{client.get_total_spent():.2f}"
            ))

    # Методы для работы с товарами
    def _add_product(self):
        """Добавить новый товар."""
        try:
            name = self.product_name_entry.get().strip()
            price_str = self.product_price_entry.get().strip()
            category = self.product_category_entry.get().strip()
            description = self.product_description_entry.get().strip()

            if not name or not price_str:
                messagebox.showerror("Ошибка", "Заполните обязательные поля: Название, Цена")
                return

            price = float(price_str)
            product = Product(name, price, category, description)

            if self.db.save_product(product):
                self.products.append(product)
                self._refresh_products()
                self._clear_product_form()
                messagebox.showinfo("Успех", "Товар успешно добавлен")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить товар")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверная цена: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _clear_product_form(self):
        """Очистить форму добавления товара."""
        self.product_name_entry.delete(0, tk.END)
        self.product_price_entry.delete(0, tk.END)
        self.product_category_entry.delete(0, tk.END)
        self.product_description_entry.delete(0, tk.END)

    def _refresh_products(self):
        """Обновить список товаров."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        for product in self.products:
            self.products_tree.insert("", tk.END, values=(
                product.product_id,
                product.name,
                f"{product.price:.2f}",
                product.category,
                product.description
            ))

    def _delete_product(self):
        """Удалить выделенный товар."""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return

        product_id = int(self.products_tree.item(selected[0])['values'][0])

        if messagebox.askyesno("Подтверждение", "Удалить выбранный товар?"):
            self.products = [p for p in self.products if p.product_id != product_id]
            self._refresh_products()

    # Методы для работы с заказами
    def _add_product_to_order(self):
        """Добавить товар в текущий заказ."""
        try:
            client_name = self.client_var.get()
            product_name = self.product_var.get()
            quantity_str = self.quantity_entry.get().strip()

            if not client_name:
                messagebox.showerror("Ошибка", "Выберите клиента")
                return

            if not product_name:
                messagebox.showerror("Ошибка", "Выберите товар")
                return

            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть положительным")
                return

            # Находим клиента и товар
            client = next((c for c in self.clients if c.name == client_name), None)
            product = next((p for p in self.products if p.name == product_name), None)

            if not client or not product:
                messagebox.showerror("Ошибка", "Клиент или товар не найден")
                return

            # Создаем заказ если его нет
            if not self.current_order:
                self.current_order = Order(client)

            # Добавляем товар
            self.current_order.add_item(product, quantity)
            self.current_order_items.append((product, quantity))

            # Обновляем отображение
            self._update_current_order_display()

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверное количество: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _create_order(self):
        """Создать заказ."""
        if not self.current_order or not self.current_order.items:
            messagebox.showerror("Ошибка", "Добавьте товары в заказ")
            return

        try:
            if self.db.save_order(self.current_order):
                self.orders.append(self.current_order)
                self._refresh_orders()
                self._clear_current_order()
                messagebox.showinfo("Успех", "Заказ успешно создан")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить заказ")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _clear_current_order(self):
        """Очистить текущий заказ."""
        self.current_order = None
        self.current_order_items = []
        self.current_order_text.delete(1.0, tk.END)
        self.client_var.set("")
        self.product_var.set("")
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")

    def _update_current_order_display(self):
        """Обновить отображение текущего заказа."""
        self.current_order_text.delete(1.0, tk.END)

        if self.current_order:
            self.current_order_text.insert(tk.END, f"Клиент: {self.current_order.client.name}\n")
            self.current_order_text.insert(tk.END,
                                           f"Дата: {self.current_order.order_date.strftime('%d.%m.%Y %H:%M')}\n\n")
            self.current_order_text.insert(tk.END, "Товары:\n")

            for item in self.current_order.items:
                self.current_order_text.insert(tk.END,
                                               f"- {item.product.name} x {item.quantity} = {item.total_price:.2f} руб.\n")

            self.current_order_text.insert(tk.END, f"\nИтого: {self.current_order.total_amount:.2f} руб.")

    def _refresh_orders(self):
        """Обновить список заказов."""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        for order in self.orders:
            products_info = ", ".join([f"{item.product.name} x {item.quantity}" for item in order.items[:3]])
            if len(order.items) > 3:
                products_info += "..."

            self.orders_tree.insert("", tk.END, values=(
                order.order_id,
                order.client.name,
                order.order_date.strftime('%d.%m.%Y'),
                order.status,
                f"{order.total_amount:.2f}",
                products_info
            ))

    # Методы для анализа данных
    def _show_top_clients(self):
        """Показать график топ клиентов."""
        self._clear_analysis_display()

        analyzer = DataAnalyzer(self.clients, self.products, self.orders)

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        top_clients = analyzer.get_top_clients_by_orders(8)
        names = [client['client'].name for client in top_clients]
        order_counts = [client['order_count'] for client in top_clients]

        bars = ax.bar(names, order_counts, color='skyblue', alpha=0.7)
        ax.set_title('Топ клиентов по количеству заказов')
        ax.set_xlabel('Клиенты')
        ax.set_ylabel('Количество заказов')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Добавление значений на столбцы
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(fig, self.analysis_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _show_top_products(self):
        """Показать график топ товаров."""
        self._clear_analysis_display()

        analyzer = DataAnalyzer(self.clients, self.products, self.orders)

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        top_products = analyzer.get_top_products_by_sales(8)
        names = [product['product'].name for product in top_products]
        revenues = [product['revenue'] for product in top_products]

        bars = ax.bar(names, revenues, color='lightgreen', alpha=0.7)
        ax.set_title('Топ товаров по выручке')
        ax.set_xlabel('Товары')
        ax.set_ylabel('Выручка (руб)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Добавление значений на столбцы
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.2f}', ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(fig, self.analysis_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _show_orders_dynamics(self):
        """Показать график динамики заказов."""
        self._clear_analysis_display()

        analyzer = DataAnalyzer(self.clients, self.products, self.orders)
        analyzer.plot_orders_dynamics()

    def _show_clients_network(self):
        """Показать граф связей клиентов."""
        self._clear_analysis_display()

        analyzer = DataAnalyzer(self.clients, self.products, self.orders)
        analyzer.create_clients_network()

    def _show_sales_report(self):
        """Показать общий отчет о продажах."""
        analyzer = DataAnalyzer(self.clients, self.products, self.orders)
        report = analyzer.generate_sales_report()

        report_text = f"""
ОБЩИЙ ОТЧЕТ О ПРОДАЖАХ

Общее количество заказов: {report['total_orders']}
Общая выручка: {report['total_revenue']:.2f} руб.
Количество клиентов: {report['total_clients']}
Количество товаров: {report['total_products']}
Средний чек: {report['avg_order_value']:.2f} руб.
Среднее количество заказов на клиента: {report['avg_orders_per_client']:.2f}

ТОП-5 КЛИЕНТОВ:
"""
        for i, client in enumerate(report['top_clients'], 1):
            report_text += f"{i}. {client['client'].name} - {client['order_count']} заказов, {client['total_spent']:.2f} руб.\n"

        report_text += "\nТОП-5 ТОВАРОВ:\n"
        for i, product in enumerate(report['top_products'], 1):
            report_text += f"{i}. {product['product'].name} - {product['quantity_sold']} шт., {product['revenue']:.2f} руб.\n"

        # Создаем текстовое окно для отчета
        report_window = tk.Toplevel(self.root)
        report_window.title("Отчет о продажах")
        report_window.geometry("600x400")

        text_widget = tk.Text(report_window, wrap=tk.WORD)
        text_widget.insert(tk.END, report_text)
        text_widget.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(report_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _clear_analysis_display(self):
        """Очистить область отображения анализа."""
        for widget in self.analysis_display_frame.winfo_children():
            widget.destroy()

    # Методы для импорта/экспорта
    def _export_data(self):
        """Экспортировать данные."""
        try:
            data_type = self.export_type.get()
            file_format = self.export_format.get().lower()

            filename = filedialog.asksaveasfilename(
                defaultextension=f".{file_format}",
                filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")]
            )

            if filename:
                if file_format == "csv":
                    success = self.db.export_to_csv(filename, data_type)
                else:  # json
                    success = self.db.export_to_json(filename, data_type)

                if success:
                    messagebox.showinfo("Успех", f"Данные успешно экспортированы в {filename}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось экспортировать данные")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _import_data(self):
        """Импортировать данные."""
        try:
            data_type = self.import_type.get()
            file_format = self.import_format.get().lower()

            filename = filedialog.askopenfilename(
                filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")]
            )

            if filename:
                if file_format == "csv":
                    success = self.db.import_from_csv(filename, data_type)
                else:  # json
                    success = self.db.import_from_json(filename, data_type)

                if success:
                    # Перезагружаем данные
                    self.clients = self.db.load_clients()
                    self.products = self.db.load_products()
                    self.orders = self.db.load_orders()
                    self._refresh_data()
                    messagebox.showinfo("Успех", f"Данные успешно импортированы из {filename}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось импортировать данные")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _refresh_data(self):
        """Обновить все данные в интерфейсе."""
        self._refresh_clients()
        self._refresh_products()
        self._refresh_orders()

        # Обновляем комбобоксы
        client_names = [client.name for client in self.clients]
        self.client_combo['values'] = client_names

        product_names = [product.name for product in self.products]
        self.product_combo['values'] = product_names