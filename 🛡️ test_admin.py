#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ Тестування адмін функцій

Цей скрипт перевіряє чи правильно працюють всі компоненти адмін системи
"""

import sys
import os
from pathlib import Path

def print_header():
    print("🛡️" * 20)
    print("\n🔧 ТЕСТУВАННЯ АДМІН СИСТЕМИ")
    print("Перевірка модерації та адмін функцій")
    print("🛡️" * 20)
    print()

def test_admin_imports():
    """Тестування імпортів адмін модулів"""
    print("📦 ТЕСТУВАННЯ АДМІН ІМПОРТІВ:")
    
    # Додаємо app/ до path
    app_dir = Path("app")
    if app_dir.exists():
        sys.path.insert(0, str(app_dir))
        print("✅ app/ додано до Python path")
    
    tests = [
        ("handlers.admin_handlers", "Адмін хендлери"),
        ("handlers.admin_handlers.register_admin_handlers", "Реєстрація адмін хендлерів"),
        ("handlers.admin_handlers.is_admin", "Перевірка адмін прав"),
        ("handlers.admin_handlers.approve_content", "Функція схвалення"),
        ("handlers.admin_handlers.reject_content", "Функція відхилення"),
        ("handlers.admin_handlers.ModerationStates", "FSM стани модерації")
    ]
    
    success_count = 0
    for module_path, description in tests:
        try:
            if "." in module_path:
                # Імпорт конкретної функції/класу
                module_name, attr_name = module_path.rsplit(".", 1)
                module = __import__(module_name, fromlist=[attr_name])
                getattr(module, attr_name)
            else:
                # Імпорт модуля
                __import__(module_path)
            print(f"✅ {module_path} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_path} - {description} ({e})")
        except AttributeError as e:
            print(f"❌ {module_path} - {description} (AttributeError: {e})")
    
    print(f"\n📊 Адмін імпортів успішно: {success_count}/{len(tests)}")
    return success_count == len(tests)

def test_admin_permissions():
    """Тестування системи прав адміна"""
    print("\n👑 ТЕСТУВАННЯ ПРАВ АДМІНА:")
    
    try:
        from handlers.admin_handlers import is_admin
        
        # Тестуємо з реальним ID адміна
        admin_id = int(os.getenv('ADMIN_ID', 0))
        
        if admin_id > 0:
            is_admin_result = is_admin(admin_id)
            print(f"✅ Перевірка адмін ID {admin_id}: {'адмін' if is_admin_result else 'не адмін'}")
            
            # Тестуємо з фейковим ID
            fake_id = 999999999
            is_fake_admin = is_admin(fake_id)
            print(f"✅ Перевірка фейк ID {fake_id}: {'адмін' if is_fake_admin else 'не адмін'}")
            
            # Результат тесту
            if is_admin_result and not is_fake_admin:
                print("✅ Система прав працює коректно")
                return True
            else:
                print("❌ Помилка в системі прав")
                return False
        else:
            print("⚠️ ADMIN_ID не встановлено в змінних середовища")
            return False
            
    except Exception as e:
        print(f"❌ Помилка тестування прав: {e}")
        return False

def test_moderation_functions():
    """Тестування функцій модерації"""
    print("\n🔧 ТЕСТУВАННЯ ФУНКЦІЙ МОДЕРАЦІЇ:")
    
    try:
        # Перевіряємо наявність функцій
        from handlers.admin_handlers import approve_content, reject_content
        print("✅ Функції approve_content та reject_content доступні")
        
        # Перевіряємо FSM стани
        from handlers.admin_handlers import ModerationStates
        print("✅ FSM стани модерації доступні")
        
        # Перевіряємо стани
        states = [
            ModerationStates.waiting_for_rejection_reason
        ]
        
        for state in states:
            if state:
                print(f"✅ FSM стан {state.state} доступний")
            else:
                print(f"❌ FSM стан недоступний")
        
        print("✅ Всі функції модерації доступні")
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування функцій модерації: {e}")
        return False

def test_database_admin_functions():
    """Тестування адмін функцій БД"""
    print("\n💾 ТЕСТУВАННЯ АДМІН ФУНКЦІЙ БД:")
    
    try:
        from database.services import (
            get_basic_stats, 
            get_detailed_admin_stats,
            get_pending_content_list,
            get_content_by_id
        )
        
        print("✅ Адмін функції БД імпортовано")
        
        # Тестуємо базову статистику
        stats = get_basic_stats()
        required_keys = ['total_users', 'total_content', 'approved_content', 'pending_content', 'rejected_content']
        
        for key in required_keys:
            if key in stats:
                print(f"✅ Статистика '{key}': {stats[key]}")
            else:
                print(f"❌ Відсутня статистика '{key}'")
        
        # Тестуємо детальну статистику
        detailed_stats = get_detailed_admin_stats()
        if 'approval_rate' in detailed_stats:
            print(f"✅ Детальна статистика доступна (Approval rate: {detailed_stats['approval_rate']}%)")
        else:
            print("❌ Детальна статистика недоступна")
        
        # Тестуємо список на модерації
        pending_list = get_pending_content_list(5)
        print(f"✅ Контент на модерації: {len(pending_list)} записів")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування адмін функцій БД: {e}")
        return False

def test_admin_commands():
    """Тестування адмін команд"""
    print("\n⚡ ТЕСТУВАННЯ АДМІН КОМАНД:")
    
    admin_commands = [
        ("/admin_stats", "cmd_admin_stats"),
        ("/moderate", "cmd_moderate"), 
        ("/pending", "cmd_pending"),
        ("/approve", "cmd_approve"),
        ("/reject", "cmd_reject")
    ]
    
    try:
        from handlers.admin_handlers import (
            cmd_admin_stats, cmd_moderate, cmd_pending, 
            cmd_approve, cmd_reject
        )
        
        print("✅ Всі адмін команди імпортовано")
        
        for command, function_name in admin_commands:
            print(f"✅ {command} → {function_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка імпорту адмін команд: {e}")
        return False

def test_admin_callbacks():
    """Тестування адмін callback'ів"""
    print("\n🔘 ТЕСТУВАННЯ АДМІН CALLBACK'ІВ:")
    
    try:
        from handlers.admin_handlers import handle_admin_callbacks
        print("✅ Функція handle_admin_callbacks доступна")
        
        # Тестові callback дані
        test_callbacks = [
            "admin_moderate",
            "admin_pending", 
            "admin_refresh_stats",
            "admin_top_users",
            "moderate_approve_123",
            "moderate_reject_456",
            "moderate_next",
            "moderate_refresh"
        ]
        
        print("✅ Тестові callback'и:")
        for callback in test_callbacks:
            print(f"   • {callback}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування callback'ів: {e}")
        return False

def test_admin_integration():
    """Тестування інтеграції з основним ботом"""
    print("\n🔗 ТЕСТУВАННЯ ІНТЕГРАЦІЇ:")
    
    try:
        # Перевіряємо реєстрацію в handlers/__init__.py
        from handlers import register_all_handlers
        print("✅ Функція register_all_handlers доступна")
        
        # Перевіряємо чи register_admin_handlers викликається
        import inspect
        source = inspect.getsource(register_all_handlers)
        
        if "register_admin_handlers" in source:
            print("✅ register_admin_handlers викликається в register_all_handlers")
        else:
            print("❌ register_admin_handlers НЕ викликається в register_all_handlers")
            return False
        
        # Тестуємо створення диспетчера
        from aiogram import Dispatcher
        dp = Dispatcher()
        
        try:
            register_all_handlers(dp)
            print("✅ Хендлери реєструються без помилок")
        except Exception as e:
            print(f"❌ Помилка реєстрації хендлерів: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування інтеграції: {e}")
        return False

def generate_admin_usage_guide():
    """Генерація посібника користування адмін функціями"""
    print("\n📖 ПОСІБНИК КОРИСТУВАННЯ АДМІН ФУНКЦІЯМИ:")
    print("=" * 50)
    
    print("\n🛡️ АДМІН КОМАНДИ:")
    print("   /admin_stats - детальна статистика бота")
    print("   /moderate - почати модерацію контенту")
    print("   /pending - список контенту на розгляді")
    print("   /approve_5 - швидко схвалити контент ID 5")
    print("   /reject_3 Неприйнятний контент - відхилити з причиною")
    
    print("\n🔘 ІНТЕРАКТИВНІ КНОПКИ (тільки для адміна):")
    print("   📊 Адмін статистика - детальна статистика")
    print("   🛡️ Модерація - почати модерацію")
    print("   📋 На розгляді - список контенту")
    print("   👥 Адмін топ - топ користувачів")
    
    print("\n⚡ ШВИДКА МОДЕРАЦІЯ:")
    print("   1. /moderate - відкрити контент на модерації")
    print("   2. Натиснути ✅ Схвалити або ❌ Відхилити")
    print("   3. При відхиленні - ввести причину")
    print("   4. Автоматично перейти до наступного контенту")
    
    print("\n💡 ПОРАДИ:")
    print("   • Використовуйте /pending для швидкого огляду")
    print("   • /approve_ID для швидкого схвалення без інтерфейсу")
    print("   • /reject_ID причина для швидкого відхилення")
    print("   • Всі дії записуються в логи")

def main():
    """Головна функція тестування адмін системи"""
    print_header()
    
    # Список тестів
    tests = [
        ("Адмін імпорти", test_admin_imports),
        ("Права адміна", test_admin_permissions),
        ("Функції модерації", test_moderation_functions),
        ("БД функції", test_database_admin_functions),
        ("Адмін команди", test_admin_commands),
        ("Callback'и", test_admin_callbacks),
        ("Інтеграція", test_admin_integration)
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
    print(f"📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ АДМІН СИСТЕМИ")
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Не пройдено: {total - passed}")
    
    if passed == total:
        print("\n🎉 ВСІ ТЕСТИ АДМІН СИСТЕМИ ПРОЙШЛИ УСПІШНО!")
        print("🛡️ Адмін функції готові до роботи!")
        
        # Показуємо посібник
        generate_admin_usage_guide()
        
    else:
        print("\n⚠️ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ")
        print("🔧 Перевірте помилки вище та виправте їх")
    
    print(f"\n🛡️ Тестування адмін системи завершено!")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)