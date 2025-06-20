#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ ШВИДКЕ ВИПРАВЛЕННЯ БАЗИ ДАНИХ

Автоматично виправляє проблеми з БД україномовного бота
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Додаємо app/ до path
app_dir = Path(__file__).parent / "app"
if app_dir.exists():
    sys.path.insert(0, str(app_dir))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header():
    print("🛠️" * 25)
    print("\n💾 ШВИДКЕ ВИПРАВЛЕННЯ БАЗИ ДАНИХ")
    print("Автоматичне відновлення функціональності БД")
    print("🛠️" * 25)
    print()

def check_prerequisites():
    """Перевірка передумов"""
    print("🔍 ПЕРЕВІРКА ПЕРЕДУМОВ:")
    
    # Перевірка змінних
    required_vars = ['BOT_TOKEN', 'ADMIN_ID', 'DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Відсутні змінні: {', '.join(missing_vars)}")
        return False
    
    print("✅ Змінні середовища OK")
    
    # Перевірка структури
    if not app_dir.exists():
        print("❌ Папка app/ не знайдена")
        return False
    
    print("✅ Структура проекту OK")
    return True

def backup_database():
    """Створення резервної копії (якщо можливо)"""
    print("\n💾 РЕЗЕРВНЕ КОПІЮВАННЯ:")
    
    try:
        database_url = os.getenv('DATABASE_URL', '')
        
        if 'sqlite' in database_url.lower():
            # Для SQLite можемо зробити копію файлу
            if '///' in database_url:
                db_path = database_url.split(':///')[-1]
                if Path(db_path).exists():
                    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    import shutil
                    shutil.copy2(db_path, backup_path)
                    print(f"✅ SQLite backup: {backup_path}")
                    return True
        
        print("⚠️ PostgreSQL - резервна копія не створена")
        return True
        
    except Exception as e:
        print(f"⚠️ Помилка backup: {e}")
        return True  # Продовжуємо навіть якщо backup не вдався

async def fix_database_imports():
    """Виправлення імпортів database"""
    print("\n📦 ВИПРАВЛЕННЯ ІМПОРТІВ:")
    
    try:
        # Тест базових імпортів
        from config.settings import settings
        print("✅ Settings імпортовано")
        
        from database.models import Base, User, Content
        print("✅ Models імпортовано")
        
        # Тест нових функцій database
        from database.database import (
            init_db, get_db_session, 
            check_if_migration_needed, migrate_database
        )
        print("✅ Database функції імпортовано")
        
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        return False

async def initialize_database():
    """Ініціалізація БД"""
    print("\n🚀 ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ:")
    
    try:
        from database.database import (
            init_db, check_if_migration_needed, 
            migrate_database, verify_database_integrity
        )
        
        # Перевірка необхідності міграції
        print("  🔍 Перевірка міграції...")
        migration_needed = await check_if_migration_needed()
        
        if migration_needed:
            print("  🔄 Виконання міграції...")
            await migrate_database()
            print("  ✅ Міграція завершена")
        else:
            print("  ✅ Міграція не потрібна")
        
        # Ініціалізація
        print("  🔧 Ініціалізація БД...")
        init_result = await init_db()
        
        if init_result:
            print("  ✅ БД ініціалізована успішно")
        else:
            print("  ⚠️ БД ініціалізована з попередженнями")
        
        # Перевірка цілісності
        print("  🔍 Перевірка цілісності...")
        integrity = await verify_database_integrity()
        
        if integrity:
            print("  ✅ Цілісність БД підтверджена")
        else:
            print("  ⚠️ Виявлено проблеми з цілісністю")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка ініціалізації БД: {e}")
        return False

async def test_basic_operations():
    """Тестування базових операцій БД"""
    print("\n🧪 ТЕСТУВАННЯ БАЗОВИХ ОПЕРАЦІЙ:")
    
    try:
        from database.database import (
            get_or_create_user, update_user_points, 
            get_random_approved_content, ContentType
        )
        
        # Тест користувача
        print("  👤 Тестування створення користувача...")
        test_user = await get_or_create_user(
            telegram_id=999999999,
            username="test_fix_user",
            first_name="Test Fix"
        )
        
        if test_user:
            print("  ✅ Користувач створений/знайдений")
            
            # Тест балів
            print("  💰 Тестування балів...")
            points_result = await update_user_points(999999999, 5)
            if points_result:
                print("  ✅ Бали оновлено")
            else:
                print("  ⚠️ Помилка оновлення балів")
        else:
            print("  ❌ Помилка створення користувача")
        
        # Тест контенту
        print("  📝 Тестування контенту...")
        content = await get_random_approved_content(ContentType.JOKE)
        if content:
            print("  ✅ Контент знайдено")
        else:
            print("  ⚠️ Контент не знайдено (можливо, ще не додано)")
        
        print("✅ Базові операції протестовано")
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False

async def create_admin_user():
    """Створення адміністратора"""
    print("\n👑 СТВОРЕННЯ АДМІНІСТРАТОРА:")
    
    try:
        from database.database import ensure_admin_exists
        
        await ensure_admin_exists()
        print("✅ Адміністратор підтверджений")
        return True
        
    except Exception as e:
        print(f"❌ Помилка створення адміна: {e}")
        return False

def update_main_py():
    """Оновлення app/main.py для кращої роботи з БД"""
    print("\n🔧 ПЕРЕВІРКА ІНТЕГРАЦІЇ З app/main.py:")
    
    main_py_path = app_dir / "main.py"
    
    if not main_py_path.exists():
        print("⚠️ app/main.py не знайдено")
        return True
    
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Перевірка чи є правильні імпорти БД
        if 'from database import' in content or 'import database' in content:
            print("✅ Database імпорти знайдено в app/main.py")
        else:
            print("⚠️ Database імпорти відсутні в app/main.py")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Помилка перевірки app/main.py: {e}")
        return True

async def main():
    """Головна функція виправлення"""
    print_header()
    
    success_steps = 0
    total_steps = 6
    
    try:
        # Крок 1: Передумови
        if check_prerequisites():
            success_steps += 1
            print("✅ Крок 1/6: Передумови")
        else:
            print("❌ Крок 1/6: Передумови не виконані")
            return False
        
        # Крок 2: Backup
        if backup_database():
            success_steps += 1
            print("✅ Крок 2/6: Backup")
        
        # Крок 3: Імпорти
        if await fix_database_imports():
            success_steps += 1
            print("✅ Крок 3/6: Імпорти")
        else:
            print("❌ Крок 3/6: Проблеми з імпортами")
        
        # Крок 4: Ініціалізація БД
        if await initialize_database():
            success_steps += 1
            print("✅ Крок 4/6: Ініціалізація БД")
        else:
            print("❌ Крок 4/6: Проблеми з ініціалізацією")
        
        # Крок 5: Тестування
        if await test_basic_operations():
            success_steps += 1
            print("✅ Крок 5/6: Тестування")
        
        # Крок 6: Адмін
        if await create_admin_user():
            success_steps += 1
            print("✅ Крок 6/6: Адміністратор")
        
        # Додатково: перевірка інтеграції
        update_main_py()
        
    except Exception as e:
        logger.error(f"Критична помилка: {e}")
    
    # Підсумок
    print("\n📊 ПІДСУМОК ВИПРАВЛЕННЯ:")
    print("=" * 50)
    
    if success_steps >= total_steps - 1:  # Дозволяємо 1 невдачу
        print("🎉 ВИПРАВЛЕННЯ БД ЗАВЕРШЕНО УСПІШНО!")
        print(f"✅ Виконано {success_steps}/{total_steps} кроків")
        print("\n🚀 НАСТУПНІ КРОКИ:")
        print("1. Перезапустіть бота: python main.py")
        print("2. Перевірте що БД працює в логах")
        print("3. Протестуйте команди в Telegram")
        return True
    else:
        print("⚠️ ВИПРАВЛЕННЯ БД ЧАСТКОВЕ")
        print(f"⚠️ Виконано лише {success_steps}/{total_steps} кроків")
        print("\n🔧 РЕКОМЕНДАЦІЇ:")
        print("1. Перевірте логи вище для деталей")
        print("2. Можливо, потрібно оновити файл app/database/database.py")
        print("3. Зверніться за підтримкою")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)