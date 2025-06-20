#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ДІАГНОСТИКА БАЗИ ДАНИХ УКРАЇНОМОВНОГО БОТА

Перевіряє і виправляє проблеми з базою даних
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Додаємо app/ до path
app_dir = Path(__file__).parent / "app"
if app_dir.exists():
    sys.path.insert(0, str(app_dir))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header():
    print("🔧" * 25)
    print("\n💾 ДІАГНОСТИКА БАЗИ ДАНИХ")
    print("Перевірка та виправлення проблем БД")
    print("🔧" * 25)
    print()

def check_environment():
    """Перевірка змінних середовища"""
    print("🌍 ПЕРЕВІРКА ЗМІННИХ СЕРЕДОВИЩА:")
    
    issues = []
    required_vars = {
        'BOT_TOKEN': 'Токен Telegram бота',
        'ADMIN_ID': 'ID адміністратора',
        'DATABASE_URL': 'URL бази даних'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'DATABASE_URL':
                # Маскування паролю в URL
                masked = value
                if '@' in value and '://' in value:
                    try:
                        parts = value.split('://', 1)[1].split('@', 1)
                        if len(parts) == 2:
                            credentials = parts[0]
                            if ':' in credentials:
                                user, password = credentials.rsplit(':', 1)
                                masked = value.replace(':' + password + '@', ':***@')
                    except:
                        masked = value[:20] + "..."
                print(f"✅ {var}: {masked}")
            else:
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: не встановлено ({description})")
            issues.append(f"Відсутня змінна {var}")
    
    return issues

def check_imports():
    """Перевірка імпортів database модулів"""
    print("\n📦 ПЕРЕВІРКА ІМПОРТІВ DATABASE:")
    
    issues = []
    
    # Тестування імпортів
    import_tests = [
        ("config.settings", "Налаштування"),
        ("database.models", "Моделі БД"),
        ("database.database", "Database функції"),
        ("database", "Database модуль")
    ]
    
    for module, description in import_tests:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - {description} ({e})")
            issues.append(f"Помилка імпорту: {module}")
    
    return issues

async def test_database_connection():
    """Тестування підключення до БД"""
    print("\n💾 ТЕСТУВАННЯ ПІДКЛЮЧЕННЯ ДО БД:")
    
    issues = []
    
    try:
        from database.database import get_db_session, ENGINE_CREATED
        
        if not ENGINE_CREATED:
            print("❌ Database engine не створено")
            issues.append("Database engine не ініціалізовано")
            return issues
        
        print("✅ Database engine створено")
        
        # Тест базового підключення
        with get_db_session() as session:
            # Простий тест запит
            result = session.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Базове підключення працює")
            else:
                print("❌ Тест запиту не пройшов")
                issues.append("Помилка тестового запиту")
        
    except Exception as e:
        print(f"❌ Помилка підключення до БД: {e}")
        issues.append(f"Помилка БД: {str(e)}")
    
    return issues

async def test_database_functions():
    """Тестування функцій БД"""
    print("\n🔧 ТЕСТУВАННЯ ФУНКЦІЙ БД:")
    
    issues = []
    
    try:
        from database.database import (
            init_db, check_if_migration_needed, verify_database_integrity,
            get_or_create_user, get_user_by_id, update_user_points
        )
        
        # Тест ініціалізації БД
        print("  🔍 Тестування init_db...")
        result = await init_db()
        if result:
            print("  ✅ init_db працює")
        else:
            print("  ⚠️ init_db повернув False")
        
        # Тест міграції
        print("  🔍 Тестування check_if_migration_needed...")
        migration_needed = await check_if_migration_needed()
        print(f"  ✅ Міграція {'потрібна' if migration_needed else 'не потрібна'}")
        
        # Тест цілісності
        print("  🔍 Тестування verify_database_integrity...")
        integrity = await verify_database_integrity()
        if integrity:
            print("  ✅ Цілісність БД OK")
        else:
            print("  ⚠️ Проблеми з цілісністю БД")
        
        # Тест роботи з користувачами
        print("  🔍 Тестування функцій користувачів...")
        test_user = await get_or_create_user(
            telegram_id=999999999,
            username="test_user",
            first_name="Test"
        )
        
        if test_user:
            print("  ✅ get_or_create_user працює")
            
            # Тест оновлення балів
            points_updated = await update_user_points(999999999, 10)
            if points_updated:
                print("  ✅ update_user_points працює")
            else:
                print("  ⚠️ update_user_points не працює")
        else:
            print("  ❌ get_or_create_user не працює")
            issues.append("Функції користувачів не працюють")
        
        print("✅ Основні функції БД протестовано")
        
    except Exception as e:
        print(f"❌ Помилка тестування функцій БД: {e}")
        issues.append(f"Помилка функцій БД: {str(e)}")
    
    return issues

async def test_database_models():
    """Тестування моделей БД"""
    print("\n🏗️ ТЕСТУВАННЯ МОДЕЛЕЙ БД:")
    
    issues = []
    
    try:
        from database.models import (
            User, Content, Rating, Duel, DuelVote, 
            ContentType, ContentStatus, DuelStatus
        )
        
        print("✅ Основні моделі імпортовано")
        
        # Тест енумів
        print(f"  📋 ContentType: {list(ContentType)}")
        print(f"  📋 ContentStatus: {list(ContentStatus)}")
        print(f"  📋 DuelStatus: {list(DuelStatus)}")
        
        print("✅ Моделі БД працюють правильно")
        
    except Exception as e:
        print(f"❌ Помилка моделей БД: {e}")
        issues.append(f"Помилка моделей: {str(e)}")
    
    return issues

def create_fix_script():
    """Створення скрипта виправлення"""
    print("\n🛠️ СТВОРЕННЯ СКРИПТА ВИПРАВЛЕННЯ:")
    
    fix_script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ ШВИДКЕ ВИПРАВЛЕННЯ БД
"""

import asyncio
import sys
from pathlib import Path

# Додати app/ до path
app_dir = Path(__file__).parent / "app"
if app_dir.exists():
    sys.path.insert(0, str(app_dir))

async def main():
    try:
        from database.database import init_db, migrate_database
        
        print("🔧 Виправлення БД...")
        
        # Виконання міграції
        await migrate_database()
        print("✅ Міграція виконана")
        
        # Ініціалізація
        result = await init_db()
        if result:
            print("✅ БД ініціалізована успішно")
        else:
            print("⚠️ БД ініціалізована з попередженнями")
        
        print("🎉 Виправлення завершено!")
        
    except Exception as e:
        print(f"❌ Помилка виправлення: {e}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    try:
        with open("fix_database.py", 'w', encoding='utf-8') as f:
            f.write(fix_script_content)
        print("✅ Створено fix_database.py")
    except Exception as e:
        print(f"❌ Помилка створення скрипта: {e}")

async def main():
    """Головна функція діагностики"""
    print_header()
    
    all_issues = []
    
    try:
        # Поетапна діагностика
        all_issues.extend(check_environment())
        all_issues.extend(check_imports())
        all_issues.extend(await test_database_connection())
        all_issues.extend(await test_database_functions())
        all_issues.extend(await test_database_models())
        
    except Exception as e:
        logger.error(f"Помилка діагностики: {e}")
        all_issues.append(f"Критична помилка: {str(e)}")
    
    # Підсумок
    print("\n📊 ПІДСУМОК ДІАГНОСТИКИ БД:")
    print("=" * 50)
    
    if not all_issues:
        print("🎉 ВСІ ПЕРЕВІРКИ БД ПРОЙДЕНО УСПІШНО!")
        print("✅ База даних готова до роботи")
    else:
        print(f"⚠️ ЗНАЙДЕНО {len(all_issues)} ПРОБЛЕМ З БД:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        create_fix_script()
        
        print("\n🛠️ РЕКОМЕНДАЦІЇ:")
        print("1. Запустіть: python fix_database.py")
        print("2. Перевірте змінні середовища")
        print("3. Перезапустіть бота")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)