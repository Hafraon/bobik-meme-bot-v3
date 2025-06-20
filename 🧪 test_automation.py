#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 ТЕСТУВАННЯ СИСТЕМИ АВТОМАТИЗАЦІЇ

Комплексне тестування всіх компонентів автоматизації:
- Планувальник завдань
- Система розсилок  
- Автоматичні дуелі
- База даних сервіси
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    print("🧪" * 30)
    print("\n🤖 ТЕСТУВАННЯ СИСТЕМИ АВТОМАТИЗАЦІЇ")
    print("Перевірка всіх компонентів автоматизації бота")
    print("🧪" * 30)
    print()

def test_automation_imports():
    """Тестування імпортів модулів автоматизації"""
    print("📦 ТЕСТУВАННЯ ІМПОРТІВ АВТОМАТИЗАЦІЇ:")
    
    # Додаємо app/ до path
    app_dir = Path("app")
    if app_dir.exists():
        sys.path.insert(0, str(app_dir))
        print("✅ app/ додано до Python path")
    
    tests = [
        # Основні модулі автоматизації
        ("services.automated_scheduler", "Автоматизований планувальник"),
        ("services.automated_scheduler.AutomatedScheduler", "Клас планувальника"),
        ("services.automated_scheduler.create_automated_scheduler", "Фабрика планувальника"),
        
        # Система розсилок
        ("services.broadcast_system", "Система розсилок"),
        ("services.broadcast_system.BroadcastSystem", "Клас розсилок"),
        ("services.broadcast_system.create_broadcast_system", "Фабрика розсилок"),
        
        # Розширені сервіси БД
        ("database.services.get_active_users_for_broadcast", "Користувачі для розсилки"),
        ("database.services.get_daily_best_content", "Кращий контент дня"),
        ("database.services.generate_weekly_stats", "Тижнева статистика"),
        ("database.services.get_recent_achievements", "Недавні досягнення"),
        ("database.services.get_broadcast_statistics", "Статистика розсилок"),
        
        # Планувальник APScheduler
        ("apscheduler.schedulers.asyncio.AsyncIOScheduler", "AsyncIO планувальник"),
        ("apscheduler.triggers.cron.CronTrigger", "Cron тригери"),
        ("apscheduler.triggers.interval.IntervalTrigger", "Інтервальні тригери"),
        
        # Основний додаток з автоматизацією
        ("main.AutomatedUkrainianTelegramBot", "Автоматизований бот"),
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
    
    print(f"\n📊 Результат імпортів: {success_count}/{len(tests)} пройдено")
    return success_count

def test_scheduler_dependencies():
    """Тестування залежностей планувальника"""
    print("\n⏰ ТЕСТУВАННЯ ЗАЛЕЖНОСТЕЙ ПЛАНУВАЛЬНИКА:")
    
    dependencies = [
        ("apscheduler", "APScheduler - основний планувальник"),
        ("pytz", "PyTZ - часові зони"),
        ("datetime", "DateTime - робота з часом"),
        ("asyncio", "AsyncIO - асинхронність")
    ]
    
    success_count = 0
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description} - {e}")
            if dep == "apscheduler":
                print("💡 Встановіть: pip install APScheduler>=3.10.0")
            elif dep == "pytz":
                print("💡 Встановіть: pip install pytz>=2023.3")
    
    print(f"\n📊 Залежності: {success_count}/{len(dependencies)} доступно")
    return success_count

async def test_scheduler_creation():
    """Тестування створення планувальника"""
    print("\n🤖 ТЕСТУВАННЯ СТВОРЕННЯ ПЛАНУВАЛЬНИКА:")
    
    try:
        # Mock bot для тестування
        class MockBot:
            def __init__(self):
                self.token = "test_token"
            
            async def send_message(self, chat_id, text, **kwargs):
                print(f"📤 Mock message to {chat_id}: {text[:50]}...")
                return True
        
        mock_bot = MockBot()
        
        # Тест створення планувальника
        from services.automated_scheduler import create_automated_scheduler
        
        scheduler = await create_automated_scheduler(mock_bot)
        
        if scheduler:
            print("✅ Планувальник створено успішно")
            
            # Тест статусу
            status = scheduler.get_scheduler_status()
            print(f"✅ Статус отримано: {status.get('total_jobs', 0)} завдань")
            
            # Тест ініціалізації
            if hasattr(scheduler, 'broadcast_system') and scheduler.broadcast_system:
                print("✅ Broadcast система ініціалізована")
            else:
                print("⚠️ Broadcast система не ініціалізована")
            
            return True
        else:
            print("❌ Не вдалося створити планувальник")
            return False
            
    except Exception as e:
        print(f"❌ Помилка створення планувальника: {e}")
        return False

async def test_broadcast_system():
    """Тестування системи розсилок"""
    print("\n📢 ТЕСТУВАННЯ СИСТЕМИ РОЗСИЛОК:")
    
    try:
        # Mock bot
        class MockBot:
            def __init__(self):
                self.messages_sent = []
            
            async def send_message(self, chat_id, text, **kwargs):
                self.messages_sent.append((chat_id, text))
                return True
        
        mock_bot = MockBot()
        
        # Створення broadcast системи
        from services.broadcast_system import create_broadcast_system
        
        broadcast_system = await create_broadcast_system(mock_bot)
        
        if broadcast_system:
            print("✅ Broadcast система створена")
            
            # Тест статусу
            status = broadcast_system.get_broadcast_status()
            print(f"✅ Статус broadcast: {status}")
            
            # Тест методів отримання користувачів (mock)
            try:
                # Ці методи можуть падати через відсутність БД, це нормально
                active_users = await broadcast_system.get_active_users(days=7)
                print(f"✅ Отримання активних користувачів: {len(active_users)} користувачів")
            except Exception as e:
                print(f"⚠️ Отримання користувачів (очікується без БД): {e}")
            
            return True
        else:
            print("❌ Не вдалося створити broadcast систему")
            return False
            
    except Exception as e:
        print(f"❌ Помилка тестування broadcast: {e}")
        return False

async def test_database_services():
    """Тестування сервісів БД для автоматизації"""
    print("\n💾 ТЕСТУВАННЯ СЕРВІСІВ БД:")
    
    services_to_test = [
        ("get_active_users_for_broadcast", "Активні користувачі"),
        ("get_all_users_for_broadcast", "Всі користувачі"),
        ("get_daily_best_content", "Кращий контент дня"),
        ("generate_weekly_stats", "Тижнева статистика"),
        ("get_recent_achievements", "Недавні досягнення"),
        ("get_broadcast_statistics", "Статистика розсилок"),
        ("mark_user_inactive", "Позначення неактивного користувача")
    ]
    
    success_count = 0
    
    try:
        from database import services
        
        for service_name, description in services_to_test:
            if hasattr(services, service_name):
                print(f"✅ {description} - функція доступна")
                success_count += 1
                
                # Тест виклику функції (може падати без БД)
                try:
                    func = getattr(services, service_name)
                    if service_name == "mark_user_inactive":
                        # Цей сервіс потребує параметр
                        pass  # Не викликаємо без параметрів
                    elif service_name in ["get_recent_achievements", "generate_weekly_stats"]:
                        # Ці можуть викликатися з параметрами
                        result = await func() if asyncio.iscoroutinefunction(func) else func()
                        print(f"   📊 Результат: {type(result).__name__}")
                    else:
                        # Інші сервіси
                        result = await func() if asyncio.iscoroutinefunction(func) else func()
                        print(f"   📊 Результат: {len(result) if isinstance(result, list) else type(result).__name__}")
                except Exception as e:
                    print(f"   ⚠️ Виклик функції (очікується без БД): {str(e)[:50]}...")
            else:
                print(f"❌ {description} - функція відсутня")
        
        print(f"\n📊 Сервіси БД: {success_count}/{len(services_to_test)} доступно")
        return success_count >= len(services_to_test) * 0.8  # 80% має бути
        
    except ImportError as e:
        print(f"❌ Не вдалося імпортувати сервіси БД: {e}")
        return False

async def test_main_app_integration():
    """Тестування інтеграції з основним додатком"""
    print("\n🎮 ТЕСТУВАННЯ ІНТЕГРАЦІЇ З ДОДАТКОМ:")
    
    try:
        from main import AutomatedUkrainianTelegramBot
        print("✅ Клас AutomatedUkrainianTelegramBot доступний")
        
        # Перевіряємо методи автоматизації
        bot_class = AutomatedUkrainianTelegramBot
        automation_methods = [
            'initialize_automation', 'register_automation_handlers',
            'get_rank_by_points'
        ]
        
        missing_methods = []
        for method in automation_methods:
            if not hasattr(bot_class, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"⚠️ Відсутні методи автоматизації: {missing_methods}")
        else:
            print("✅ Всі методи автоматизації присутні")
        
        # Тест створення екземпляра
        try:
            bot_instance = AutomatedUkrainianTelegramBot()
            print("✅ Екземпляр бота створено")
            
            # Перевірка початкових значень
            if hasattr(bot_instance, 'automation_active'):
                print(f"✅ Автоматизація ініціалізована: {bot_instance.automation_active}")
            
            if hasattr(bot_instance, 'scheduler'):
                print(f"✅ Планувальник: {bot_instance.scheduler is not None}")
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка створення екземпляра: {e}")
            return False
        
    except ImportError as e:
        print(f"❌ Основний додаток недоступний: {e}")
        return False

def test_configuration_files():
    """Тестування конфігураційних файлів"""
    print("\n📁 ТЕСТУВАННЯ КОНФІГУРАЦІЙНИХ ФАЙЛІВ:")
    
    required_files = [
        ("app/services/automated_scheduler.py", "Планувальник"),
        ("app/services/broadcast_system.py", "Система розсилок"),
        ("app/main.py", "Основний додаток"),
        ("requirements.txt", "Залежності"),
        ("app/database/services.py", "Сервіси БД")
    ]
    
    optional_files = [
        ("app/services/__init__.py", "Services пакет"),
        ("app/config/settings.py", "Налаштування"),
        (".env", "Змінні середовища")
    ]
    
    success_count = 0
    
    print("📋 ОБОВ'ЯЗКОВІ ФАЙЛИ:")
    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} ({description})")
            success_count += 1
        else:
            print(f"❌ {file_path} ({description}) - КРИТИЧНИЙ")
    
    print("\n📋 ОПЦІОНАЛЬНІ ФАЙЛИ:")
    for file_path, description in optional_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} ({description})")
        else:
            print(f"⚠️ {file_path} ({description}) - рекомендується")
    
    return success_count == len(required_files)

async def test_scheduler_jobs():
    """Тестування конфігурації завдань планувальника"""
    print("\n📅 ТЕСТУВАННЯ КОНФІГУРАЦІЇ ЗАВДАНЬ:")
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger
        
        # Створюємо тестовий планувальник
        test_scheduler = AsyncIOScheduler()
        
        # Тестуємо різні типи тригерів
        test_jobs = [
            ("daily_morning", CronTrigger(hour=9, minute=0), "Щоденна ранкова розсилка"),
            ("check_duels", IntervalTrigger(minutes=1), "Перевірка дуелей"),
            ("weekly_digest", CronTrigger(day_of_week=6, hour=18, minute=0), "Тижневий дайджест")
        ]
        
        success_count = 0
        for job_id, trigger, description in test_jobs:
            try:
                # Додаємо тестове завдання
                async def dummy_job():
                    pass
                
                job = test_scheduler.add_job(
                    dummy_job,
                    trigger,
                    id=job_id,
                    name=description
                )
                
                print(f"✅ {description} - тригер налаштовано")
                print(f"   ⏰ Наступний запуск: {job.next_run_time}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ {description} - помилка: {e}")
        
        print(f"\n📊 Тригери: {success_count}/{len(test_jobs)} працюють")
        
        # Очищуємо тестовий планувальник
        test_scheduler.shutdown()
        
        return success_count == len(test_jobs)
        
    except Exception as e:
        print(f"❌ Помилка тестування тригерів: {e}")
        return False

async def run_comprehensive_automation_test():
    """Запуск повного тестування автоматизації"""
    print_header()
    
    tests = [
        ("Імпорти автоматизації", test_automation_imports),
        ("Залежності планувальника", test_scheduler_dependencies),
        ("Створення планувальника", test_scheduler_creation),
        ("Система розсилок", test_broadcast_system),
        ("Сервіси БД", test_database_services),
        ("Інтеграція додатку", test_main_app_integration),
        ("Конфігураційні файли", test_configuration_files),
        ("Конфігурація завдань", test_scheduler_jobs)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n{'='*60}")
        print(f"🧪 ТЕСТ: {test_name}")
        print('='*60)
        
        try:
            if asyncio.iscoroutinefunction(test_function):
                result = await test_function()
            else:
                result = test_function()
            
            if result:
                passed_tests += 1
                print(f"✅ ТЕСТ '{test_name}' ПРОЙДЕНО")
            else:
                print(f"❌ ТЕСТ '{test_name}' НЕ ПРОЙДЕНО")
        except Exception as e:
            print(f"💥 ТЕСТ '{test_name}' ЗАВЕРШИВСЯ ПОМИЛКОЮ: {e}")
    
    # Підсумок
    print(f"\n{'🏆'*30}")
    print(f"📊 ПІДСУМОК ТЕСТУВАННЯ АВТОМАТИЗАЦІЇ")
    print(f"{'🏆'*30}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"✅ Пройдено: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ВСІ ТЕСТИ АВТОМАТИЗАЦІЇ ПРОЙШЛИ УСПІШНО!")
        print("🤖 Система автоматизації готова до роботи!")
        return True
    elif passed_tests >= total_tests * 0.8:  # 80%
        print("🔶 БІЛЬШІСТЬ ТЕСТІВ ПРОЙШЛИ!")
        print("🤖 Автоматизація готова з деякими обмеженнями")
        return True
    else:
        print("❌ ЗАНАДТО БАГАТО ПОМИЛОК!")
        print("🔧 Необхідно виправити проблеми перед запуском")
        return False

async def main():
    """Головна функція тестування"""
    try:
        success = await run_comprehensive_automation_test()
        
        if success:
            print(f"\n🚀 РЕКОМЕНДАЦІЇ ДЛЯ ЗАПУСКУ:")
            print(f"1. Встановіть залежності: pip install -r requirements.txt")
            print(f"2. Перевірте змінні середовища BOT_TOKEN, ADMIN_ID")
            print(f"3. Запустіть бота: python main.py")
            print(f"4. Перевірте автоматизацію: /automation_status")
            print(f"5. Тест ручної розсилки: /broadcast_now")
            print(f"6. Моніторте планувальник через адмін команди")
            
            print(f"\n📅 ОЧІКУВАНІ АВТОМАТИЧНІ ФУНКЦІЇ:")
            print(f"• 9:00 щодня - ранкова розсилка контенту")
            print(f"• 20:00 щодня - вечірня статистика")
            print(f"• Кожну хвилину - перевірка дуелей")
            print(f"• Кожні 15 хвилин - нагадування про дуелі")
            print(f"• П'ятниця 19:00 - тижневий турнір")
            print(f"• Неділя 18:00 - тижневий дайджест")
            print(f"• 1 число 12:00 - місячні підсумки")
            print(f"• 3:00 щодня - автоматична очистка")
            
        else:
            print(f"\n🔧 НЕОБХІДНІ ДІЇ:")
            print(f"1. Встановіть відсутні залежності:")
            print(f"   pip install APScheduler>=3.10.0 pytz>=2023.3")
            print(f"2. Перевірте структуру файлів проекту")
            print(f"3. Виправте помилки імпорту")
            print(f"4. Запустіть тест знову")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Тестування перервано користувачем")
        return False
    except Exception as e:
        print(f"\n💥 Критична помилка тестування: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)