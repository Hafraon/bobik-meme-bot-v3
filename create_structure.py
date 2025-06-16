#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для створення структури проекту Бобік 2.0
Запустіть цей файл у корені вашого проекту
"""

import os
import shutil
from pathlib import Path

def create_project_structure():
    """Створює повну структуру проекту"""
    
    print("🐕 Створюю структуру проекту Бобік 2.0...")
    
    # Структура папок
    folders = [
        "config",
        "database", 
        "handlers",
        "services",
        "utils",
        "api",
        "tests",
        "scripts",
        "docs",
        "docker",
        "deployment",
        "monitoring",
        "data",
        "logs",
        ".github/workflows",
        ".github/ISSUE_TEMPLATE",
        ".vscode"
    ]
    
    # Створюємо папки
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"📁 Створено папку: {folder}")
    
    # Створюємо __init__.py файли для Python пакетів
    python_packages = [
        "config",
        "database",
        "handlers", 
        "services",
        "utils",
        "api",
        "tests"
    ]
    
    for package in python_packages:
        init_file = Path(package) / "__init__.py"
        init_file.write_text("# -*- coding: utf-8 -*-\n")
        print(f"📄 Створено __init__.py в {package}")
    
    # Переміщуємо існуючі файли
    move_existing_files()
    
    # Створюємо основні файли
    create_main_files()
    
    print("\n✅ Структура проекту створена успішно!")
    print("🎯 Наступні кроки:")
    print("1. Розбийте bobik_bot.py на окремі модулі")
    print("2. Оновіть imports у коді")
    print("3. Протестуйте роботу бота")

def move_existing_files():
    """Переміщує існуючі файли у відповідні папки"""
    
    # Файли для переміщення
    file_moves = {
        # Документація
        "CONTRIBUTING.md": "docs/CONTRIBUTING.md",
        "SECURITY.md": "docs/SECURITY.md", 
        "QUICK_START.md": "docs/QUICK_START.md",
        "FILES_SUMMARY.md": "docs/FILES_SUMMARY.md",
        
        # Docker
        "Dockerfile": "docker/Dockerfile",
        "docker-compose.yml": "docker/docker-compose.yml", 
        ".dockerignore": "docker/.dockerignore",
        
        # Deployment
        "railway.json": "deployment/railway.json",
        "Procfile": "deployment/Procfile",
        
        # Моніторинг
        "monitoring prometheus.yml": "monitoring/prometheus.yml",
        "monitoring grafana-dashboard.json": "monitoring/grafana-dashboard.json"
    }
    
    for source, destination in file_moves.items():
        if os.path.exists(source):
            # Створюємо папку якщо не існує
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            print(f"📦 Переміщено: {source} → {destination}")

def create_main_files():
    """Створює основні файли проекту"""
    
    # main.py
    main_py_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Головний файл запуску Бобік 2.0 - AI Мем-Бот
"""

import asyncio
import logging
import sys
import os

# Додаємо поточну папку до Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Головна функція запуску бота"""
    
    try:
        # Поки що імпортуємо старий код
        from bobik_bot import main as old_main
        old_main()
    except ImportError:
        print("❌ Файл bobik_bot.py не знайдено!")
        print("📝 Створіть модульну структуру згідно документації")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(main_py_content)
    print("📄 Створено main.py")
    
    # config/settings.py
    settings_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Налаштування проекту Бобік 2.0
"""

import os
from typing import Optional

class Settings:
    """Клас налаштувань бота"""
    
    def __init__(self):
        # Основні налаштування
        self.BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@BobikFun")
        
        # AI налаштування
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Часові налаштування
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
        self.POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "11"))
        
        # Логування
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Валідація
        self._validate()
    
    def _validate(self):
        """Валідація обов'язкових налаштувань"""
        if not self.BOT_TOKEN:
            raise ValueError("⚠️ TELEGRAM_BOT_TOKEN потрібен для роботи бота")
        
        if not self.CHANNEL_ID:
            raise ValueError("⚠️ TELEGRAM_CHANNEL_ID потрібен для публікацій")
        
        print(f"✅ Налаштування завантажено для каналу: {self.CHANNEL_ID}")
'''
    
    with open("config/settings.py", "w", encoding="utf-8") as f:
        f.write(settings_content)
    print("📄 Створено config/settings.py")
    
    # config/localization.py
    localization_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Українська локалізація для Бобік 2.0
"""

# Тексти інтерфейсу українською
TEXTS = {
    'start_message': """🐕 **Привіт! Я Бобік 2.0!**

🚀 **Нові можливості:**
• 🤖 AI локалізація мемів
• 📡 Відмовостійкі API
• 🇺🇦 Оптимізація під Україну
• 📊 Розширена аналітика

📱 **Меню з'явилося внизу екрану!**
🔗 **Канал:** @BobikFun""",

    'menu_restored': "📱 **Постійне меню відновлено!**",
    
    'test_post_success': "✅ **Тестовий мем опубліковано!**",
    'test_post_error': "❌ **Помилка публікації**",
    
    'scheduler_started': "✅ **Автоматичний розклад запущено!**",
    'scheduler_stopped': "⏹️ **Автоматичний розклад зупинено**",
    
    'api_checking': "🔍 Перевіряю API...",
    'ai_active': "🤖 **AI активний**",
    'ai_disabled': "🤖 **AI вимкнений**"
}

def get_text(key: str) -> str:
    """Отримує локалізований текст"""
    return TEXTS.get(key, f"❌ Текст '{key}' не знайдено")
'''
    
    with open("config/localization.py", "w", encoding="utf-8") as f:
        f.write(localization_content)
    print("📄 Створено config/localization.py")

if __name__ == "__main__":
    create_project_structure()