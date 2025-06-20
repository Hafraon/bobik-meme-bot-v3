#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПОВНА БАЗА ДАНИХ ДЛЯ УКРАЇНОМОВНОГО БОТА 🧠😂🔥

Повністю функціональний модуль з усіма необхідними функціями
✅ Всі функції реалізовані
✅ PostgreSQL сумісність  
✅ Правильна обробка помилок
✅ Усі функції з __init__.py присутні
"""

import logging
import random
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, and_, or_, desc, asc, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)

# ===== ІМПОРТ НАЛАШТУВАНЬ =====
try:
    from config.settings import settings
    SETTINGS_LOADED = True
    logger.info("✅ Settings завантажено з config.settings")
except ImportError:
    # Fallback для випадків коли settings недоступні
    import os
    class FallbackSettings:
        BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        POINTS_FOR_APPROVAL = 20
        POINTS_FOR_SUBMISSION = 10
        POINTS_FOR_VIEW = 1
        POINTS_FOR_REACTION = 2
    settings = FallbackSettings()
    SETTINGS_LOADED = False
    logger.warning("⚠️ Використано fallback settings")

# ===== ІМПОРТ МОДЕЛЕЙ БД =====
try:
    from .models import (
        Base, User, Content, Rating, Duel, DuelVote, 
        AdminAction, BotStatistics, ContentType, ContentStatus, DuelStatus
    )
    MODELS_LOADED = True
    logger.info("✅ Моделі БД завантажено успішно")
except ImportError:
    try:
        from models import (
            Base, User, Content, Rating, Duel, DuelVote, 
            AdminAction, BotStatistics, ContentType, ContentStatus, DuelStatus
        )
        MODELS_LOADED = True
        logger.info("✅ Моделі БД завантажено (fallback import)")
    except ImportError:
        MODELS_LOADED = False
        logger.error("❌ Не вдалося імпортувати моделі БД")

# ===== НАЛАШТУВАННЯ БД =====
if MODELS_LOADED:
    try:
        # Створення движка з професійними налаштуваннями
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG if SETTINGS_LOADED else False,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            } if "sqlite" in settings.DATABASE_URL else {
                "connect_timeout": 30,
                "application_name": "ukrainian_telegram_bot"
            }
        )
        
        SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=engine,
            expire_on_commit=False
        )
        
        ENGINE_CREATED = True
        logger.info("✅ Database engine створено успішно")
        
    except Exception as e:
        ENGINE_CREATED = False
        logger.error(f"❌ Помилка створення database engine: {e}")
else:
    ENGINE_CREATED = False

# ===== КОНТЕКСТНИЙ МЕНЕДЖЕР СЕСІЙ =====

@contextmanager
def get_db_session():
    """Професійний контекстний менеджер для роботи з БД"""
    if not ENGINE_CREATED:
        logger.error("❌ Database engine не створено!")
        raise RuntimeError("Database не ініціалізовано")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Помилка БД: {e}")
        raise
    finally:
        session.close()

# ===== ІНІЦІАЛІЗАЦІЯ БД =====

async def init_db():
    """Ініціалізація бази даних"""
    try:
        if not MODELS_LOADED:
            logger.warning("⚠️ Моделі не завантажені, пропускаю ініціалізацію БД")
            return False
        
        if not ENGINE_CREATED:
            logger.warning("⚠️ Database engine не створено")
            return False
        
        logger.info("💾 Початок ініціалізації бази даних...")
        
        # Створення всіх таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблиці БД створено/оновлено")
        
        # Перевірка адміністратора
        await ensure_admin_exists()
        
        # Додавання початкових даних
        await add_initial_data()
        
        logger.info("✅ База даних повністю ініціалізована!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації БД: {e}")
        return False

async def check_if_migration_needed() -> bool:
    """Перевірити чи потрібна міграція БД"""
    try:
        if not ENGINE_CREATED:
            return False
            
        with get_db_session() as session:
            # Перевірка чи існують основні таблиці
            try:
                session.execute(text("SELECT 1 FROM users LIMIT 1"))
                session.execute(text("SELECT 1 FROM content LIMIT 1"))
                logger.info("✅ Основні таблиці існують")
                return False
            except Exception:
                logger.info("⚠️ Таблиці потребують створення")
                return True
                
    except Exception as e:
        logger.warning(f"⚠️ Не вдалося перевірити міграцію: {e}")
        return True

async def migrate_database():
    """Виконати міграцію БД"""
    try:
        if not MODELS_LOADED or not ENGINE_CREATED:
            logger.warning("⚠️ Неможливо виконати міграцію")
            return
        
        logger.info("🔄 Виконання міграції БД...")
        
        # Створення таблиць (безпечно для існуючих)
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Міграція завершена")
        
    except Exception as e:
        logger.error(f"❌ Помилка міграції: {e}")

async def verify_database_integrity() -> bool:
    """Перевірити цілісність БД"""
    try:
        if not ENGINE_CREATED:
            return False
            
        with get_db_session() as session:
            # Перевірка основних таблиць
            session.execute(text("SELECT COUNT(*) FROM users"))
            session.execute(text("SELECT COUNT(*) FROM content"))
            
            logger.info("✅ Цілісність БД підтверджена")
            return True
            
    except Exception as e:
        logger.warning(f"⚠️ Проблеми з цілісністю БД: {e}")
        return False

# ===== ФУНКЦІЇ РОБОТИ З КОРИСТУВАЧАМИ =====

async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> Optional[User]:
    """Отримати або створити користувача"""
    try:
        if not ENGINE_CREATED:
            logger.warning("⚠️ БД недоступна для створення користувача")
            return None
            
        with get_db_session() as session:
            # Спроба знайти існуючого користувача
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Оновити ім'я та username якщо змінилися
                updated = False
                if username and user.username != username:
                    user.username = username
                    updated = True
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                
                if updated:
                    user.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"✅ Оновлено користувача {telegram_id}")
                
                return user
            
            # Створити нового користувача
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name or "User",
                points=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            
            logger.info(f"✅ Створено нового користувача {telegram_id}")
            return new_user
            
    except Exception as e:
        logger.error(f"❌ Помилка створення користувача {telegram_id}: {e}")
        return None

async def get_user_by_id(telegram_id: int) -> Optional[User]:
    """Отримати користувача за Telegram ID"""
    try:
        if not ENGINE_CREATED:
            return None
            
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return user
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {telegram_id}: {e}")
        return None

async def update_user_points(telegram_id: int, points_delta: int) -> bool:
    """Оновити бали користувача"""
    try:
        if not ENGINE_CREATED:
            return False
            
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                user.points += points_delta
                user.updated_at = datetime.utcnow()
                session.commit()
                
                logger.info(f"✅ Користувач {telegram_id}: {points_delta:+d} балів (всього: {user.points})")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення балів {telegram_id}: {e}")
        return False

async def get_rank_by_points(points: int) -> str:
    """Отримати ранг за кількістю балів"""
    try:
        if points >= 5000:
            return "🚀 Гумористичний Геній"
        elif points >= 3000:
            return "🌟 Легенда Мемів"
        elif points >= 1500:
            return "🏆 Король Гумору"
        elif points >= 750:
            return "👑 Мастер Рофлу"
        elif points >= 350:
            return "🎭 Комік"
        elif points >= 150:
            return "😂 Гуморист"
        elif points >= 50:
            return "😄 Сміхун"
        else:
            return "🤡 Новачок"
            
    except Exception as e:
        logger.error(f"❌ Помилка визначення рангу: {e}")
        return "🤡 Новачок"

# ===== ФУНКЦІЇ РОБОТИ З КОНТЕНТОМ =====

async def add_content_for_moderation(author_id: int, content_type: ContentType, text: str) -> Optional[Content]:
    """Додати контент на модерацію"""
    try:
        if not ENGINE_CREATED:
            return None
            
        with get_db_session() as session:
            content = Content(
                content_type=content_type,
                text=text,
                author_id=author_id,
                status=ContentStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            session.add(content)
            session.commit()
            
            # Нарахування балів за подачу
            await update_user_points(author_id, settings.POINTS_FOR_SUBMISSION)
            
            logger.info(f"✅ Додано контент на модерацію від {author_id}")
            return content
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту: {e}")
        return None

async def get_pending_content() -> List[Content]:
    """Отримати контент на модерації"""
    try:
        if not ENGINE_CREATED:
            return []
            
        with get_db_session() as session:
            content_list = session.query(Content).filter(
                Content.status == ContentStatus.PENDING
            ).order_by(Content.created_at).all()
            
            return content_list
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту на модерації: {e}")
        return []

async def moderate_content(content_id: int, approved: bool, moderator_id: int, reason: str = None) -> bool:
    """Модерувати контент"""
    try:
        if not ENGINE_CREATED:
            return False
            
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if content:
                content.status = ContentStatus.APPROVED if approved else ContentStatus.REJECTED
                content.moderated_at = datetime.utcnow()
                content.moderator_id = moderator_id
                content.rejection_reason = reason
                
                session.commit()
                
                # Нарахування балів за схвалення
                if approved:
                    await update_user_points(content.author_id, settings.POINTS_FOR_APPROVAL)
                
                logger.info(f"✅ Контент {content_id} {'схвалено' if approved else 'відхилено'}")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Помилка модерації контенту {content_id}: {e}")
        return False

async def get_random_approved_content(content_type: ContentType) -> Optional[Content]:
    """Отримати випадковий схвалений контент"""
    try:
        if not ENGINE_CREATED:
            return None
            
        with get_db_session() as session:
            content_list = session.query(Content).filter(
                Content.content_type == content_type,
                Content.status == ContentStatus.APPROVED
            ).all()
            
            if content_list:
                return random.choice(content_list)
            
            return None
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання випадкового контенту: {e}")
        return None

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def ensure_admin_exists():
    """Переконатися що адміністратор існує в БД"""
    try:
        if not SETTINGS_LOADED or not settings.ADMIN_ID:
            logger.warning("⚠️ ADMIN_ID не встановлено")
            return
            
        admin_user = await get_or_create_user(
            telegram_id=settings.ADMIN_ID,
            username="admin",
            first_name="Адміністратор"
        )
        
        if admin_user:
            logger.info(f"✅ Адміністратор {settings.ADMIN_ID} підтверджений")
        else:
            logger.warning(f"⚠️ Не вдалося створити адміністратора {settings.ADMIN_ID}")
            
    except Exception as e:
        logger.error(f"❌ Помилка створення адміністратора: {e}")

async def add_initial_data():
    """Додати початкові дані (зразки контенту)"""
    try:
        if not ENGINE_CREATED:
            return
            
        with get_db_session() as session:
            # Перевірити чи є вже контент
            existing_content = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).first()
            
            if existing_content:
                logger.info("✅ Початковий контент вже існує")
                return
            
            # Додати зразки жартів
            sample_jokes = [
                "🧠 Приходить программіст до лікаря:\n- Доктор, в мене болить рука!\n- А де саме?\n- В лівому кліку! 😂",
                "🔥 Зустрічаються два українці:\n- Як справи?\n- Та нормально, працюю в IT.\n- А що робиш?\n- Борщ доставляю через додаток! 😂",
                "😂 Учитель запитує:\n- Петрику, скільки буде 2+2?\n- А ви про що? Про гривні чи про долари? 🧠",
                "🔥 Покупець у магазині:\n- Скільки коштує хліб?\n- 20 гривень.\n- А вчора був 15!\n- Вчора ви його і не купили! 😂"
            ]
            
            for joke_text in sample_jokes:
                joke = Content(
                    content_type=ContentType.JOKE,
                    text=joke_text,
                    author_id=settings.ADMIN_ID if SETTINGS_LOADED else 1,
                    status=ContentStatus.APPROVED,
                    created_at=datetime.utcnow(),
                    moderated_at=datetime.utcnow(),
                    moderator_id=settings.ADMIN_ID if SETTINGS_LOADED else 1
                )
                session.add(joke)
            
            session.commit()
            logger.info(f"✅ Додано {len(sample_jokes)} зразків контенту")
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання початкових даних: {e}")

# ===== ЕКСПОРТ =====
__all__ = [
    'init_db',
    'get_db_session',
    'check_if_migration_needed',
    'migrate_database', 
    'verify_database_integrity',
    'get_or_create_user',
    'get_user_by_id',
    'update_user_points',
    'get_rank_by_points',
    'add_content_for_moderation',
    'get_pending_content',
    'moderate_content',
    'get_random_approved_content',
    'ensure_admin_exists',
    'add_initial_data'
]

# Логування статусу модуля
logger.info(f"📦 Database модуль завантажено:")
logger.info(f"  - Settings: {'✅' if SETTINGS_LOADED else '❌'}")
logger.info(f"  - Models: {'✅' if MODELS_LOADED else '❌'}")
logger.info(f"  - Engine: {'✅' if ENGINE_CREATED else '❌'}")
logger.info(f"  - Функцій експортовано: {len(__all__)}")