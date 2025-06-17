#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Міграційний скрипт для всіх покращень 🧠😂🔥
"""

import logging
import asyncio
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, text, Column, Integer, BigInteger, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker

from config.settings import settings

logger = logging.getLogger(__name__)

def get_migration_session():
    """Створити сесію для міграції"""
    engine = create_engine(
        settings.DATABASE_URL,
        echo=True if settings.DEBUG else False,  # Показуємо SQL в debug режимі
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal(), engine

async def run_migration():
    """Головна функція міграції"""
    logger.info("🚀 Починаємо міграцію бази даних...")
    
    session, engine = get_migration_session()
    
    try:
        # Перевіряємо які таблиці вже існують
        existing_tables = await check_existing_tables(session)
        logger.info(f"📋 Існуючі таблиці: {existing_tables}")
        
        # Додаємо нові колонки до існуючих таблиць
        await migrate_users_table(session)
        await migrate_content_table(session)
        await migrate_ratings_table(session)
        
        # Створюємо нові таблиці
        if 'content_views' not in existing_tables:
            await create_content_views_table(session)
        
        if 'user_preferences' not in existing_tables:
            await create_user_preferences_table(session)
        
        if 'content_popularity' not in existing_tables:
            await create_content_popularity_table(session)
        
        # Оновлюємо існуючі дані
        await update_existing_content_data(session)
        await add_sample_enhanced_content(session)
        
        session.commit()
        logger.info("✅ Міграція завершена успішно!")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Помилка міграції: {e}")
        raise
    finally:
        session.close()

async def check_existing_tables(session) -> list:
    """Перевірити які таблиці вже існують"""
    try:
        if "postgresql" in settings.DATABASE_URL:
            result = session.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
        else:  # SQLite
            result = session.execute(text("""
                SELECT name FROM sqlite_master WHERE type='table'
            """))
        
        tables = [row[0] for row in result.fetchall()]
        return tables
        
    except Exception as e:
        logger.error(f"Помилка перевірки таблиць: {e}")
        return []

async def migrate_users_table(session):
    """Додати нові колонки до таблиці users"""
    logger.info("🔄 Міграція таблиці users...")
    
    new_columns = [
        ("preferred_content_type", "VARCHAR(20) DEFAULT 'mixed'"),
        ("reset_history_days", "INTEGER DEFAULT 7"),
        ("last_history_reset", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for column_name, column_def in new_columns:
        try:
            await add_column_if_not_exists(session, "users", column_name, column_def)
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося додати колонку {column_name}: {e}")

async def migrate_content_table(session):
    """Додати нові колонки до таблиці content"""
    logger.info("🔄 Міграція таблиці content...")
    
    new_columns = [
        ("topic", "VARCHAR(100)"),
        ("style", "VARCHAR(100)"), 
        ("difficulty", "INTEGER DEFAULT 1"),
        ("unique_views", "INTEGER DEFAULT 0"),
        ("shares", "INTEGER DEFAULT 0"),
        ("popularity_score", "FLOAT DEFAULT 0.0"),
        ("trending_score", "FLOAT DEFAULT 0.0"), 
        ("quality_score", "FLOAT DEFAULT 0.8"),
        ("last_shown", "TIMESTAMP")
    ]
    
    for column_name, column_def in new_columns:
        try:
            await add_column_if_not_exists(session, "content", column_name, column_def)
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося додати колонку {column_name}: {e}")

async def migrate_ratings_table(session):
    """Додати нові колонки до таблиці ratings"""
    logger.info("🔄 Міграція таблиці ratings...")
    
    new_columns = [
        ("reaction_time", "FLOAT"),
        ("comment", "TEXT"),
        ("emotion_detected", "VARCHAR(50)")
    ]
    
    for column_name, column_def in new_columns:
        try:
            await add_column_if_not_exists(session, "ratings", column_name, column_def)
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося додати колонку {column_name}: {e}")

async def add_column_if_not_exists(session, table_name: str, column_name: str, column_def: str):
    """Додати колонку якщо вона не існує"""
    try:
        # Перевіряємо чи існує колонка
        if "postgresql" in settings.DATABASE_URL:
            check_sql = text(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = '{column_name}'
            """)
        else:  # SQLite
            check_sql = text(f"PRAGMA table_info({table_name})")
        
        result = session.execute(check_sql)
        
        if "postgresql" in settings.DATABASE_URL:
            existing_columns = [row[0] for row in result.fetchall()]
        else:
            existing_columns = [row[1] for row in result.fetchall()]
        
        if column_name not in existing_columns:
            alter_sql = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            session.execute(alter_sql)
            logger.info(f"✅ Додано колонку {column_name} до {table_name}")
        else:
            logger.info(f"⏭️ Колонка {column_name} вже існує в {table_name}")
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання колонки {column_name}: {e}")
        raise

async def create_content_views_table(session):
    """Створити таблицю content_views"""
    logger.info("🆕 Створення таблиці content_views...")
    
    try:
        if "postgresql" in settings.DATABASE_URL:
            create_sql = text("""
                CREATE TABLE content_views (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id),
                    content_id INTEGER NOT NULL REFERENCES content(id),
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_duration INTEGER,
                    device_type VARCHAR(50),
                    source VARCHAR(50) DEFAULT 'random',
                    session_id VARCHAR(100)
                )
            """)
            
            index_sql = text("""
                CREATE INDEX idx_user_content_date ON content_views(user_id, content_id, viewed_at)
            """)
        else:  # SQLite
            create_sql = text("""
                CREATE TABLE content_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    content_id INTEGER NOT NULL,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_duration INTEGER,
                    device_type VARCHAR(50),
                    source VARCHAR(50) DEFAULT 'random',
                    session_id VARCHAR(100),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (content_id) REFERENCES content(id)
                )
            """)
            
            index_sql = text("""
                CREATE INDEX idx_user_content_date ON content_views(user_id, content_id, viewed_at)
            """)
        
        session.execute(create_sql)
        session.execute(index_sql)
        logger.info("✅ Таблиця content_views створена")
    except Exception as e:
        logger.error(f"❌ Помилка створення content_views: {e}")
        raise

async def create_user_preferences_table(session):
    """Створити таблицю user_preferences"""
    logger.info("🆕 Створення таблиці user_preferences...")
    
    try:
        if "postgresql" in settings.DATABASE_URL:
            create_sql = text("""
                CREATE TABLE user_preferences (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id),
                    preference_type VARCHAR(50) NOT NULL,
                    preference_value VARCHAR(100) NOT NULL,
                    weight FLOAT DEFAULT 1.0,
                    source VARCHAR(50) DEFAULT 'implicit',
                    confidence FLOAT DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, preference_type, preference_value)
                )
            """)
        else:  # SQLite
            create_sql = text("""
                CREATE TABLE user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    preference_type VARCHAR(50) NOT NULL,
                    preference_value VARCHAR(100) NOT NULL,
                    weight FLOAT DEFAULT 1.0,
                    source VARCHAR(50) DEFAULT 'implicit',
                    confidence FLOAT DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, preference_type, preference_value)
                )
            """)
        
        session.execute(create_sql)
        logger.info("✅ Таблиця user_preferences створена")
    except Exception as e:
        logger.error(f"❌ Помилка створення user_preferences: {e}")
        raise

async def create_content_popularity_table(session):
    """Створити таблицю content_popularity"""
    logger.info("🆕 Створення таблиці content_popularity...")
    
    try:
        if "postgresql" in settings.DATABASE_URL:
            create_sql = text("""
                CREATE TABLE content_popularity (
                    id SERIAL PRIMARY KEY,
                    content_id INTEGER NOT NULL REFERENCES content(id),
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    period_type VARCHAR(20) DEFAULT 'daily',
                    views_count INTEGER DEFAULT 0,
                    unique_views_count INTEGER DEFAULT 0,
                    likes_count INTEGER DEFAULT 0,
                    dislikes_count INTEGER DEFAULT 0,
                    shares_count INTEGER DEFAULT 0,
                    engagement_rate FLOAT DEFAULT 0.0,
                    satisfaction_rate FLOAT DEFAULT 0.0,
                    virality_score FLOAT DEFAULT 0.0
                )
            """)
        else:  # SQLite
            create_sql = text("""
                CREATE TABLE content_popularity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    period_type VARCHAR(20) DEFAULT 'daily',
                    views_count INTEGER DEFAULT 0,
                    unique_views_count INTEGER DEFAULT 0,
                    likes_count INTEGER DEFAULT 0,
                    dislikes_count INTEGER DEFAULT 0,
                    shares_count INTEGER DEFAULT 0,
                    engagement_rate FLOAT DEFAULT 0.0,
                    satisfaction_rate FLOAT DEFAULT 0.0,
                    virality_score FLOAT DEFAULT 0.0,
                    FOREIGN KEY (content_id) REFERENCES content(id)
                )
            """)
        
        session.execute(create_sql)
        logger.info("✅ Таблиця content_popularity створена")
    except Exception as e:
        logger.error(f"❌ Помилка створення content_popularity: {e}")
        raise

async def update_existing_content_data(session):
    """Оновити існуючий контент новими даними"""
    logger.info("🔄 Оновлення існуючих даних...")
    
    try:
        # Оновлюємо користувачів
        session.execute(text("""
            UPDATE users 
            SET preferred_content_type = 'mixed',
                reset_history_days = 7,
                last_history_reset = CURRENT_TIMESTAMP
            WHERE preferred_content_type IS NULL OR preferred_content_type = ''
        """))
        
        # Оновлюємо контент
        session.execute(text("""
            UPDATE content 
            SET popularity_score = 0.5,
                quality_score = 0.8,
                difficulty = 1,
                unique_views = views
            WHERE popularity_score IS NULL OR popularity_score = 0
        """))
        
        # Призначаємо тематики для існуючого контенту
        content_mappings = [
            (['програміст', 'код', 'async', 'GitHub', 'компілюється', 'компютер', 'IT'], 'programming', 'irony'),
            (['зарплат', 'офіс', 'робот', 'поверх', 'співбесід', 'роботодавець'], 'work', 'sarcasm'),
            (['дружина', 'чоловік', 'мама', 'батьк', 'син', 'дочка', "сім'я"], 'family', 'kind'),
            (['лікар', 'аптек', 'хворий', 'пацієнт', 'таблетк'], 'life', 'sarcasm'),
            (['студент', 'екзамен', 'університет', 'навчання', 'вчитель'], 'education', 'irony')
        ]
        
        for keywords, topic, style in content_mappings:
            for keyword in keywords:
                session.execute(text(f"""
                    UPDATE content 
                    SET topic = '{topic}', style = '{style}'
                    WHERE text LIKE '%{keyword}%' AND (topic IS NULL OR topic = '')
                """))
        
        # Для контенту без тематики
        session.execute(text("""
            UPDATE content 
            SET topic = 'life', style = 'irony'
            WHERE topic IS NULL OR topic = ''
        """))
        
        logger.info("✅ Існуючі дані оновлено")
        
    except Exception as e:
        logger.error(f"❌ Помилка оновлення даних: {e}")
        raise

async def add_sample_enhanced_content(session):
    """Додати новий розширений контент"""
    logger.info("🆕 Додавання нового контенту...")
    
    try:
        # Перевіряємо чи є вже багато контенту
        count_result = session.execute(text("SELECT COUNT(*) FROM content WHERE status = 'approved'"))
        existing_count = count_result.scalar()
        
        if existing_count >= 15:  # Якщо вже є 15+ елементів, не додаємо нових
            logger.info(f"⏭️ Контенту достатньо ({existing_count}), пропускаємо додавання")
            return
        
        # Додаємо нові анекдоти з категоризацією
        new_jokes = [
            {
                "text": "🧠 Звертається клієнт до програміста:\n- Чому програма так повільно працює?\n- А ви SSD встановили?\n- Так.\n- Ну то швидко знайдете нового програміста! 😂",
                "topic": "programming",
                "style": "sarcasm",
                "difficulty": 2
            },
            {
                "text": "🔥 Українець на співбесіді:\n- Ваші слабкі сторони?\n- Чесність.\n- Не думаю, що чесність - це слабка сторона.\n- А мені насрати, що ви думаєте! 😂",
                "topic": "work",
                "style": "absurd",
                "difficulty": 2
            },
            {
                "text": "😂 Дзвонить чоловік дружині:\n- Люба, я сьогодні пізно.\n- Що сталося?\n- Грають Динамо.\n- А хто виграє?\n- Моя совість! 🧠",
                "topic": "family",
                "style": "irony",
                "difficulty": 2
            },
            {
                "text": "🔥 Викладач студентам:\n- Хто може назвати п'ять тварин Африки?\n- Слон і чотири мавпи! 😂",
                "topic": "education",
                "style": "absurd",
                "difficulty": 1
            },
            {
                "text": "🧠 DevOps інженер прийшов до психолога:\n- Доктор, мені здається, що всі проблеми в продакшені - це моя вина.\n- Не переживайте, це не здається! 😂🔥",
                "topic": "programming",
                "style": "sarcasm",
                "difficulty": 3
            }
        ]
        
        for joke_data in new_jokes:
            session.execute(text("""
                INSERT INTO content 
                (content_type, text, topic, style, difficulty, status, author_id, views, likes, popularity_score, quality_score, created_at)
                VALUES 
                ('joke', :text, :topic, :style, :difficulty, 'approved', :admin_id, 0, 0, 0.5, 0.9, CURRENT_TIMESTAMP)
            """), {
                'text': joke_data['text'],
                'topic': joke_data['topic'],
                'style': joke_data['style'],
                'difficulty': joke_data['difficulty'],
                'admin_id': settings.ADMIN_ID
            })
        
        # Додаємо нові меми
        new_memes = [
            {
                "text": "🧠 Коли GitHub знову лежить, а deadline завтра 😱",
                "topic": "programming",
                "style": "absurd"
            },
            {
                "text": "😂 Мій код: працює на моєму комп'ютері ✅",
                "topic": "programming", 
                "style": "irony"
            },
            {
                "text": "🔥 Коли PM каже 'швидкий фікс' 💀",
                "topic": "work",
                "style": "sarcasm"
            }
        ]
        
        for meme_data in new_memes:
            session.execute(text("""
                INSERT INTO content 
                (content_type, text, topic, style, difficulty, status, author_id, views, likes, popularity_score, quality_score, created_at)
                VALUES 
                ('meme', :text, :topic, :style, 1, 'approved', :admin_id, 0, 0, 0.5, 0.9, CURRENT_TIMESTAMP)
            """), {
                'text': meme_data['text'],
                'topic': meme_data['topic'],
                'style': meme_data['style'],
                'admin_id': settings.ADMIN_ID
            })
        
        logger.info(f"✅ Додано {len(new_jokes)} нових анекдотів та {len(new_memes)} мемів")
        
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту: {e}")
        raise

# Функція для запуску міграції
async def main():
    """Головна функція"""
    try:
        await run_migration()
        print("🎉 Міграція завершена успішно!")
    except Exception as e:
        print(f"💥 Помилка міграції: {e}")
        raise

if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())