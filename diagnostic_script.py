#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ДІАГНОСТИЧНИЙ СКРИПТ ДЛЯ УКРАНОМОВНОГО БОТА 🧠😂🔥

Автоматична діагностика та виправлення проблем
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import traceback

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def print_header():
    """Заголовок діагностики"""
    print("🧠😂🔥" * 20)
    print("\n🔧 ДІАГНОСТИКА ПРОФЕСІЙНОГО УКРАЇНОМОВНОГО БОТА")
    print("📊 Автоматична перевірка та виправлення проблем")
    print("🧠😂🔥" * 20)
    print()

def check_environment():
    """Перевірка середовища"""
    print("📍 ПЕРЕВІРКА СЕРЕДОВИЩА:")
    
    issues = []
    
    # Python версія
    python_version = sys.version_info
    if python_version >= (3, 9):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (потрібен >= 3.9)")
        issues.append("Python версія застаріла")
    
    # Змінні середовища
    required_env = {
        'BOT_TOKEN': 'Токен Telegram бота',
        'ADMIN_ID': 'ID адміністратора'
    }
    
    for env_var, description in required_env.items():
        value = os.getenv(env_var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {env_var}: {masked}")
        else:
            print(f"❌ {env_var}: не встановлено ({description})")
            issues.append(f"Відсутня змінна {env_var}")
    
    # Railway середовище
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Railway середовище виявлено")
    else:
        print("📍 Локальне середовище")
    
    return issues

def check_structure():
    """Перевірка структури проекту відповідно до вашої організації"""
    print("\n📁 ПЕРЕВІРКА СТРУКТУРИ ПРОЕКТУ:")
    
    critical_files = {
        # Корінь проекту
        'main.py': 'Головний файл запуску (корінь)',
        'requirements.txt': 'Основні залежності',
        'Procfile': 'Railway процеси (корінь)',
        
        # App структура
        'app/main.py': 'Основний код бота',
        'app/__init__.py': 'App пакет',
        'app/config/settings.py': 'Налаштування',
        'app/config/__init__.py': 'Config пакет',
        'app/database/models.py': 'Моделі БД',
        'app/database/database.py': 'Сервіси БД',
        'app/database/__init__.py': 'Database пакет',
        'app/handlers/__init__.py': 'Хендлери пакет',
        'app/handlers/basic_commands.py': 'Базові команди',
        'app/services/__init__.py': 'Services пакет',
        'app/utils/__init__.py': 'Utils пакет',
        
        # Deployment структура
        'deployment/railway.json': 'Railway конфігурація',
        'deployment/Procfile': 'Railway процеси (backup)',
        'deployment/requirements.txt': 'Deployment залежності'
    }
    
    optional_files = {
        '.env': 'Локальні змінні',
        'alembic.ini': 'Міграції БД',
        'app/services/scheduler.py': 'Планувальник',
        'app/keyboards/__init__.py': 'Клавіатури',
        'docker/docker-compose.yml': 'Docker композиція',
        'docs/README.md': 'Документація'
    }
    
    issues = []
    
    print("📋 КРИТИЧНІ ФАЙЛИ:")
    for file_path, description in critical_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path} ({description})")
        else:
            print(f"❌ {file_path} ({description}) - КРИТИЧНИЙ")
            issues.append(f"Відсутній критичний файл: {file_path}")
    
    print("\n📋 ОПЦІОНАЛЬНІ ФАЙЛИ:")
    for file_path, description in optional_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path} ({description})")
        else:
            print(f"⚠️ {file_path} ({description}) - опціональний")
    
    return issues

def check_dependencies():
    """Перевірка залежностей"""
    print("\n📦 ПЕРЕВІРКА ЗАЛЕЖНОСТЕЙ:")
    
    required_deps = [
        ('aiogram', 'Telegram Bot API'),
        ('sqlalchemy', 'ORM для БД'),
        ('asyncpg', 'PostgreSQL драйвер'),
        ('aiohttp', 'HTTP клієнт'),
    ]
    
    optional_deps = [
        ('apscheduler', 'Планувальник'),
        ('openai', 'OpenAI API'),
        ('redis', 'Кеш (опціонально)')
    ]
    
    issues = []
    
    for dep, description in required_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} ({description})")
        except ImportError:
            print(f"❌ {dep} ({description}) - КРИТИЧНИЙ")
            issues.append(f"Відсутня критична залежність: {dep}")
    
    for dep, description in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} ({description})")
        except ImportError:
            print(f"⚠️ {dep} ({description}) - опціональний")
    
    return issues

def check_imports():
    """Перевірка імпортів проекту з app/ структурою"""
    print("\n🔗 ПЕРЕВІРКА ІМПОРТІВ ПРОЕКТУ:")
    
    # Додавання app/ до Python path
    app_dir = Path('app')
    if app_dir.exists():
        sys.path.insert(0, str(app_dir))
        print("✅ Додано app/ до Python path")
    else:
        print("❌ Папка app/ не знайдена!")
        return ["Папка app/ відсутня"]
    
    project_modules = [
        ('config.settings', 'Налаштування проекту (app/config/)'),
        ('database.models', 'Моделі БД (app/database/)'),
        ('database.database', 'Сервіси БД (app/database/)'),
        ('handlers', 'Хендлери команд (app/handlers/)'),
        ('services', 'Бізнес-логіка (app/services/)'),
        ('utils', 'Утиліти (app/utils/)')
    ]
    
    issues = []
    
    for module, description in project_modules:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError as e:
            print(f"❌ {module} ({description}) - {str(e)}")
            issues.append(f"Помилка імпорту: {module}")
    
    return issues

async def check_bot_connection():
    """Перевірка з'єднання з Telegram"""
    print("\n🤖 ПЕРЕВІРКА З'ЄДНАННЯ З TELEGRAM:")
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не встановлено")
        return ["BOT_TOKEN відсутній"]
    
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Тест з'єднання
        bot_info = await bot.get_me()
        print(f"✅ Підключено до @{bot_info.username}")
        print(f"✅ Ім'я бота: {bot_info.first_name}")
        print(f"✅ ID бота: {bot_info.id}")
        
        await bot.session.close()
        return []
        
    except Exception as e:
        print(f"❌ Помилка з'єднання: {e}")
        return [f"Помилка Telegram API: {str(e)}"]

def check_database():
    """Перевірка бази даних"""
    print("\n💾 ПЕРЕВІРКА БАЗИ ДАНИХ:")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL не встановлено")
        return ["DATABASE_URL відсутній"]
    
    # Маскування паролю в URL
    masked_url = database_url
    if '@' in database_url:
        parts = database_url.split('@')
        if len(parts) == 2:
            credentials = parts[0].split('//')[-1]
            if ':' in credentials:
                user, password = credentials.split(':', 1)
                masked_url = database_url.replace(password, '***')
    
    print(f"✅ Database URL: {masked_url}")
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(database_url, echo=False)
        
        # Тест підключення
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ З'єднання з БД успішне")
                return []
            else:
                print("❌ Тест запиту не пройшов")
                return ["Помилка тестового запиту"]
                
    except Exception as e:
        print(f"❌ Помилка БД: {e}")
        return [f"Помилка бази даних: {str(e)}"]

def generate_fixes(all_issues):
    """Генерація рекомендацій для виправлення"""
    if not all_issues:
        return
    
    print("\n🛠️ РЕКОМЕНДАЦІЇ ДЛЯ ВИПРАВЛЕННЯ:")
    print("=" * 50)
    
    # Групування проблем
    env_issues = [i for i in all_issues if 'змінна' in i.lower()]
    dep_issues = [i for i in all_issues if 'залежність' in i.lower()]
    file_issues = [i for i in all_issues if 'файл' in i.lower()]
    import_issues = [i for i in all_issues if 'імпорт' in i.lower()]
    
    if env_issues:
        print("\n🌍 ЗМІННІ СЕРЕДОВИЩА:")
        print("Створіть файл .env з наступними змінними:")
        print("```")
        print("BOT_TOKEN=your_bot_token_here")
        print("ADMIN_ID=your_telegram_id")
        print("DATABASE_URL=sqlite:///bot.db  # для локальної розробки")
        print("```")
    
    if dep_issues:
        print("\n📦 ЗАЛЕЖНОСТІ:")
        print("Встановіть відсутні залежності:")
        print("```bash")
        print("pip install -r requirements.txt")
        print("# або")
        print("pip install aiogram sqlalchemy asyncpg")
        print("```")
    
    if file_issues:
        print("\n📁 ФАЙЛИ:")
        print("Переконайтеся що існують критичні файли:")
        for issue in file_issues:
            print(f"- {issue}")
    
    if import_issues:
        print("\n🔗 ІМПОРТИ:")
        print("Перевірте структуру проекту та наявність __init__.py файлів")
        print("Можливо потрібно додати app/ до Python path")

async def main():
    """Головна функція діагностики"""
    print_header()
    
    all_issues = []
    
    # Поетапна діагностика
    try:
        all_issues.extend(check_environment())
        all_issues.extend(check_structure())
        all_issues.extend(check_dependencies())
        all_issues.extend(check_imports())
        all_issues.extend(await check_bot_connection())
        all_issues.extend(check_database())
        
    except Exception as e:
        logger.error(f"Помилка діагностики: {e}")
        traceback.print_exc()
    
    # Підсумок
    print("\n📊 ПІДСУМОК ДІАГНОСТИКИ:")
    print("=" * 50)
    
    if not all_issues:
        print("🎉 ВСІ ПЕРЕВІРКИ ПРОЙДЕНО УСПІШНО!")
        print("✅ Бот готовий до запуску")
    else:
        print(f"⚠️ ЗНАЙДЕНО {len(all_issues)} ПРОБЛЕМ:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        generate_fixes(all_issues)
    
    print("\n🚀 ДЛЯ ЗАПУСКУ ВИКОРИСТОВУЙТЕ:")
    print("python main.py")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)