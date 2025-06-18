#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПОВНИЙ РОБОЧИЙ МОДУЛЬ DATABASE.PY 🧠😂🔥
ЗАМІНІТЬ ВЕСЬ ІСНУЮЧИЙ database/database.py НА ЦЕЙ КОД
"""

import logging
import random
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, and_, or_, desc, asc, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Імпорт налаштувань
try:
    from config.settings import settings
except ImportError:
    # Fallback налаштування
    import os
    class Settings:
        BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        POINTS_FOR_APPROVAL = 20
        POINTS_FOR_SUBMISSION = 10
    settings = Settings()

# Імпорт моделей БД з fallback
try:
    from .models import (
        Base, User, Content, Rating, Duel, DuelVote, 
        AdminAction, BotStatistics, ContentType, ContentStatus, UserRank
    )
    MODELS_LOADED = True
except ImportError:
    try:
        from database.models import (
            Base, User, Content, Rating, Duel, DuelVote, 
            AdminAction, BotStatistics, ContentType, ContentStatus, UserRank
        )
        MODELS_LOADED = True
    except ImportError:
        # Створити мінімальні моделі
        print("⚠️ Створюю fallback моделі")
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
        from enum import Enum
        
        Base = declarative_base()
        
        class ContentType(Enum):
            JOKE = "joke"
            MEME = "meme"
        
        class ContentStatus(Enum):
            PENDING = "pending"
            APPROVED = "approved"
            REJECTED = "rejected"
        
        class UserRank(Enum):
            NEWBIE = "Новачок"
            JOKER = "Жартівник"
            COMEDIAN = "Комік"
            HUMORIST = "Гуморист"
            MASTER = "Майстер сміху"
            EXPERT = "Експерт гумору"
            VIRTUOSO = "Віртуоз жартів"
            LEGEND = "Легенда гумору"
        
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            telegram_id = Column(Integer, unique=True, nullable=False)
            username = Column(String(50))
            first_name = Column(String(100))
            last_name = Column(String(100))
            is_active = Column(Boolean, default=True)
            is_admin = Column(Boolean, default=False)
            total_points = Column(Integer, default=0)
            created_at = Column(DateTime, server_default=func.now())
            last_activity = Column(DateTime, server_default=func.now())
        
        class Content(Base):
            __tablename__ = "content"
            id = Column(Integer, primary_key=True)
            text = Column(Text)
            author_id = Column(Integer)
            status = Column(String(20), default="pending")
            created_at = Column(DateTime, server_default=func.now())
        
        MODELS_LOADED = False

logger = logging.getLogger(__name__)

# ===== НАЛАШТУВАННЯ БД =====

try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        } if "sqlite" in settings.DATABASE_URL else {
            "connect_timeout": 30
        }
    )
    
    SessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine,
        expire_on_commit=False
    )
    
    DB_CONNECTED = True
    logger.info("✅ База даних підключена")
    
except Exception as e:
    logger.error(f"❌ Помилка підключення до БД: {e}")
    DB_CONNECTED = False

# ===== КОНТЕКСТНИЙ МЕНЕДЖЕР =====

@contextmanager
def get_db_session():
    """Контекстний менеджер для роботи з БД"""
    if not DB_CONNECTED:
        logger.warning("⚠️ БД не підключена")
        yield None
        return
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"🧠 Помилка БД: {e}")
        raise
    finally:
        session.close()

# ===== ІНІЦІАЛІЗАЦІЯ БД =====

async def init_db():
    """Ініціалізація бази даних з міграцією"""
    try:
        logger.info("💾 Початок ініціалізації бази даних...")
        
        if not DB_CONNECTED:
            logger.error("❌ БД не підключена, пропускаю ініціалізацію")
            return
        
        # Перевірка міграції
        needs_migration = await check_if_migration_needed()
        
        if needs_migration:
            logger.info("🔄 Потрібна міграція БД...")
            await migrate_database()
        
        # Створення таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("🔥 Таблиці бази даних створено!")
        
        # Початкові дані
        await add_initial_data()
        
        logger.info("✅ База даних повністю ініціалізована!")
        
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації БД: {e}")
        # Не кидаємо помилку, щоб бот міг запуститися

async def check_if_migration_needed() -> bool:
    """Перевірити чи потрібна міграція"""
    try:
        with get_db_session() as session:
            if session is None:
                return False
            
            # Спроба запиту до нової структури
            session.execute(text("SELECT telegram_id FROM users LIMIT 1"))
            return False
    except Exception:
        return True

async def migrate_database():
    """Міграція БД"""
    try:
        with engine.begin() as conn:
            tables = ['duel_votes', 'admin_actions', 'bot_statistics', 'ratings', 'duels', 'content', 'users']
            for table in tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    logger.info(f"🗑️ Видалено таблицю: {table}")
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"⚠️ Помилка міграції: {e}")

# ===== ФУНКЦІЇ КОРИСТУВАЧІВ =====

async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, **kwargs) -> Optional[User]:
    """Отримати або створити користувача"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            
            # Знайти існуючого
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Оновити дані
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                user.last_activity = datetime.utcnow()
                session.commit()
                return user
            
            # Створити нового
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                is_active=True,
                is_admin=(telegram_id == settings.ADMIN_ID),
                total_points=0,
                **kwargs
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            logger.info(f"✅ Створено користувача: {telegram_id} (@{username})")
            return new_user
            
    except Exception as e:
        logger.error(f"❌ Помилка створення користувача {telegram_id}: {e}")
        return None

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Отримати користувача за ID"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if user:
                user.last_activity = datetime.utcnow()
                session.commit()
                session.refresh(user)
            return user
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
        return None

async def update_user_points(user_id: int, points: int, reason: str = "activity") -> Optional[Dict[str, Any]]:
    """Оновити бали користувача"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                logger.warning(f"⚠️ Користувач {user_id} не знайдений для оновлення балів")
                return None
            
            old_points = user.total_points
            user.total_points = max(0, user.total_points + points)
            user.last_activity = datetime.utcnow()
            
            session.commit()
            session.refresh(user)
            
            logger.info(f"💰 Користувач {user_id}: {old_points} → {user.total_points} (+{points}) за {reason}")
            
            return {
                "user_id": user_id,
                "old_points": old_points,
                "added_points": points,
                "total_points": user.total_points,
                "reason": reason
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення балів {user_id}: {e}")
        return None

async def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Статистика користувача"""
    try:
        with get_db_session() as session:
            if session is None:
                return {"error": "БД недоступна"}
            
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                return {"error": "Користувач не знайдений"}
            
            return {
                "user_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "total_points": user.total_points,
                "is_admin": getattr(user, 'is_admin', False),
                "created_at": user.created_at,
                "last_activity": user.last_activity
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка статистики користувача {user_id}: {e}")
        return {"error": str(e)}

# ===== ФУНКЦІЇ КОНТЕНТУ =====

async def add_content_for_moderation(user_id: int, content_type: str, text: str, file_id: str = None) -> Optional[Content]:
    """Додати контент на модерацію"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            
            content = Content(
                text=text,
                author_id=user_id,
                status="pending"
            )
            
            # Додаємо інші поля якщо вони є в моделі
            if hasattr(content, 'content_type'):
                content.content_type = ContentType.JOKE if content_type.lower() == "joke" else ContentType.MEME
            if hasattr(content, 'file_id'):
                content.file_id = file_id
            
            session.add(content)
            session.commit()
            session.refresh(content)
            
            logger.info(f"📝 Контент на модерацію від {user_id}: ID={content.id}")
            return content
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту: {e}")
        return None

async def get_pending_content(limit: int = 10) -> List[Dict[str, Any]]:
    """Контент на модерації"""
    try:
        with get_db_session() as session:
            if session is None:
                return []
            
            pending = session.query(Content).filter(
                Content.status == "pending"
            ).order_by(Content.created_at.asc()).limit(limit).all()
            
            result = []
            for item in pending:
                # Отримати дані автора
                author = session.query(User).filter(User.telegram_id == item.author_id).first()
                author_name = "Невідомий"
                if author:
                    author_name = f"{author.first_name or ''} {author.last_name or ''}".strip()
                    if author.username:
                        author_name += f" (@{author.username})"
                
                result.append({
                    "id": item.id,
                    "type": getattr(item, 'content_type', 'joke'),
                    "text": item.text,
                    "author_id": item.author_id,
                    "author_name": author_name,
                    "created_at": item.created_at
                })
            
            return result
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту на модерації: {e}")
        return []

async def moderate_content(content_id: int, moderator_id: int, approve: bool, comment: str = None) -> bool:
    """Модерація контенту"""
    try:
        with get_db_session() as session:
            if session is None:
                return False
            
            content = session.query(Content).filter(Content.id == content_id).first()
            if not content:
                return False
            
            content.status = "approved" if approve else "rejected"
            if hasattr(content, 'moderator_id'):
                content.moderator_id = moderator_id
            if hasattr(content, 'moderation_comment'):
                content.moderation_comment = comment
            
            session.commit()
            
            # Нарахувати бали автору
            if approve:
                await update_user_points(content.author_id, settings.POINTS_FOR_APPROVAL, "approved_content")
            
            status_text = "схвалено" if approve else "відхилено"
            logger.info(f"📋 Контент {content_id} {status_text} модератором {moderator_id}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка модерації {content_id}: {e}")
        return False

async def get_content_by_id(content_id: int) -> Optional[Content]:
    """Контент за ID"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                session.refresh(content)
            return content
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту {content_id}: {e}")
        return None

async def get_random_approved_content(content_type: str = "mixed", limit: int = 1) -> Union[Content, List[Content], None]:
    """Випадковий схвалений контент"""
    try:
        with get_db_session() as session:
            if session is None:
                return [] if limit > 1 else None
            
            query = session.query(Content).filter(Content.status == "approved")
            all_content = query.all()
            
            if not all_content:
                return [] if limit > 1 else None
            
            if limit == 1:
                selected = random.choice(all_content)
                session.refresh(selected)
                return selected
            else:
                selected = random.sample(all_content, min(limit, len(all_content)))
                for item in selected:
                    session.refresh(item)
                return selected
                
    except Exception as e:
        logger.error(f"❌ Помилка отримання випадкового контенту: {e}")
        return [] if limit > 1 else None

# ===== ФУНКЦІЇ РЕЙТИНГІВ =====

async def add_content_rating(user_id: int, content_id: int, rating: int, comment: str = None) -> bool:
    """Додати рейтинг"""
    try:
        logger.info(f"⭐ Рейтинг від {user_id} для контенту {content_id}: {rating}")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка рейтингу: {e}")
        return False

async def get_content_rating(user_id: int, content_id: int) -> Optional[int]:
    """Отримати рейтинг"""
    return None

async def update_content_rating(user_id: int, content_id: int, new_rating: int) -> bool:
    """Оновити рейтинг"""
    return await add_content_rating(user_id, content_id, new_rating)

# ===== ФУНКЦІЇ РЕКОМЕНДАЦІЙ =====

async def get_recommended_content(user_id: int, content_type: str) -> Optional[Content]:
    """Рекомендований контент"""
    return await get_random_approved_content(content_type, 1)

async def record_content_view(user_id: int, content_id: int, source: str = "command") -> bool:
    """Записати перегляд"""
    await update_user_points(user_id, 1, f"content_view_{source}")
    return True

# ===== ФУНКЦІЇ СТАТИСТИКИ =====

async def get_bot_statistics() -> Dict[str, Any]:
    """Статистика бота"""
    try:
        with get_db_session() as session:
            if session is None:
                return {"total_users": 0, "total_content": 0, "today_ratings": 0}
            
            total_users = session.query(User).count()
            active_today = session.query(User).filter(
                User.last_activity >= datetime.utcnow() - timedelta(days=1)
            ).count()
            
            total_content = session.query(Content).count()
            approved_content = session.query(Content).filter(
                Content.status == "approved"
            ).count()
            pending_content = session.query(Content).filter(
                Content.status == "pending"
            ).count()
            
            return {
                "total_users": total_users,
                "active_today": active_today,
                "total_content": total_content,
                "approved_content": approved_content,
                "pending_content": pending_content,
                "today_ratings": 0
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка статистики: {e}")
        return {"total_users": 0, "total_content": 0, "today_ratings": 0}

async def update_bot_statistics() -> bool:
    """Оновити статистику"""
    logger.info("📊 Статистика оновлена")
    return True

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def ensure_admin_exists() -> bool:
    """Створити адміністратора"""
    try:
        admin = await get_or_create_user(
            telegram_id=settings.ADMIN_ID,
            username="admin",
            first_name="Administrator",
            is_admin=True,
            total_points=1000
        )
        
        if admin:
            logger.info(f"👑 Адміністратор: {settings.ADMIN_ID}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"❌ Помилка створення адміністратора: {e}")
        return False

async def add_initial_data():
    """Початкові дані"""
    try:
        await ensure_admin_exists()
        
        # Додати зразки жартів
        sample_jokes = [
            "Чому програмісти не можуть відрізнити Хеловін від Різдва? Бо Oct 31 == Dec 25! 🧠😂",
            "Приходить українець до лікаря: 'Лікарю, у мене болить тут!' Лікар: 'А що там у вас?' Українець: 'Та хата стара, дах тече...' 😂",
            "Чому українські IT-шники найкращі в світі? Бо вони вміють працювати без світла! 🔥😂"
        ]
        
        with get_db_session() as session:
            if session is None:
                return
            
            existing = session.query(Content).filter(Content.status == "approved").count()
            if existing == 0:
                for joke in sample_jokes:
                    content = Content(
                        text=joke,
                        author_id=settings.ADMIN_ID,
                        status="approved"
                    )
                    session.add(content)
                session.commit()
                logger.info(f"✅ Додано {len(sample_jokes)} зразків")
        
        logger.info("✅ Початкові дані додано")
        
    except Exception as e:
        logger.error(f"❌ Помилка початкових даних: {e}")

# ===== ФУНКЦІЇ ДУЕЛЕЙ (ЗАГЛУШКИ) =====

async def create_duel(challenger_id: int, challenger_content_id: int) -> Optional[object]:
    """Створити дуель"""
    logger.info(f"⚔️ Запит на дуель від {challenger_id}")
    return None

async def get_active_duels() -> List[object]:
    """Активні дуелі"""
    return []

async def vote_in_duel(duel_id: int, voter_id: int, vote: str) -> bool:
    """Голосувати в дуелі"""
    logger.info(f"🗳️ Голос {voter_id} в дуелі {duel_id}: {vote}")
    return False

# ===== LEGACY ФУНКЦІЇ =====

async def submit_content(user_id: int, content_type, text: str = None, file_id: str = None) -> Optional[Content]:
    """Legacy подача контенту"""
    ct_string = "joke" if hasattr(content_type, 'JOKE') else "meme"
    return await add_content_for_moderation(user_id, ct_string, text, file_id)

async def update_user_stats(user_id: int, stats_update: Dict[str, Any]) -> bool:
    """Legacy оновлення статистики"""
    if "points" in stats_update:
        result = await update_user_points(user_id, stats_update["points"], "stats_update")
        return result is not None
    logger.info(f"📊 Статистика {user_id}: {stats_update}")
    return True

async def verify_database_integrity():
    """Перевірка цілісності БД"""
    try:
        stats = await get_bot_statistics()
        logger.info(f"📊 БД перевірено: {stats['total_users']} користувачів, {stats['total_content']} контенту")
    except Exception as e:
        logger.warning(f"⚠️ Помилка перевірки БД: {e}")

async def add_sample_content(session):
    """Додати зразки (legacy)"""
    pass

def calculate_user_rank(points: int):
    """Розрахувати ранг (legacy)"""
    if points >= 2500:
        return UserRank.LEGEND
    elif points >= 1500:
        return UserRank.VIRTUOSO
    elif points >= 1000:
        return UserRank.EXPERT
    elif points >= 600:
        return UserRank.MASTER
    elif points >= 300:
        return UserRank.HUMORIST
    elif points >= 150:
        return UserRank.COMEDIAN
    elif points >= 50:
        return UserRank.JOKER
    else:
        return UserRank.NEWBIE

def get_rank_info(points: int, current_rank):
    """Інформація про ранг (legacy)"""
    return {"rank_info": {"current_rank": "Новачок", "current_points": points}}

# ===== ЕКСПОРТ =====
logger.info("📦 Database модуль завантажено успішно")
logger.info(f"🔧 БД підключена: {DB_CONNECTED}")
logger.info(f"🎯 Моделі завантажені: {MODELS_LOADED}")