#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ЕКСТРЕНА МІГРАЦІЯ БД (ВИПРАВЛЕННЯ КОЛОНОК) 🧠😂🔥
Цей скрипт виправляє проблему з відсутніми колонками
"""

import os
import sys
import logging
from datetime import datetime

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def get_database_url():
    """Отримати URL бази даних"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL не знайдено!")
        sys.exit(1)
    
    logger.info(f"🔗 Підключення до БД: {database_url.split('@')[0]}@***")
    return database_url

def emergency_migration():
    """Екстрена міграція БД"""
    try:
        from sqlalchemy import create_engine, text
        
        logger.info("🚀 Початок екстреної міграції...")
        
        engine = create_engine(get_database_url())
        
        with engine.begin() as conn:
            logger.info("🗑️ Видалення старих таблиць...")
            
            # Видалення в правильному порядку (зважаючи на FK)
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
                    logger.info(f"   ✅ Видалено: {table}")
                except Exception as e:
                    logger.warning(f"   ⚠️ {table}: {e}")
            
            # Видалення старих enum типів
            logger.info("🗑️ Видалення старих enum типів...")
            enum_types = ['contentstatus', 'contenttype', 'duelstatus']
            
            for enum_type in enum_types:
                try:
                    conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))
                    logger.info(f"   ✅ Видалено enum: {enum_type}")
                except Exception as e:
                    logger.warning(f"   ⚠️ {enum_type}: {e}")
        
        logger.info("✅ Старі структури видалено")
        
        # Створення нових таблиць
        logger.info("🏗️ Створення нових таблиць...")
        
        # Імпорт моделей та створення таблиць
        sys.path.insert(0, os.path.dirname(__file__))
        
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Нові таблиці створено")
        
        # Перевірка результату
        with engine.connect() as conn:
            # Перевірка структури users
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            
            columns = [(row[0], row[1]) for row in result]
            logger.info(f"📋 Колонки users: {[col[0] for col in columns]}")
            
            # Перевірка що points колонка існує
            if any(col[0] == 'points' for col in columns):
                logger.info("✅ Колонка 'points' створена успішно")
            else:
                logger.error("❌ Колонка 'points' відсутня!")
                return False
        
        # Додавання початкових даних
        logger.info("📝 Додавання початкових даних...")
        
        admin_id = os.getenv("ADMIN_ID")
        if admin_id:
            admin_id = int(admin_id)
            
            with engine.begin() as conn:
                # Створення адміністратора
                conn.execute(text("""
                    INSERT INTO users (id, username, first_name, points, rank, created_at, updated_at, last_active)
                    VALUES (:id, 'admin', 'Адміністратор', 0, '🤡 Новачок', NOW(), NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING
                """), {"id": admin_id})
                
                logger.info(f"✅ Адміністратор {admin_id} додано")
                
                # Додавання зразкових жартів
                sample_jokes = [
                    "Що робить програміст коли не може заснути? Рахує овець у циклі while!",
                    "Чому програмісти люблять темний режим? Тому що світло приваблює жуків!",
                    "Що сказав HTML CSS? Без тебе я нічого не значу!",
                    "Програміст заходить в бар і замовляє 1 пиво, 0 пив, -1 пиво, NULL пив...",
                    "Чому програмісти плутають Хеллоуін і Різдво? Тому що 31 OCT = 25 DEC!"
                ]
                
                for i, joke in enumerate(sample_jokes, 1):
                    conn.execute(text("""
                        INSERT INTO content (content_type, text, author_id, status, created_at, moderated_at, moderator_id)
                        VALUES ('JOKE', :text, :author_id, 'APPROVED', NOW(), NOW(), :moderator_id)
                    """), {
                        "text": joke,
                        "author_id": admin_id,
                        "moderator_id": admin_id
                    })
                
                logger.info(f"✅ Додано {len(sample_jokes)} зразкових жартів")
        
        logger.info("🎉 ЕКСТРЕНА МІГРАЦІЯ ЗАВЕРШЕНА УСПІШНО!")
        logger.info("✅ БД готова до роботи")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 КРИТИЧНА ПОМИЛКА МІГРАЦІЇ: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def verify_migration():
    """Перевірити результат міграції"""
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Підрахунок користувачів
            users_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            logger.info(f"👥 Користувачів в БД: {users_count}")
            
            # Підрахунок контенту
            content_count = conn.execute(text("SELECT COUNT(*) FROM content")).scalar()
            approved_count = conn.execute(text("SELECT COUNT(*) FROM content WHERE status = 'APPROVED'")).scalar()
            logger.info(f"📝 Контенту: {content_count} (схвалено: {approved_count})")
            
            # Перевірка колонки points
            result = conn.execute(text("SELECT points FROM users LIMIT 1"))
            logger.info("✅ Колонка 'points' працює")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка перевірки: {e}")
        return False

def main():
    """Головна функція"""
    print("🧠😂🔥 ЕКСТРЕНА МІГРАЦІЯ БД 🧠😂🔥")
    print("=" * 50)
    
    try:
        # Міграція
        if emergency_migration():
            # Перевірка
            if verify_migration():
                print("\n🎉 МІГРАЦІЯ УСПІШНА!")
                print("✅ Бот готовий до роботи")
                print("📝 Перевірте бота командою /start")
            else:
                print("\n⚠️ Міграція завершена з попередженнями")
        else:
            print("\n❌ МІГРАЦІЯ НЕУСПІШНА")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 КРИТИЧНА ПОМИЛКА: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()