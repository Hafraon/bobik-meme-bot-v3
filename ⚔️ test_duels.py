#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚔️ ТЕСТУВАННЯ СИСТЕМИ ДУЕЛІВ

Цей скрипт перевіряє чи правильно працюють всі компоненти системи дуелів жартів
"""

import sys
import os
from pathlib import Path

def print_header():
    print("⚔️" * 25)
    print("\n🔧 ТЕСТУВАННЯ СИСТЕМИ ДУЕЛІВ ЖАРТІВ")
    print("Перевірка всіх компонентів дуельної системи")
    print("⚔️" * 25)
    print()

def test_duel_imports():
    """Тестування імпортів дуельних модулів"""
    print("📦 ТЕСТУВАННЯ ДУЕЛЬНИХ ІМПОРТІВ:")
    
    # Додаємо app/ до path
    app_dir = Path("app")
    if app_dir.exists():
        sys.path.insert(0, str(app_dir))
        print("✅ app/ додано до Python path")
    
    tests = [
        ("handlers.duel_handlers", "Дуельні хендлери"),
        ("handlers.duel_handlers.register_duel_handlers", "Реєстрація дуельних хендлерів"),
        ("handlers.duel_handlers.cmd_duel", "Команда /duel"),
        ("handlers.duel_handlers.create_random_duel", "Створення випадкової дуелі"),
        ("handlers.duel_handlers.DuelStates", "FSM стани дуелів"),
        ("handlers.duel_handlers.RANK_REWARDS", "Система нагород"),
        ("database.services.create_duel", "Створення дуелі в БД"),
        ("database.services.vote_in_duel", "Голосування в дуелі"),
        ("database.services.finish_duel", "Завершення дуелі"),
        ("database.services.get_user_duel_stats", "Статистика дуелів користувача"),
        ("database.services.auto_finish_expired_duels", "Автозавершення дуелів")
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
            
            print(f"✅ {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description} - ImportError: {e}")
        except AttributeError as e:
            print(f"❌ {description} - AttributeError: {e}")
        except Exception as e:
            print(f"⚠️ {description} - {e}")
    
    print(f"\n📊 Результат: {success_count}/{len(tests)} пройдено")
    return success_count

def test_database_models():
    """Тестування моделей дуелів в БД"""
    print("\n💾 ТЕСТУВАННЯ МОДЕЛЕЙ ДУЕЛІВ:")
    
    try:
        from database.models import Duel, DuelVote, DuelStatus
        print("✅ Модель Duel - дуелі жартів")
        print("✅ Модель DuelVote - голосування")
        print("✅ Enum DuelStatus - статуси дуелей")
        
        # Перевіряємо атрибути моделі Duel
        duel_attrs = [
            'id', 'content1_id', 'content2_id', 'status',
            'content1_votes', 'content2_votes', 'total_votes',
            'ends_at', 'created_at', 'finished_at', 'winner_content_id'
        ]
        
        missing_attrs = []
        for attr in duel_attrs:
            if not hasattr(Duel, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"⚠️ Відсутні атрибути в Duel: {missing_attrs}")
        else:
            print("✅ Всі необхідні атрибути Duel присутні")
        
        # Перевіряємо DuelVote
        vote_attrs = ['id', 'duel_id', 'user_id', 'content_id', 'created_at']
        missing_vote_attrs = []
        for attr in vote_attrs:
            if not hasattr(DuelVote, attr):
                missing_vote_attrs.append(attr)
        
        if missing_vote_attrs:
            print(f"⚠️ Відсутні атрибути в DuelVote: {missing_vote_attrs}")
        else:
            print("✅ Всі необхідні атрибути DuelVote присутні")
        
        return True
        
    except ImportError as e:
        print(f"❌ Моделі дуелів недоступні: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Помилка перевірки моделей: {e}")
        return False

def test_duel_services():
    """Тестування сервісів дуелів"""
    print("\n🔧 ТЕСТУВАННЯ СЕРВІСІВ ДУЕЛІВ:")
    
    services = [
        ("create_duel", "Створення дуелі"),
        ("get_duel_by_id", "Отримання дуелі за ID"),
        ("get_active_duels", "Список активних дуелів"),
        ("vote_in_duel", "Голосування в дуелі"),
        ("finish_duel", "Завершення дуелі"),
        ("get_user_duel_stats", "Статистика користувача"),
        ("get_random_approved_content", "Випадковий контент"),
        ("auto_finish_expired_duels", "Автозавершення"),
        ("cleanup_old_duels", "Очистка старих дуелів")
    ]
    
    success_count = 0
    try:
        from database import services
        
        for service_name, description in services:
            if hasattr(services, service_name):
                print(f"✅ {description}")
                success_count += 1
            else:
                print(f"❌ {description} - функція відсутня")
        
        print(f"\n📊 Сервіси: {success_count}/{len(services)} доступно")
        return success_count >= len(services) * 0.8  # 80% сервісів має бути доступно
        
    except ImportError as e:
        print(f"❌ Сервіси дуелів недоступні: {e}")
        return False

def test_scheduler_support():
    """Тестування підтримки планувальника"""
    print("\n⏰ ТЕСТУВАННЯ ПЛАНУВАЛЬНИКА:")
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        print("✅ APScheduler доступний")
        
        from apscheduler.triggers.interval import IntervalTrigger
        print("✅ IntervalTrigger доступний")
        
        # Тестуємо створення планувальника
        scheduler = AsyncIOScheduler()
        print("✅ Планувальник створено успішно")
        
        return True
        
    except ImportError as e:
        print(f"❌ APScheduler недоступний: {e}")
        print("💡 Встановіть: pip install APScheduler>=3.10.0")
        return False
    except Exception as e:
        print(f"⚠️ Помилка планувальника: {e}")
        return False

def test_handlers_integration():
    """Тестування інтеграції хендлерів"""
    print("\n🔗 ТЕСТУВАННЯ ІНТЕГРАЦІЇ ХЕНДЛЕРІВ:")
    
    try:
        from handlers import register_handlers
        print("✅ Функція register_handlers доступна")
        
        from handlers import check_handlers_status
        status = check_handlers_status()
        
        print(f"📊 Статус хендлерів:")
        print(f"  • Content: {'✅' if status.get('content_handlers') else '❌'}")
        print(f"  • Admin: {'✅' if status.get('admin_handlers') else '❌'}")
        print(f"  • Duel: {'✅' if status.get('duel_handlers') else '❌'}")
        print(f"  • Fallback: {'✅' if status.get('fallback_handlers') else '❌'}")
        
        if status.get('duel_handlers'):
            print("✅ Дуельні хендлери інтегровані")
            return True
        else:
            print("❌ Дуельні хендлери НЕ інтегровані")
            return False
            
    except ImportError as e:
        print(f"❌ Хендлери недоступні: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Помилка інтеграції: {e}")
        return False

def test_main_app_integration():
    """Тестування інтеграції з основним додатком"""
    print("\n🎮 ТЕСТУВАННЯ ІНТЕГРАЦІЇ З ДОДАТКОМ:")
    
    try:
        from main import UkrainianTelegramBotWithDuels
        print("✅ Основний клас бота доступний")
        
        # Перевіряємо методи
        bot_class = UkrainianTelegramBotWithDuels
        methods = [
            'initialize_bot', 'initialize_database', 'register_handlers',
            'setup_scheduler', 'main'
        ]
        
        missing_methods = []
        for method in methods:
            if not hasattr(bot_class, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"⚠️ Відсутні методи: {missing_methods}")
        else:
            print("✅ Всі необхідні методи присутні")
        
        return len(missing_methods) == 0
        
    except ImportError as e:
        print(f"❌ Основний додаток недоступний: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Помилка додатку: {e}")
        return False

def run_comprehensive_test():
    """Запуск повного тестування"""
    print_header()
    
    tests = [
        ("Імпорти дуелів", test_duel_imports),
        ("Моделі БД", test_database_models),
        ("Сервіси дуелів", test_duel_services),
        ("Планувальник", test_scheduler_support),
        ("Інтеграція хендлерів", test_handlers_integration),
        ("Інтеграція додатку", test_main_app_integration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n{'='*50}")
        print(f"🧪 ТЕСТ: {test_name}")
        print('='*50)
        
        try:
            result = test_function()
            if result:
                passed_tests += 1
                print(f"✅ ТЕСТ '{test_name}' ПРОЙДЕНО")
            else:
                print(f"❌ ТЕСТ '{test_name}' НЕ ПРОЙДЕНО")
        except Exception as e:
            print(f"💥 ТЕСТ '{test_name}' ЗАВЕРШИВСЯ ПОМИЛКОЮ: {e}")
    
    # Підсумок
    print(f"\n{'🏆'*25}")
    print(f"📊 ПІДСУМОК ТЕСТУВАННЯ")
    print(f"{'🏆'*25}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"✅ Пройдено: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        print("⚔️ Система дуелів готова до роботи!")
        return True
    elif passed_tests >= total_tests * 0.8:  # 80%
        print("🔶 БІЛЬШІСТЬ ТЕСТІВ ПРОЙШЛИ!")
        print("⚔️ Система дуелів готова з деякими обмеженнями")
        return True
    else:
        print("❌ ЗАНАДТО БАГАТО ПОМИЛОК!")
        print("🔧 Необхідно виправити проблеми перед запуском")
        return False

def main():
    """Головна функція тестування"""
    try:
        success = run_comprehensive_test()
        
        if success:
            print(f"\n🚀 РЕКОМЕНДАЦІЇ:")
            print(f"1. Запустіть: python main.py")
            print(f"2. Протестуйте команду: /duel")
            print(f"3. Створіть дуель та проголосуйте")
            print(f"4. Перевірте рейтинг: /profile")
            print(f"5. Переглядайте активні дуелі")
            
        else:
            print(f"\n🔧 НЕОБХІДНІ ДІЇ:")
            print(f"1. Встановіть відсутні залежності")
            print(f"2. Виправте помилки імпорту")
            print(f"3. Перевірте структуру файлів")
            print(f"4. Запустіть тест знову")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Тестування перервано користувачем")
        return False
    except Exception as e:
        print(f"\n💥 Критична помилка тестування: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)