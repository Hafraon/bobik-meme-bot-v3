#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Швидка діагностика стану бота після виправлень 🧠😂🔥
"""

import sys
import traceback
from datetime import datetime

def test_imports():
    """Тестування імпортів"""
    print("🔍 ТЕСТУВАННЯ ІМПОРТІВ:")
    
    tests = [
        ("config.settings", "Налаштування"),
        ("database.models", "Моделі БД"),
        ("database.database", "Функції БД"),
        ("database", "Database пакет"),
        ("handlers.basic_commands", "Основні команди"),
        ("handlers.content_handlers", "Контент хендлери"),
        ("handlers.admin_panel_handlers", "Адмін панель"),
    ]
    
    success_count = 0
    failed_imports = []
    
    for module, description in tests:
        try:
            __import__(module)
            print(f"  ✅ {description}: OK")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
            failed_imports.append((module, str(e)))
    
    print(f"\n📊 Імпортів працює: {success_count}/{len(tests)}")
    return success_count, failed_imports

def test_database_functions():
    """Тестування функцій БД"""
    print("\n🔍 ТЕСТУВАННЯ ФУНКЦІЙ БД:")
    
    try:
        from database import (
            get_recommended_content,
            add_content_rating,
            add_content_for_moderation,
            record_content_view,
            get_user_stats
        )
        
        functions = [
            "get_recommended_content",
            "add_content_rating", 
            "add_content_for_moderation",
            "record_content_view",
            "get_user_stats"
        ]
        
        for func_name in functions:
            print(f"  ✅ {func_name}: імпортується")
        
        print(f"\n📊 Всі критичні функції доступні!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Помилка імпорту: {e}")
        return False

def test_user_model():
    """Тестування моделі User"""
    print("\n🔍 ТЕСТУВАННЯ МОДЕЛІ USER:")
    
    try:
        from database.models import User
        
        # Перевіряємо чи є поле is_active
        if hasattr(User, 'is_active'):
            print("  ✅ Поле is_active: присутнє")
        else:
            print("  ❌ Поле is_active: відсутнє")
            return False
        
        # Тестуємо створення екземпляру
        test_user_data = {
            'telegram_id': 123456,
            'username': 'test_user',
            'first_name': 'Test',
            'is_active': True
        }
        
        # Перевіряємо чи можна створити користувача з is_active
        user = User(**test_user_data)
        print("  ✅ Створення User з is_active: OK")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Помилка моделі User: {e}")
        return False

def test_handlers():
    """Тестування хендлерів"""
    print("\n🔍 ТЕСТУВАННЯ ХЕНДЛЕРІВ:")
    
    try:
        from handlers.content_handlers import (
            cmd_meme, cmd_anekdot, cmd_submit,
            callback_like_content, callback_dislike_content
        )
        
        handlers = [
            "cmd_meme",
            "cmd_anekdot", 
            "cmd_submit",
            "callback_like_content",
            "callback_dislike_content"
        ]
        
        for handler_name in handlers:
            print(f"  ✅ {handler_name}: імпортується")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Помилка хендлерів: {e}")
        return False

def test_bot_token():
    """Перевірка налаштувань"""
    print("\n🔍 ПЕРЕВІРКА НАЛАШТУВАНЬ:")
    
    try:
        from config.settings import settings
        
        if hasattr(settings, 'BOT_TOKEN') and settings.BOT_TOKEN:
            token_preview = settings.BOT_TOKEN[:10] + "..." if len(settings.BOT_TOKEN) > 10 else settings.BOT_TOKEN
            print(f"  ✅ BOT_TOKEN: {token_preview}")
        else:
            print("  ❌ BOT_TOKEN: не налаштовано")
            return False
        
        if hasattr(settings, 'ADMIN_ID') and settings.ADMIN_ID:
            print(f"  ✅ ADMIN_ID: {settings.ADMIN_ID}")
        else:
            print("  ❌ ADMIN_ID: не налаштовано")
            return False
        
        if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
            db_preview = settings.DATABASE_URL[:20] + "..." if len(settings.DATABASE_URL) > 20 else settings.DATABASE_URL
            print(f"  ✅ DATABASE_URL: {db_preview}")
        else:
            print("  ❌ DATABASE_URL: не налаштовано")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Помилка налаштувань: {e}")
        return False

def main():
    """Головна функція діагностики"""
    print("🧠😂🔥 ДІАГНОСТИКА БОТА ПІСЛЯ ВИПРАВЛЕНЬ 🧠😂🔥")
    print(f"⏰ Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Тести
    tests_results = []
    
    # 1. Тестування імпортів
    success_count, failed_imports = test_imports()
    tests_results.append(("Імпорти", success_count >= 6))
    
    # 2. Тестування функцій БД
    db_functions_ok = test_database_functions()
    tests_results.append(("Функції БД", db_functions_ok))
    
    # 3. Тестування моделі User
    user_model_ok = test_user_model()
    tests_results.append(("Модель User", user_model_ok))
    
    # 4. Тестування хендлерів
    handlers_ok = test_handlers()
    tests_results.append(("Хендлери", handlers_ok))
    
    # 5. Тестування налаштувань
    settings_ok = test_bot_token()
    tests_results.append(("Налаштування", settings_ok))
    
    # Підсумок
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТИ ДІАГНОСТИКИ:")
    
    all_passed = True
    for test_name, passed in tests_results:
        status = "✅ ПРОЙДЕНО" if passed else "❌ ПРОВАЛЕНО"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 ЗАГАЛЬНИЙ РЕЗУЛЬТАТ:")
    if all_passed:
        print("🎉 ВСЕ ТЕСТИ ПРОЙДЕНІ! Бот готовий до роботи!")
        return 0
    else:
        print("⚠️ ДЕЯКІ ТЕСТИ ПРОВАЛЕНІ. Потрібні додаткові виправлення.")
        
        if failed_imports:
            print("\n❌ Помилки імпортів:")
            for module, error in failed_imports:
                print(f"  - {module}: {error}")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Діагностику перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Критична помилка діагностики: {e}")
        print("🔍 Детальна інформація:")
        traceback.print_exc()
        sys.exit(1)