#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Діагностичний скрипт для перевірки всіх модулів 🧠😂🔥
"""

import sys
import traceback
from pathlib import Path

print("🧠😂🔥 ДІАГНОСТИКА МОДУЛІВ УКРАЇНОМОВНОГО БОТА 🧠😂🔥\n")

def check_module(module_name, description):
    """Перевірка одного модулю"""
    try:
        print(f"🔍 Перевіряю {description}...", end=" ")
        
        if module_name == "config.settings":
            from config.settings import settings, EMOJI, TEXTS
            print(f"✅ OK (Адмін: {settings.ADMIN_ID})")
            return True
        
        elif module_name == "database.database":
            from database.database import init_db, get_db_session
            print("✅ OK")
            return True
            
        elif module_name == "database.models":
            from database.models import User, Content, Duel, Rating
            print("✅ OK")
            return True
            
        elif module_name == "handlers":
            from handlers import register_handlers
            print("✅ OK")
            return True
            
        elif module_name == "handlers.basic_commands":
            from handlers.basic_commands import register_basic_handlers
            print("✅ OK")
            return True
            
        elif module_name == "handlers.content_handlers":
            from handlers.content_handlers import register_content_handlers
            print("✅ OK")
            return True
            
        elif module_name == "handlers.gamification_handlers":
            from handlers.gamification_handlers import register_gamification_handlers
            print("✅ OK")
            return True
            
        elif module_name == "handlers.moderation_handlers":
            from handlers.moderation_handlers import register_moderation_handlers
            print("✅ OK")
            return True
            
        elif module_name == "handlers.duel_handlers":
            from handlers.duel_handlers import register_duel_handlers
            print("✅ OK")
            return True
            
        elif module_name == "middlewares.auth":
            from middlewares.auth import AuthMiddleware, AntiSpamMiddleware
            print("✅ OK")
            return True
            
        elif module_name == "services.scheduler":
            from services.scheduler import SchedulerService
            print("✅ OK")
            return True
            
        elif module_name == "services.content_generator":
            from services.content_generator import content_generator
            print("✅ OK")
            return True
            
        else:
            __import__(module_name)
            print("✅ OK")
            return True
            
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_dependencies():
    """Перевірка зовнішніх залежностей"""
    print("\n📦 ПЕРЕВІРКА ЗАЛЕЖНОСТЕЙ:")
    
    dependencies = [
        ("aiogram", "Telegram Bot API"),
        ("sqlalchemy", "ORM для БД"),
        ("aiohttp", "HTTP клієнт"),
        ("apscheduler", "Планувальник"),
        ("openai", "OpenAI API"),
        ("asyncpg", "PostgreSQL драйвер")
    ]
    
    success_count = 0
    for dep, desc in dependencies:
        try:
            print(f"📚 {desc}...", end=" ")
            __import__(dep)
            print("✅ OK")
            success_count += 1
        except ImportError:
            print("❌ Відсутня")
    
    print(f"\n📊 Залежностей встановлено: {success_count}/{len(dependencies)}")
    return success_count == len(dependencies)

def check_files():
    """Перевірка наявності файлів"""
    print("\n📁 ПЕРЕВІРКА ФАЙЛІВ:")
    
    required_files = [
        ("main.py", "Головний файл"),
        ("config/settings.py", "Налаштування"),
        ("database/models.py", "Моделі БД"),
        ("database/database.py", "Робота з БД"),
        ("handlers/__init__.py", "Ініціалізація хендлерів"),
        ("middlewares/auth.py", "Middleware"),
        ("services/scheduler.py", "Планувальник"),
        ("requirements.txt", "Залежності")
    ]
    
    success_count = 0
    for file_path, desc in required_files:
        if Path(file_path).exists():
            print(f"📄 {desc}: ✅ Існує")
            success_count += 1
        else:
            print(f"📄 {desc}: ❌ Відсутній ({file_path})")
    
    print(f"\n📊 Файлів знайдено: {success_count}/{len(required_files)}")
    return success_count == len(required_files)

def main():
    """Головна функція діагностики"""
    
    # Перевірка файлів
    files_ok = check_files()
    
    # Перевірка залежностей
    deps_ok = check_dependencies()
    
    # Перевірка модулів
    print("\n🔧 ПЕРЕВІРКА МОДУЛІВ:")
    
    modules_to_check = [
        ("config.settings", "Налаштування"),
        ("database.models", "Моделі БД"),
        ("database.database", "Робота з БД"),
        ("handlers", "Головний реєстратор хендлерів"),
        ("handlers.basic_commands", "Основні команди"),
        ("handlers.content_handlers", "Контент хендлери"),
        ("handlers.gamification_handlers", "Гейміфікація"),
        ("handlers.moderation_handlers", "Модерація"),
        ("handlers.duel_handlers", "Дуелі"),
        ("middlewares.auth", "Middleware аутентифікації"),
        ("services.scheduler", "Планувальник"),
        ("services.content_generator", "AI генератор")
    ]
    
    success_count = 0
    for module, desc in modules_to_check:
        if check_module(module, desc):
            success_count += 1
    
    print(f"\n📊 Модулів працює: {success_count}/{len(modules_to_check)}")
    
    # Загальний висновок
    print(f"\n🎯 ЗАГАЛЬНИЙ РЕЗУЛЬТАТ:")
    print(f"📁 Файли: {'✅' if files_ok else '❌'}")
    print(f"📦 Залежності: {'✅' if deps_ok else '❌'}")
    print(f"🔧 Модулі: {'✅' if success_count >= len(modules_to_check) * 0.8 else '❌'}")
    
    if files_ok and deps_ok and success_count >= len(modules_to_check) * 0.8:
        print(f"\n🎉 ВСЕ ГОТОВО ДО ЗАПУСКУ! 🚀")
        return True
    else:
        print(f"\n⚠️ ПОТРІБНІ ДОДАТКОВІ НАЛАШТУВАННЯ")
        
        if not files_ok:
            print("   📁 Створіть відсутні файли")
        if not deps_ok:
            print("   📦 Встановіть відсутні залежності: pip install -r requirements.txt")
        if success_count < len(modules_to_check) * 0.8:
            print("   🔧 Виправте помилки в модулях")
        
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Діагностику перервано")
    except Exception as e:
        print(f"\n\n💥 Критична помилка діагностики: {e}")
        traceback.print_exc()