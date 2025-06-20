#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Швидке тестування контент-системи

Цей скрипт перевіряє чи правильно працюють всі компоненти контент-системи
"""

import sys
import os
from pathlib import Path

def print_header():
    print("🧪" * 20)
    print("\n🎭 ТЕСТУВАННЯ КОНТЕНТ-СИСТЕМИ")
    print("Перевірка всіх компонентів контенту")
    print("🧪" * 20)
    print()

def test_imports():
    """Тестування імпортів"""
    print("📦 ТЕСТУВАННЯ ІМПОРТІВ:")
    
    # Додаємо app/ до path
    app_dir = Path("app")
    if app_dir.exists():
        sys.path.insert(0, str(app_dir))
        print("✅ app/ додано до Python path")
    
    tests = [
        ("config.settings", "Налаштування"),
        ("database.models", "Моделі БД"),
        ("database.services", "Сервіси БД"),
        ("handlers.content_handlers", "Контент хендлери"),
        ("handlers", "Система хендлерів")
    ]
    
    success_count = 0
    for module, description in tests:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} - {description} ({e})")
    
    print(f"\n📊 Імпортів успішно: {success_count}/{len(tests)}")
    return success_count == len(tests)

def test_content_data():
    """Тестування демо контенту"""
    print("\n🎭 ТЕСТУВАННЯ ДЕМО КОНТЕНТУ:")
    
    try:
        from handlers.content_handlers import DEMO_MEMES, DEMO_JOKES, DEMO_ANEKDOTS
        
        print(f"😂 Демо мемів: {len(DEMO_MEMES)}")
        print(f"🤣 Демо жартів: {len(DEMO_JOKES)}")
        print(f"🧠 Демо анекдотів: {len(DEMO_ANEKDOTS)}")
        
        # Показуємо приклади
        if DEMO_MEMES:
            print(f"\n📝 Приклад мему:\n{DEMO_MEMES[0][:100]}...")
        if DEMO_JOKES:
            print(f"\n📝 Приклад жарту:\n{DEMO_JOKES[0][:100]}...")
        if DEMO_ANEKDOTS:
            print(f"\n📝 Приклад анекдоту:\n{DEMO_ANEKDOTS[0][:100]}...")
        
        print("\n✅ Демо контент завантажено успішно")
        return True
        
    except Exception as e:
        print(f"❌ Помилка завантаження демо контенту: {e}")
        return False

def test_database_connection():
    """Тестування з'єднання з БД"""
    print("\n💾 ТЕСТУВАННЯ БАЗИ ДАНИХ:")
    
    try:
        from database.services import init_database, test_database_connection
        
        # Тестовий URL БД
        test_db_url = os.getenv('DATABASE_URL', 'sqlite:///test_bot.db')
        print(f"🔗 URL БД: {test_db_url}")
        
        # Ініціалізація
        if init_database(test_db_url):
            print("✅ База даних ініціалізована")
            
            # Тестування з'єднання
            if test_database_connection():
                print("✅ З'єднання з БД успішне")
                return True
            else:
                print("❌ З'єднання з БД неможливе")
                return False
        else:
            print("❌ Ініціалізація БД невдала")
            return False
            
    except Exception as e:
        print(f"❌ Помилка БД: {e}")
        return False

def test_content_functions():
    """Тестування контентних функцій"""
    print("\n🔧 ТЕСТУВАННЯ КОНТЕНТНИХ ФУНКЦІЙ:")
    
    try:
        from handlers.content_handlers import get_content_keyboard
        
        # Тестування створення клавіатури
        keyboard = get_content_keyboard(1, "demo")
        if keyboard:
            print("✅ Клавіатура контенту створюється")
        
        # Тестування FSM станів
        from handlers.content_handlers import ContentSubmissionStates
        print("✅ FSM стани для подачі контенту доступні")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка контентних функцій: {e}")
        return False

def test_handlers_registration():
    """Тестування реєстрації хендлерів"""
    print("\n📋 ТЕСТУВАННЯ РЕЄСТРАЦІЇ ХЕНДЛЕРІВ:")
    
    try:
        from aiogram import Dispatcher
        from handlers import register_all_handlers
        
        # Створюємо тестовий диспетчер
        dp = Dispatcher()
        
        # Реєструємо хендлери
        register_all_handlers(dp)
        print("✅ Хендлери зареєстровано без помилок")
        
        # Перевіряємо кількість зареєстрованих хендлерів
        print(f"📊 Зареєстровано хендлерів: {len(dp.message.handlers) + len(dp.callback_query.handlers)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка реєстрації хендлерів: {e}")
        return False

def main():
    """Головна функція тестування"""
    print_header()
    
    # Список тестів
    tests = [
        ("Імпорти", test_imports),
        ("Демо контент", test_content_data),
        ("База даних", test_database_connection),
        ("Контентні функції", test_content_functions),
        ("Реєстрація хендлерів", test_handlers_registration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Тест '{test_name}' не пройшов")
        except Exception as e:
            print(f"💥 Тест '{test_name}' викликав помилку: {e}")
    
    # Підсумок
    print("\n" + "="*50)
    print(f"📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ")
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Не пройдено: {total - passed}")
    
    if passed == total:
        print("\n🎉 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        print("🚀 Контент-система готова до роботи!")
        print("\n📋 Доступні команди в боті:")
        print("   /meme - випадковий мем")
        print("   /joke - смішний жарт") 
        print("   /anekdot - український анекдот")
        print("   📝 Кнопки для подачі власного контенту")
    else:
        print("\n⚠️ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ")
        print("🔧 Перевірте помилки вище та виправте їх")
    
    print("\n🧪 Тестування завершено!")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)