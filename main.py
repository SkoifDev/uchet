"""
Главный модуль для запуска приложения системы учёта заказов.
"""

import tkinter as tk
from gui import OnlineStoreApp
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """
    Главная функция для запуска приложения.

    Returns
    -------
    int
        Код возврата
    """
    try:
        # Создаем главное окно
        root = tk.Tk()

        # Создаем и запускаем приложение
        app = OnlineStoreApp(root)

        # Запускаем главный цикл
        root.mainloop()

        return 0

    except Exception as e:
        print(f"Произошла ошибка при запуске приложения: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)