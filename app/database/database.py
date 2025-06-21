#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 ПОВНІСТЮ ВИПРАВЛЕНА БАЗА ДАНИХ - POSTGRESQL СУМІСНА 💾

ВИПРАВЛЕННЯ:
✅ Правильне підключення до PostgreSQL Railway
✅ Fallback функції для роботи без БД
✅ Виправлені enum'и для PostgreSQL
✅ Правильна обробка User моделі
✅ Детальне логування процесу підключення
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager
import os

# SQLAlchemy імпорти
try:
    from sqlalchemy import create_engine, text, MetaData
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Глобальні змінні для БД
engine = None
SessionLocal = None
DATABASE_AVAILABLE = False

# ===== БЕЗПЕЧНИЙ ІМПОРТ НАЛАШТУВАНЬ =====
def get_database_url() -> str:
    """Отримання DATABASE_URL з різних джерел"""
    # 1. Прямо з environment
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info("✅ DATABASE_URL отримано з environment")
        return database_url
    
    # 2. З config.settings
    try:
        from config.settings import DATABASE_URL as settings_url
        if settings_url:
            logger.info("✅ DATABASE_URL отримано з config.settings")
            return settings_url
    except ImportError:
        pass
    
    # 3. Fallback
    logger.warning("⚠️ DATABASE_URL не знайдено, використовую fallback")
    return "sqlite:///fallback.db"

def get_admin_id() -> int:
    """Отримання ADMIN_ID"""
    try:
        from config.settings import ADMIN_ID
        return ADMIN_ID
    except ImportError:
        return int(os.getenv("ADMIN_ID", 603047391))

# ===== БЕЗПЕЧНИЙ ІМПОРТ МОДЕЛЕЙ =====
try:
    from .models import Base, User, Content, Duel, DuelVote, Rating
    MODELS_LOADED = True
    logger.info("✅ Моделі БД імпортовано успішно")
except ImportError as e:
    MODELS_LOADED = False
    logger.warning(f"⚠️ Моделі БД не імпортовано: {e}")

# ===== ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ =====
async def init_db() -> bool:
    """
    Ініціалізація бази даних з детальною діагностикою
    
    Returns:
        bool: True якщо БД успішно ініціалізована
    """
    global engine, SessionLocal, DATABASE_AVAILABLE
    
    logger.info("💾 Початок ініціалізації бази даних...")
    
    # Перевірка наявності SQLAlchemy
    if not SQLALCHEMY_AVAILABLE:
        logger.error("❌ SQLAlchemy не встановлено!")
        return False
    
    # Перевірка моделей
    if not MODELS_LOADED:
        logger.warning("⚠️ Моделі БД не завантажені, працюємо без БД")
        return False
    
    try:
        # Отримання DATABASE_URL
        database_url = get_database_url()
        logger.info(f"🔗 DATABASE_URL: {database_url[:30]}...{database_url[-10:]}")
        
        # Створення engine з правильними налаштуваннями для PostgreSQL
        if database_url.startswith('postgresql'):
            # PostgreSQL налаштування
            engine = create_engine(
                database_url,
                echo=False,  # Вимкнути SQL логування
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                pool_pre_ping=True,  # Перевірка з'єднання
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "ukrainian_telegram_bot"
                }
            )
            logger.info("🐘 PostgreSQL engine створено")
        else:
            # SQLite fallback
            engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True
            )
            logger.info("📁 SQLite engine створено")
        
        # Створення SessionLocal
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("✅ Session factory створено")
        
        # Перевірка підключення
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_row = result.fetchone()
            if test_row and test_row[0] == 1:
                logger.info("✅ Тест підключення пройшов успішно")
            else:
                logger.error("❌ Тест підключення не пройшов")
                return False
        
        # Створення таблиць
        logger.info("🔨 Створення таблиць БД...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблиці створено/оновлено")
        
        # Перевірка що таблиці створились
        metadata = MetaData()
        metadata.reflect(bind=engine)
        tables = list(metadata.tables.keys())
        logger.info(f"📋 Знайдено таблиць: {len(tables)} - {tables}")
        
        # Створення початкових даних
        await ensure_admin_exists()
        await add_sample_content()
        
        DATABASE_AVAILABLE = True
        logger.info("🎉 База даних повністю ініціалізована!")
        return True
        
    except OperationalError as e:
        logger.error(f"❌ Помилка підключення до БД: {e}")
        DATABASE_AVAILABLE = False
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Помилка SQLAlchemy: {e}")
        DATABASE_AVAILABLE = False
        return False
    except Exception as e:
        logger.error(f"❌ Неочікувана помилка ініціалізації БД: {e}")
        logger.error(f"Тип помилки: {type(e).__name__}")
        DATABASE_AVAILABLE = False
        return False

@contextmanager
def get_db_session():
    """Контекстний менеджер для роботи з сесією БД"""
    if not DATABASE_AVAILABLE or not SessionLocal:
        raise Exception("База даних недоступна")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Помилка БД сесії: {e}")
        raise
    finally:
        session.close()

def is_database_available() -> bool:
    """Перевірка доступності БД"""
    return DATABASE_AVAILABLE

# ===== ФУНКЦІЇ КОРИСТУВАЧІВ =====
async def get_or_create_user(telegram_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None) -> Optional[User]:
    """Отримати або створити користувача"""
    if not DATABASE_AVAILABLE:
        logger.warning("⚠️ БД недоступна для get_or_create_user")
        return None
        
    try:
        with get_db_session() as session:
            # Шукаємо користувача за telegram_id
            user = session.query(User).filter(User.id == telegram_id).first()
            
            if user:
                # Оновлюємо дані існуючого користувача
                updated = False
                if username and user.username != username:
                    user.username = username
                    updated = True
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                
                if updated:
                    user.updated_at = datetime.utcnow()
                    logger.info(f"🔄 Оновлено користувача: {telegram_id}")
                
                return user
            else:
                # Створюємо нового користувача
                new_user = User(
                    id=telegram_id,  # Використовуємо telegram_id як primary key
                    username=username,
                    first_name=first_name or "Користувач",
                    last_name=last_name,
                    points=0,
                    rank="Новачок",
                    total_content_submitted=0,
                    total_content_approved=0,
                    total_duels_won=0,
                    total_duels_participated=0,
                    is_admin=(telegram_id == get_admin_id()),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(new_user)
                session.flush()  # Щоб отримати ID
                
                logger.info(f"➕ Створено нового користувача: {telegram_id} (@{username})")
                return new_user
                
    except Exception as e:
        logger.error(f"❌ Помилка get_or_create_user: {e}")
        return None

async def get_user_by_id(telegram_id: int) -> Optional[User]:
    """Отримати користувача за ID"""
    if not DATABASE_AVAILABLE:
        return None
        
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.id == telegram_id).first()
            return user
    except Exception as e:
        logger.error(f"❌ Помилка get_user_by_id: {e}")
        return None

async def update_user_points(telegram_id: int, points: int) -> bool:
    """Оновити бали користувача"""
    if not DATABASE_AVAILABLE:
        return False
        
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.id == telegram_id).first()
            if user:
                user.points += points
                user.updated_at = datetime.utcnow()
                
                # Оновлюємо ранг на основі балів
                if user.points >= 1000:
                    user.rank = "Майстер Гумору"
                elif user.points >= 500:
                    user.rank = "Жартівник"
                elif user.points >= 100:
                    user.rank = "Весельчак"
                elif user.points >= 50:
                    user.rank = "Початківець"
                else:
                    user.rank = "Новачок"
                
                logger.info(f"📈 Користувач {telegram_id} отримав {points} балів (загалом: {user.points})")
                return True
            return False
    except Exception as e:
        logger.error(f"❌ Помилка update_user_points: {e}")
        return False

async def get_top_users(limit: int = 10) -> List[User]:
    """Отримати топ користувачів за балами"""
    if not DATABASE_AVAILABLE:
        return []
        
    try:
        with get_db_session() as session:
            users = session.query(User)\
                          .filter(User.is_active == True)\
                          .order_by(User.points.desc())\
                          .limit(limit)\
                          .all()
            return users
    except Exception as e:
        logger.error(f"❌ Помилка get_top_users: {e}")
        return []

# ===== ФУНКЦІЇ КОНТЕНТУ =====
async def add_content(user_id: int, content_type: str, text: str) -> Optional[Content]:
    """Додати контент від користувача"""
    if not DATABASE_AVAILABLE:
        return None
        
    try:
        with get_db_session() as session:
            new_content = Content(
                user_id=user_id,
                content_type=content_type,  # "meme" або "anekdot"
                text=text,
                status="pending",  # String замість enum для PostgreSQL
                created_at=datetime.utcnow()
            )
            
            session.add(new_content)
            session.flush()
            
            logger.info(f"📝 Додано контент від користувача {user_id}")
            return new_content
    except Exception as e:
        logger.error(f"❌ Помилка add_content: {e}")
        return None

async def get_random_content(content_type: str) -> Optional[Content]:
    """Отримати випадковий контент"""
    if not DATABASE_AVAILABLE:
        return None
        
    try:
        with get_db_session() as session:
            content = session.query(Content)\
                           .filter(Content.content_type == content_type,
                                  Content.status == "approved")\
                           .order_by(text("RANDOM()"))\
                           .first()
            return content
    except Exception as e:
        logger.error(f"❌ Помилка get_random_content: {e}")
        return None

# ===== ПОЧАТКОВІ ДАНІ =====
async def ensure_admin_exists():
    """Переконатися що адміністратор існує в БД"""
    if not DATABASE_AVAILABLE:
        return
    
    admin_id = get_admin_id()
    logger.info(f"👑 Перевірка адміністратора: {admin_id}")
    
    admin = await get_or_create_user(
        telegram_id=admin_id,
        username="admin", 
        first_name="Адміністратор"
    )
    
    if admin:
        logger.info("✅ Адміністратор підтверджений в БД")
    else:
        logger.warning("⚠️ Не вдалося створити адміністратора")

async def add_sample_content():
    """Додати початковий контент якщо БД порожня"""
    if not DATABASE_AVAILABLE:
        return
        
    try:
        with get_db_session() as session:
            # Перевіряємо чи є контент
            content_count = session.query(Content).count()
            
            if content_count == 0:
                logger.info("📚 Додаю початковий контент...")
                
                sample_memes = [
                    "Програміст дружині: — Я дізнався що ти мене зраджуєш! — Як?! — git log",
                    "Чому програмісти плутають Хеллоуїн і Різдво? Тому що 31 OCT = 25 DEC!",
                    "Скільки програмістів потрібно щоб закрутити лампочку? Жодного. Це апаратна проблема!"
                ]
                
                sample_anekdots = [
                    "Дружина програмісту: — Йди в магазин, купи хліб. А якщо будуть яйця — візьми десяток. Програміст повертається з десятьма хлібами.",
                    "— Скільки коштує ваш сайт? — 300 доларів. — А якщо без JavaScript? — Тоді 50 доларів. — А якщо тільки HTML? — Тоді це вже не сайт, а візитка!",
                    "Дітей вчать що 2+2=4. Програмістів вчать що 2+2=5 для великих значень 2."
                ]
                
                admin_id = get_admin_id()
                
                # Додаємо меми
                for text in sample_memes:
                    content = Content(
                        user_id=admin_id,
                        content_type="meme",
                        text=text,
                        status="approved",
                        created_at=datetime.utcnow()
                    )
                    session.add(content)
                
                # Додаємо анекдоти
                for text in sample_anekdots:
                    content = Content(
                        user_id=admin_id,
                        content_type="anekdot", 
                        text=text,
                        status="approved",
                        created_at=datetime.utcnow()
                    )
                    session.add(content)
                
                session.commit()
                logger.info("✅ Початковий контент додано")
            else:
                logger.info(f"📚 Контент вже є: {content_count} записів")
                
    except Exception as e:
        logger.error(f"❌ Помилка add_sample_content: {e}")

# ===== СТАТИСТИКА =====
async def get_database_stats() -> Dict[str, Any]:
    """Отримати статистику БД"""
    if not DATABASE_AVAILABLE:
        return {"error": "База даних недоступна"}
    
    try:
        with get_db_session() as session:
            stats = {
                "users_total": session.query(User).count(),
                "users_active": session.query(User).filter(User.is_active == True).count(),
                "content_total": session.query(Content).count(),
                "content_approved": session.query(Content).filter(Content.status == "approved").count(),
                "content_pending": session.query(Content).filter(Content.status == "pending").count(),
            }
            
            # Додаємо статистику дуелей якщо таблиця існує
            try:
                stats["duels_total"] = session.query(Duel).count()
                stats["duels_active"] = session.query(Duel).filter(Duel.status == "active").count()
            except:
                stats["duels_total"] = 0
                stats["duels_active"] = 0
            
            return stats
    except Exception as e:
        logger.error(f"❌ Помилка get_database_stats: {e}")
        return {"error": str(e)}

# ===== ДІАГНОСТИКА =====
async def test_database_connection() -> bool:
    """Тестування підключення до БД"""
    try:
        if not DATABASE_AVAILABLE:
            logger.warning("⚠️ БД позначена як недоступна")
            return False
        
        with get_db_session() as session:
            result = session.execute(text("SELECT 1 as test"))
            test_row = result.fetchone()
            if test_row and test_row[0] == 1:
                logger.info("✅ Тест підключення БД успішний")
                return True
            else:
                logger.error("❌ Тест підключення БД неуспішний")
                return False
                
    except Exception as e:
        logger.error(f"❌ Помилка тесту підключення: {e}")
        return False

# ===== ЕКСПОРТ =====
__all__ = [
    'init_db', 'get_db_session', 'is_database_available',
    'get_or_create_user', 'get_user_by_id', 'update_user_points', 'get_top_users',
    'add_content', 'get_random_content',
    'get_database_stats', 'test_database_connection'
]

logger.info("💾 Database модуль завантажено з PostgreSQL підтримкою")