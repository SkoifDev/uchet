"""
Скрипт для автоматической генерации документации Sphinx.
"""

import os
import subprocess
import sys
import shutil


def generate_documentation():
    """
    Генерирует документацию Sphinx для проекта.

    Returns
    -------
    bool
        True если успешно, иначе False
    """
    try:
        # Путь к директории docs
        docs_dir = os.path.join(os.path.dirname(__file__), 'docs')

        # Проверяем существование директории docs
        if not os.path.exists(docs_dir):
            print("Создание директории docs...")
            os.makedirs(docs_dir)

        # Генерируем документацию
        print("Генерация документации Sphinx...")

        # Команды для генерации документации
        commands = [
            # Очистка предыдущей документации
            f'sphinx-build -M clean "{docs_dir}" "{docs_dir}/_build"',
            # Генерация HTML документации
            f'sphinx-build -b html "{docs_dir}" "{docs_dir}/_build/html"'
        ]

        for command in commands:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Ошибка при выполнении команды: {command}")
                print(f"Stderr: {result.stderr}")
                return False

        print("✅ Документация успешно сгенерирована!")
        print(f"📁 Файлы документации находятся в: {docs_dir}/_build/html")
        print("📖 Откройте index.html в браузере для просмотра документации")

        return True

    except Exception as e:
        print(f"❌ Ошибка при генерации документации: {e}")
        return False


def setup_sphinx():
    """
    Настраивает Sphinx для проекта.

    Returns
    -------
    bool
        True если успешно, иначе False
    """
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), 'docs')

        # Создаем директорию docs если её нет
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)

        # Запускаем sphinx-quickstart
        print("Запуск sphinx-quickstart...")
        command = f'sphinx-quickstart "{docs_dir}" --quiet --project="Система учёта заказов" --author="Python Developer" --release="1.0" --language="ru"'

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("Ошибка при настройке Sphinx")
            return False

        print("✅ Sphinx успешно настроен!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при настройке Sphinx: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Генератор документации для системы учёта заказов")
    print("=" * 50)

    # Проверяем, установлен ли Sphinx
    try:
        import sphinx

        print("✅ Sphinx установлен")
    except ImportError:
        print("❌ Sphinx не установлен. Установите его:")
        print("pip install sphinx sphinx-rtd-theme numpydoc")
        sys.exit(1)

    # Настраиваем Sphinx если нужно
    if not os.path.exists("docs/conf.py"):
        print("📝 Настройка Sphinx...")
        if setup_sphinx():
            print("✅ Настройка завершена")
        else:
            print("❌ Ошибка настройки")
            sys.exit(1)

    # Генерируем документацию
    if generate_documentation():
        print("\n🎉 Документация готова!")
    else:
        print("\n💥 Ошибка генерации документации")
        sys.exit(1)