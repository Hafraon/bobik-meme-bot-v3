#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Database модуль (ВИПРАВЛЕНО enum та get_or_create_user) 🧠😂🔥
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

# Імпорт налаштувань
try:
    from config.settings import settings
except ImportError:
    import os
    class Settings:
        BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        POINTS_FOR_APPROVAL = 20
        POINTS_FOR_SUBMISSION = 10
    settings = Settings()

# Імпорт моделей БД
try:
    from .models import (
        Base, User, Content, Rating, Duel, DuelVote, 
        AdminAction, BotStatistics, ContentType, ContentStatus
    )
    MODELS_LOADED = True
except ImportError:
    try:
        from database.models import (
            Base, User, Content, Rating, Duel, DuelVote, 
            AdminAction, BotStatistics, ContentType, ContentStatus
        )
        MODELS_LOADED = True
    except ImportError:
        MODELS_LOADED = False
        logger.error("❌ Не вдалося імпортувати моделі БД")

# ===== НАЛАШТУВАННЯ БД =====
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """Контекстний менеджер для сесії БД"""
    session = SessionLocal()
    try:
        yield session
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
            return
        
        # Створення таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблиці БД створено/оновлено")
        
        # Перевірка адміністратора
        await ensure_admin_exists()
        
        # Додавання початкових даних
        await add_initial_data()
        
        logger.info("✅ База даних повністю ініціалізована!")
        
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації БД: {e}")

# ===== ФУНКЦІЇ КОРИСТУВАЧІВ =====

async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None, **kwargs) -> Optional[User]:
    """Отримати або створити користувача - ВИПРАВЛЕНО"""
    try:
        if not MODELS_LOADED:
            logger.warning("⚠️ Моделі не завантажені")
            return None
            
        with get_db_session() as session:
            # Знайти існуючого користувача
            user = session.query(User).filter(User.id == telegram_id).first()
            
            if user:
                # Оновити дані існуючого користувача
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
                
                user.last_active = datetime.utcnow()
                session.commit()
                session.refresh(user)
                
                logger.debug(f"✅ Користувач {telegram_id} оновлено")
                return user
            
            # Створити нового користувача
            new_user = User(
                id=telegram_id,  # У моделі це primary key
                username=username,
                first_name=first_name,
                last_name=last_name,
                points=0,
                rank="🤡 Новачок",
                daily_subscription=False,
                language_code="uk",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                **kwargs
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            logger.info(f"✅ Створено нового користувача: {telegram_id} (@{username})")
            return new_user
            
    except Exception as e:
        logger.error(f"❌ Помилка створення/оновлення користувача {telegram_id}: {e}")
        return None

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Отримати користувача за ID"""
    try:
        if not MODELS_LOADED:
            return None
            
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_active = datetime.utcnow()
                session.commit()
                session.refresh(user)
            return user
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
        return None

async def update_user_points(user_id: int, points: int, reason: str = "activity") -> Optional[Dict[str, Any]]:
    """Оновити бали користувача"""
    try:
        if not MODELS_LOADED:
            return None
            
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"⚠️ Користувач {user_id} не знайдений для оновлення балів")
                return None
            
            old_points = user.points
            user.points = max(0, user.points + points)
            user.last_active = datetime.utcnow()
            
            # Оновлення рангу
            user.rank = get_rank_by_points(user.points)
            
            session.commit()
            session.refresh(user)
            
            logger.info(f"💰 Користувач {user_id}: {old_points} → {user.points} (+{points}) за {reason}")
            
            return {
                "user_id": user_id,
                "old_points": old_points,
                "added_points": points,
                "total_points": user.points,
                "new_rank": user.rank,
                "reason": reason
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення балів {user_id}: {e}")
        return None

def get_rank_by_points(points: int) -> str:
    """Визначити ранг за кількістю балів"""
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

# ===== ФУНКЦІЇ КОНТЕНТУ =====

async def add_content_for_moderation(author_id: int, content_text: str, content_type: str = "JOKE") -> Optional[Content]:
    """Додати контент на модерацію - ВИПРАВЛЕНО enum"""
    try:
        if not MODELS_LOADED:
            return None
            
        with get_db_session() as session:
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильні enum значення
            if content_type.upper() == "JOKE":
                content_type_enum = ContentType.JOKE
            elif content_type.upper() == "MEME":
                content_type_enum = ContentType.MEME
            else:
                content_type_enum = ContentType.JOKE
            
            new_content = Content(
                content_type=content_type_enum,
                text=content_text,
                author_id=author_id,
                status=ContentStatus.PENDING,  # ✅ ВИПРАВЛЕНО: використовуємо PENDING
                created_at=datetime.utcnow()
            )
            
            session.add(new_content)
            session.commit()
            session.refresh(new_content)
            
            logger.info(f"✅ Контент додано на модерацію: {new_content.id} від користувача {author_id}")
            return new_content
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту: {e}")
        return None

async def get_pending_content() -> List[Content]:
    """Отримати контент на модерації - ВИПРАВЛЕНО enum"""
    try:
        if not MODELS_LOADED:
            return []
            
        with get_db_session() as session:
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильне enum значення
            content_list = session.query(Content).filter(
                Content.status == ContentStatus.PENDING  # ✅ ВИПРАВЛЕНО
            ).order_by(Content.created_at.asc()).all()
            
            return content_list
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту на модерації: {e}")
        return []

async def moderate_content(content_id: int, action: str, moderator_id: int, comment: str = None) -> bool:
    """Модерувати контент - ВИПРАВЛЕНО enum"""
    try:
        if not MODELS_LOADED:
            return False
            
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            if not content:
                return False
            
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильні enum значення
            if action.upper() == "APPROVE":
                content.status = ContentStatus.APPROVED  # ✅ ВИПРАВЛЕНО
                # Нарахування балів автору
                await update_user_points(content.author_id, settings.POINTS_FOR_APPROVAL, "схвалення контенту")
            elif action.upper() == "REJECT":
                content.status = ContentStatus.REJECTED  # ✅ ВИПРАВЛЕНО
            else:
                return False
            
            content.moderator_id = moderator_id
            content.moderation_comment = comment
            content.moderated_at = datetime.utcnow()
            
            session.commit()
            
            logger.info(f"✅ Контент {content_id} {action.lower()}ed модератором {moderator_id}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка модерації контенту {content_id}: {e}")
        return False

async def get_random_approved_content(content_type: str = None, user_id: int = None) -> Optional[Content]:
    """Отримати випадковий схвалений контент - ВИПРАВЛЕНО enum"""
    try:
        if not MODELS_LOADED:
            return None
            
        with get_db_session() as session:
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильне enum значення
            query = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED  # ✅ ВИПРАВЛЕНО
            )
            
            # Фільтр по типу контенту
            if content_type:
                if content_type.upper() == "JOKE":
                    query = query.filter(Content.content_type == ContentType.JOKE)
                elif content_type.upper() == "MEME":
                    query = query.filter(Content.content_type == ContentType.MEME)
            
            # Отримати всі результати
            content_list = query.all()
            
            if not content_list:
                logger.warning(f"❌ Немає схваленого контенту типу {content_type}")
                return None
            
            # Випадковий вибір
            content = random.choice(content_list)
            
            # Оновити статистику перегляду
            content.views += 1
            content.last_shown_at = datetime.utcnow()
            session.commit()
            
            return content
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання випадкового контенту: {e}")
        return None

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def check_if_migration_needed() -> bool:
    """Перевірити чи потрібна міграція БД"""
    try:
        if not MODELS_LOADED:
            return False
            
        with get_db_session() as session:
            # Перевірка чи існують таблиці з правильною структурою
            try:
                # Перевірка enum значень
                result = session.execute(text("SELECT 1 FROM content WHERE status = 'APPROVED' LIMIT 1"))
                return False  # Міграція не потрібна
            except Exception:
                return True  # Потрібна міграція
                
    except Exception as e:
        logger.error(f"❌ Помилка перевірки міграції: {e}")
        return True

async def migrate_database():
    """Виконати міграцію БД"""
    try:
        if not MODELS_LOADED:
            logger.warning("⚠️ Моделі не завантажені, пропускаю міграцію")
            return
            
        logger.info("🔄 Починаю міграцію БД...")
        
        with engine.begin() as conn:
            # Видалення старих таблиць
            tables = ['duel_votes', 'admin_actions', 'bot_statistics', 'ratings', 'duels', 'content', 'users']
            for table in tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    logger.info(f"🗑️ Видалено таблицю: {table}")
                except Exception:
                    pass
            
            # Видалення старих enum типів
            enum_types = ['contentstatus', 'contenttype', 'duelstatus']
            for enum_type in enum_types:
                try:
                    conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))
                except Exception:
                    pass
        
        # Створення нових таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Міграція завершена")
        
    except Exception as e:
        logger.error(f"❌ Помилка міграції: {e}")
        raise

async def verify_database_integrity() -> bool:
    """Перевірити цілісність БД"""
    try:
        if not MODELS_LOADED:
            return False
            
        with get_db_session() as session:
            # Перевірка основних таблиць
            session.execute(text("SELECT 1 FROM users LIMIT 1"))
            session.execute(text("SELECT 1 FROM content LIMIT 1"))
            
            logger.info("✅ Цілісність БД підтверджена")
            return True
            
    except Exception as e:
        logger.warning(f"⚠️ Проблеми з цілісністю БД: {e}")
        return False

async def ensure_admin_exists():
    """Переконатися що адміністратор існує в БД"""
    try:
        if not MODELS_LOADED or not settings.ADMIN_ID:
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
    """Додати початкові дані"""
    try:
        if not MODELS_LOADED:
            return
            
        # Додати приклади контенту
        sample_jokes = [
            "Що робить програміст коли не може заснути? Рахує овець у циклі while!",
            "Чому програмісти люблять темний режим? Тому що світло приваблює жуків!",
            "Що сказав HTML CSS? Без тебе я нічого не значу!"
        ]
        
        with get_db_session() as session:
            # Перевірити чи є контент
            existing_content = session.query(Content).first()
            if existing_content:
                return  # Дані вже є
            
            # Додати зразки
            for joke in sample_jokes:
                content = Content(
                    content_type=ContentType.JOKE,
                    text=joke,
                    author_id=settings.ADMIN_ID,
                    status=ContentStatus.APPROVED,
                    created_at=datetime.utcnow(),
                    moderated_at=datetime.utcnow(),
                    moderator_id=settings.ADMIN_ID
                )
                session.add(content)
            
            session.commit()
            logger.info("✅ Додано початковий контент")
            
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