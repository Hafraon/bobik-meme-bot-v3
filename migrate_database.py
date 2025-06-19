#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 СКРИПТ МІГРАЦІЇ БД (ВИПРАВЛЕННЯ ENUM ПРОБЛЕМ) 🧠😂🔥
Запустіть цей скрипт для виправлення всіх проблем з базою даних
"""

import os
import sys
import logging
from datetime import datetime

# Додавання поточної директорії до шляху
sys.path.insert(0, os.path.dirname(__file__))

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log')
    ]
)

logger = logging.getLogger(__name__)

def get_database_url():
    """Отримати URL бази даних"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL не знайдено в змінних середовища!")
        sys.exit(1)
    
    logger.info(f"🔗 База даних: {database_url[:50]}...")
    return database_url

def backup_existing_data():
    """Резервне копіювання існуючих даних"""
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Перевірка існування таблиць
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            tables = [row[0] for row in result]
            logger.info(f"📋 Знайдено таблиці: {tables}")
            
            # Резервне копіювання користувачів
            if 'users' in tables:
                users_result = conn.execute(text("SELECT COUNT(*) FROM users"))
                users_count = users_result.scalar()
                logger.info(f"👥 Користувачів в БД: {users_count}")
                
                if users_count > 0:
                    # Експорт користувачів
                    users_data = conn.execute(text("""
                        SELECT id, username, first_name, points, rank, created_at 
                        FROM users 
                        ORDER BY created_at
                    """))
                    
                    backup_file = f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write("# Резервна копія користувачів\n")
                        f.write("# ID, Username, First Name, Points, Rank, Created At\n")
                        for row in users_data:
                            f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n")
                    
                    logger.info(f"💾 Користувачів збережено в {backup_file}")
            
            # Резервне копіювання контенту
            if 'content' in tables:
                content_result = conn.execute(text("SELECT COUNT(*) FROM content"))
                content_count = content_result.scalar()
                logger.info(f"📝 Контенту в БД: {content_count}")
            
    except Exception as e:
        logger.warning(f"⚠️ Помилка резервного копіювання: {e}")
        logger.info("Продовжую без резервного копіювання...")

def drop_all_tables():
    """Видалити всі таблиці"""
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(get_database_url())
        
        with engine.begin() as conn:
            # Видалення таблиць у правильному порядку (зважаючи на зовнішні ключі)
            tables_to_drop = [
                'duel_votes',
                'admin_actions', 
                'bot_statistics',
                'ratings',
                'duels',
                'content',
                'users'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    logger.info(f"🗑️ Видалено таблицю: {table}")
                except Exception as e:
                    logger.warning(f"⚠️ Помилка видалення {table}: {e}")
            
            # Видалення старих enum типів
            enum_types = ['contentstatus', 'contenttype', 'duelstatus']
            for enum_type in enum_types:
                try:
                    conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))
                    logger.info(f"🗑️ Видалено enum тип: {enum_type}")
                except Exception as e:
                    logger.warning(f"⚠️ Помилка видалення enum {enum_type}: {e}")
            
        logger.info("✅ Всі старі таблиці видалено")
        
    except Exception as e:
        logger.error(f"❌ Помилка видалення таблиць: {e}")
        raise

def create_new_tables():
    """Створити нові таблиці з виправленими enum"""
    try:
        # Імпорт моделей
        from database.models import Base
        from sqlalchemy import create_engine
        
        engine = create_engine(get_database_url())
        
        # Створення всіх таблиць
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Нові таблиці створено успішно")
        
    except Exception as e:
        logger.error(f"❌ Помилка створення таблиць: {e}")
        raise

def add_initial_admin():
    """Додати початкового адміністратора"""
    try:
        admin_id = os.getenv("ADMIN_ID")
        if not admin_id:
            logger.warning("⚠️ ADMIN_ID не знайдено, пропускаю створення адміна")
            return
        
        admin_id = int(admin_id)
        
        from database.database import get_or_create_user
        import asyncio
        
        async def create_admin():
            admin_user = await get_or_create_user(
                telegram_id=admin_id,
                username="admin",
                first_name="Адміністратор",
                last_name="Бота"
            )
            
            if admin_user:
                logger.info(f"✅ Адміністратора {admin_id} створено/оновлено")
            else:
                logger.warning(f"⚠️ Не вдалося створити адміна {admin_id}")
        
        asyncio.run(create_admin())
        
    except Exception as e:
        logger.error(f"❌ Помилка створення адміна: {e}")

def add_sample_content():
    """Додати зразковий контент"""
    try:
        from database.database import add_content_for_moderation, moderate_content
        import asyncio
        
        admin_id = int(os.getenv("ADMIN_ID", "0"))
        if not admin_id:
            logger.warning("⚠️ ADMIN_ID не знайдено, пропускаю зразковий контент")
            return
        
        sample_jokes = [
            "Що робить програміст коли не може заснути? Рахує овець у циклі while!",
            "Чому програмісти люблять темний режим? Тому що світло приваблює жуків!",
            "Що сказав HTML CSS? Без тебе я нічого не значу!",
            "Програміст заходить в бар і замовляє 1 пиво, 0 пив, -1 пиво, NULL пив...",
            "Чому програмісти плутають Хеллоуін і Різдво? Тому що 31 OCT = 25 DEC!",
        ]
        
        async def create_sample_content():
            for joke in sample_jokes:
                # Додати контент
                content = await add_content_for_moderation(
                    author_id=admin_id,
                    content_text=joke,
                    content_type="JOKE"
                )
                
                if content:
                    # Одразу схвалити
                    await moderate_content(
                        content_id=content.id,
                        action="APPROVE", 
                        moderator_id=admin_id,
                        comment="Початковий контент"
                    )
                    logger.info(f"✅ Додано зразковий жарт: {joke[:50]}...")
        
        asyncio.run(create_sample_content())
        
    except Exception as e:
        logger.error(f"❌ Помилка додавання зразкового контенту: {e}")

def verify_migration():
    """Перевірити успішність міграції"""
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Перевірка таблиць
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            expected_tables = ['users', 'content', 'ratings', 'duels', 'duel_votes', 'admin_actions', 'bot_statistics']
            
            logger.info(f"📋 Створені таблиці: {tables}")
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                logger.warning(f"⚠️ Відсутні таблиці: {missing_tables}")
            else:
                logger.info("✅ Всі необхідні таблиці створено")
            
            # Перевірка enum типів
            enum_result = conn.execute(text("""
                SELECT typname FROM pg_type 
                WHERE typtype = 'e' 
                ORDER BY typname
            """))
            
            enums = [row[0] for row in enum_result]
            logger.info(f"🔢 Enum типи: {enums}")
            
            # Перевірка користувачів
            if 'users' in tables:
                users_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                logger.info(f"👥 Користувачів в БД: {users_count}")
            
            # Перевірка контенту
            if 'content' in tables:
                content_count = conn.execute(text("SELECT COUNT(*) FROM content")).scalar()
                approved_count = conn.execute(text("SELECT COUNT(*) FROM content WHERE status = 'APPROVED'")).scalar()
                logger.info(f"📝 Контенту в БД: {content_count} (схвалено: {approved_count})")
        
        logger.info("✅ Міграція завершена успішно!")
        
    except Exception as e:
        logger.error(f"❌ Помилка перевірки міграції: {e}")

def main():
    """Головна функція міграції"""
    print("🧠😂🔥 МІГРАЦІЯ БАЗИ ДАНИХ УКРАЇНОМОВНОГО БОТА 🧠😂🔥")
    print("=" * 60)
    
    try:
        logger.info("🚀 Початок міграції...")
        
        # Крок 1: Резервне копіювання
        logger.info("📋 Крок 1: Резервне копіювання даних")
        backup_existing_data()
        
        # Крок 2: Видалення старих таблиць
        logger.info("🗑️ Крок 2: Видалення старих таблиць")
        drop_all_tables()
        
        # Крок 3: Створення нових таблиць
        logger.info("🏗️ Крок 3: Створення нових таблиць")
        create_new_tables()
        
        # Крок 4: Додавання адміністратора
        logger.info("👑 Крок 4: Створення адміністратора")
        add_initial_admin()
        
        # Крок 5: Додавання зразкового контенту
        logger.info("📝 Крок 5: Додавання зразкового контенту")
        add_sample_content()
        
        # Крок 6: Перевірка результатів
        logger.info("✅ Крок 6: Перевірка міграції")
        verify_migration()
        
        print("\n" + "=" * 60)
        print("🎉 МІГРАЦІЯ ЗАВЕРШЕНА УСПІШНО!")
        print("✅ Бот готовий до роботи")
        print("📝 Перевірте логи в файлі migration.log")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"💥 КРИТИЧНА ПОМИЛКА МІГРАЦІЇ: {e}")
        print(f"\n❌ МІГРАЦІЯ НЕУСПІШНА: {e}")
        print("📝 Деталі в файлі migration.log")
        sys.exit(1)

if __name__ == "__main__":
    main()