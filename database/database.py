#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНА РОБОТА З БАЗОЮ ДАНИХ - ПОВНА ВЕРСІЯ 🧠😂🔥
Повністю функціональний модуль з усіма необхідними функціями для України-бота
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
from config.settings import settings

# Імпорт моделей БД
from .models import (
    Base, User, Content, Rating, Duel, DuelVote, 
    AdminAction, BotStatistics, ContentType, ContentStatus, UserRank
)

logger = logging.getLogger(__name__)

# ===== НАЛАШТУВАННЯ БД =====

# Створення движка бази даних з професійними налаштуваннями
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL логи тільки в debug режимі
    pool_pre_ping=True,   # Перевірка з'єднання перед використанням
    pool_recycle=3600,    # Оновлення з'єднань кожну годину
    pool_size=10,         # Розмір пулу з'єднань
    max_overflow=20,      # Максимум додаткових з'єднань
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    } if "sqlite" in settings.DATABASE_URL else {
        "connect_timeout": 30,
        "application_name": "ukraine_telegram_bot"
    }
)

# Створення фабрики сесій
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Важливо для уникнення detached objects
)

# ===== КОНТЕКСТНИЙ МЕНЕДЖЕР СЕСІЙ =====

@contextmanager
def get_db_session():
    """Професійний контекстний менеджер для роботи з БД"""
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
    """Професійна ініціалізація бази даних"""
    try:
        logger.info("💾 Початок ініціалізації бази даних...")
        
        # Створення всіх таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("🔥 Таблиці бази даних створено!")
        
        # Додавання початкових даних
        await add_initial_data()
        
        # Перевірка цілісності
        await verify_database_integrity()
        
        logger.info("✅ База даних повністю ініціалізована!")
        
    except Exception as e:
        logger.error(f"❌ Критична помилка ініціалізації БД: {e}")
        raise

async def verify_database_integrity():
    """Перевірка цілісності бази даних"""
    try:
        with get_db_session() as session:
            # Перевірка основних таблиць
            user_count = session.query(User).count()
            content_count = session.query(Content).count()
            
            logger.info(f"📊 Перевірка БД: {user_count} користувачів, {content_count} контенту")
            
            # Перевірка адміністратора
            admin = session.query(User).filter(User.telegram_id == settings.ADMIN_ID).first()
            if not admin:
                logger.warning("⚠️ Адміністратор не знайдений, створюю...")
                await ensure_admin_exists()
                
    except Exception as e:
        logger.error(f"❌ Помилка перевірки цілісності БД: {e}")

# ===== ФУНКЦІЇ РОБОТИ З КОРИСТУВАЧАМИ =====

async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, 
                           last_name: str = None, **kwargs) -> Optional[User]:
    """Отримати або створити користувача з повною обробкою помилок"""
    try:
        with get_db_session() as session:
            # Спробувати знайти існуючого користувача
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Оновити дані користувача якщо вони змінилися
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
                
                # Оновити час останньої активності
                user.last_activity = datetime.utcnow()
                
                if updated:
                    session.commit()
                    logger.info(f"🔄 Оновлено дані користувача: {telegram_id} (@{username})")
                
                return user
            
            # Створити нового користувача
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_admin=(telegram_id == settings.ADMIN_ID),
                total_points=0,
                current_rank=UserRank.NEWBIE,
                **kwargs
            )
            
            session.add(new_user)
            session.commit()
            
            # Refresh для отримання всіх даних
            session.refresh(new_user)
            
            logger.info(f"✅ Створено нового користувача: {telegram_id} (@{username})")
            return new_user
            
    except IntegrityError as e:
        logger.error(f"⚠️ Користувач {telegram_id} вже існує: {e}")
        # Повторна спроба отримання
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.telegram_id == telegram_id).first()
        except Exception:
            return None
    except Exception as e:
        logger.error(f"❌ Помилка створення/отримання користувача {telegram_id}: {e}")
        return None

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Отримати користувача за telegram_id"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if user:
                # Оновити час останньої активності
                user.last_activity = datetime.utcnow()
                session.commit()
                session.refresh(user)
            return user
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
        return None

async def update_user_points(user_id: int, points: int, reason: str = "activity") -> Optional[Dict[str, Any]]:
    """Професійне оновлення балів користувача з перевіркою рангу"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                logger.warning(f"⚠️ Користувач {user_id} не знайдений для оновлення балів")
                return None
            
            # Зберігаємо попередній ранг
            old_rank = user.current_rank
            old_points = user.total_points
            
            # Оновлюємо бали
            user.total_points = max(0, user.total_points + points)
            user.last_activity = datetime.utcnow()
            
            # Перевіряємо зміну рангу
            new_rank = calculate_user_rank(user.total_points)
            rank_changed = new_rank != old_rank
            
            if rank_changed:
                user.current_rank = new_rank
            
            session.commit()
            session.refresh(user)
            
            result = {
                "user_id": user_id,
                "old_points": old_points,
                "added_points": points,
                "total_points": user.total_points,
                "old_rank": old_rank.value if old_rank else "Новачок",
                "new_rank": new_rank.value,
                "rank_changed": rank_changed,
                "reason": reason
            }
            
            logger.info(f"💰 Користувач {user_id}: {old_points} → {user.total_points} (+{points}) за {reason}")
            
            if rank_changed:
                logger.info(f"🎉 Користувач {user_id} підвищився до рангу: {new_rank.value}")
            
            return result
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення балів користувача {user_id}: {e}")
        return None

def calculate_user_rank(points: int) -> UserRank:
    """Розрахунок рангу користувача за балами"""
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

async def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Детальна статистика користувача"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return {"error": "Користувач не знайдений"}
            
            # Базова статистика користувача
            stats = {
                "user_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "total_points": user.total_points,
                "current_rank": user.current_rank.value if user.current_rank else "Новачок",
                "is_premium": user.is_premium,
                "is_admin": user.is_admin,
                "daily_subscription": user.daily_subscription,
                
                # Контент
                "jokes_submitted": user.jokes_submitted,
                "jokes_approved": user.jokes_approved,
                "memes_submitted": user.memes_submitted,
                "memes_approved": user.memes_approved,
                
                # Взаємодія
                "likes_given": user.likes_given,
                "dislikes_given": user.dislikes_given,
                "comments_made": user.comments_made,
                
                # Дуелі
                "duels_won": user.duels_won,
                "duels_lost": user.duels_lost,
                "duels_participated": user.duels_participated,
                
                # Час
                "created_at": user.created_at,
                "last_activity": user.last_activity
            }
            
            # Додаткова статистика з запитів
            total_content_created = session.query(Content).filter(
                Content.author_id == user_id
            ).count()
            
            approved_content = session.query(Content).filter(
                and_(Content.author_id == user_id, Content.status == ContentStatus.APPROVED)
            ).count()
            
            total_ratings_given = session.query(Rating).filter(Rating.user_id == user_id).count()
            
            # Позиція в рейтингу
            rank_position = session.query(User).filter(
                User.total_points > user.total_points
            ).count() + 1
            
            stats.update({
                "total_content_created": total_content_created,
                "approved_content": approved_content,
                "total_ratings_given": total_ratings_given,
                "approval_rate": (approved_content / total_content_created * 100) if total_content_created > 0 else 0,
                "rank_position": rank_position
            })
            
            # Інформація про ранг
            rank_info = get_rank_info(user.total_points, user.current_rank)
            stats.update(rank_info)
            
            return stats
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики користувача {user_id}: {e}")
        return {"error": str(e)}

def get_rank_info(points: int, current_rank: UserRank) -> Dict[str, Any]:
    """Інформація про прогрес рангу"""
    rank_requirements = {
        UserRank.NEWBIE: 0,
        UserRank.JOKER: 50,
        UserRank.COMEDIAN: 150,
        UserRank.HUMORIST: 300,
        UserRank.MASTER: 600,
        UserRank.EXPERT: 1000,
        UserRank.VIRTUOSO: 1500,
        UserRank.LEGEND: 2500
    }
    
    ranks = list(UserRank)
    current_index = ranks.index(current_rank)
    
    next_rank = None
    points_to_next = 0
    progress_percent = 100
    
    if current_index < len(ranks) - 1:
        next_rank = ranks[current_index + 1]
        points_to_next = rank_requirements[next_rank] - points
        current_rank_min = rank_requirements[current_rank]
        next_rank_min = rank_requirements[next_rank]
        progress_percent = min(100, ((points - current_rank_min) / (next_rank_min - current_rank_min)) * 100)
    
    return {
        "rank_info": {
            "current_rank": current_rank.value,
            "current_points": points,
            "next_rank": next_rank.value if next_rank else None,
            "points_to_next": max(0, points_to_next) if next_rank else 0,
            "progress_percent": round(progress_percent, 1)
        }
    }

# ===== ФУНКЦІЇ РОБОТИ З КОНТЕНТОМ =====

async def add_content_for_moderation(user_id: int, content_type: str, text: str, file_id: str = None) -> Optional[Content]:
    """Додати контент на модерацію з повною обробкою"""
    try:
        with get_db_session() as session:
            # Конвертуємо string в enum
            if content_type.lower() == "joke":
                ct = ContentType.JOKE
            elif content_type.lower() == "meme":
                ct = ContentType.MEME
            else:
                raise ValueError(f"Невідомий тип контенту: {content_type}")
            
            # Створюємо контент
            content = Content(
                content_type=ct,
                text=text,
                file_id=file_id,
                author_id=user_id,
                status=ContentStatus.PENDING,
                topic="general",
                style="neutral",
                difficulty=1,
                quality_score=0.5,
                popularity_score=0.0
            )
            
            session.add(content)
            session.commit()
            session.refresh(content)
            
            # Оновити статистику користувача
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if user:
                if ct == ContentType.JOKE:
                    user.jokes_submitted += 1
                else:
                    user.memes_submitted += 1
                session.commit()
            
            logger.info(f"📝 Новий контент на модерацію від {user_id}: ID={content.id}, тип={content_type}")
            return content
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту на модерацію: {e}")
        return None

async def get_pending_content(limit: int = 10) -> List[Dict[str, Any]]:
    """Отримати контент на модерації"""
    try:
        with get_db_session() as session:
            pending_items = session.query(Content).filter(
                Content.status == ContentStatus.PENDING
            ).order_by(Content.created_at.asc()).limit(limit).all()
            
            result = []
            for item in pending_items:
                # Отримати дані автора
                author = session.query(User).filter(User.telegram_id == item.author_id).first()
                author_name = "Невідомий"
                if author:
                    author_name = f"{author.first_name or ''} {author.last_name or ''}".strip()
                    if author.username:
                        author_name += f" (@{author.username})"
                
                result.append({
                    "id": item.id,
                    "type": item.content_type.value,
                    "text": item.text,
                    "file_id": item.file_id,
                    "author_id": item.author_id,
                    "author_name": author_name,
                    "created_at": item.created_at,
                    "topic": item.topic,
                    "quality_score": item.quality_score
                })
            
            return result
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту на модерації: {e}")
        return []

async def moderate_content(content_id: int, moderator_id: int, approve: bool, comment: str = None) -> bool:
    """Модерація контенту з повною обробкою"""
    try:
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if not content:
                logger.warning(f"⚠️ Контент {content_id} не знайдено для модерації")
                return False
            
            # Оновити статус контенту
            content.status = ContentStatus.APPROVED if approve else ContentStatus.REJECTED
            content.moderator_id = moderator_id
            content.moderation_comment = comment
            content.moderated_at = datetime.utcnow()
            
            # Оновити статистику автора
            author = session.query(User).filter(User.telegram_id == content.author_id).first()
            if author and approve:
                if content.content_type == ContentType.JOKE:
                    author.jokes_approved += 1
                else:
                    author.memes_approved += 1
                
                # Нарахувати бали за схвалення
                await update_user_points(author.telegram_id, settings.POINTS_FOR_APPROVAL, "approved_content")
            
            session.commit()
            
            status_text = "схвалено" if approve else "відхилено"
            logger.info(f"📋 Контент {content_id} {status_text} модератором {moderator_id}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка модерації контенту {content_id}: {e}")
        return False

async def get_content_by_id(content_id: int) -> Optional[Content]:
    """Отримати контент за ID"""
    try:
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                session.refresh(content)
            return content
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту {content_id}: {e}")
        return None

async def get_random_approved_content(content_type: str = "mixed", limit: int = 1) -> Union[Content, List[Content], None]:
    """Отримати випадковий схвалений контент"""
    try:
        with get_db_session() as session:
            query = session.query(Content).filter(Content.status == ContentStatus.APPROVED)
            
            # Фільтр за типом контенту
            if content_type != "mixed":
                if content_type.lower() == "joke":
                    query = query.filter(Content.content_type == ContentType.JOKE)
                elif content_type.lower() == "meme":
                    query = query.filter(Content.content_type == ContentType.MEME)
            
            # Отримати всі записи та вибрати випадково
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

# ===== ФУНКЦІЇ РОБОТИ З РЕЙТИНГАМИ =====

async def add_content_rating(user_id: int, content_id: int, rating: int, comment: str = None) -> bool:
    """Додати або оновити рейтинг контенту"""
    try:
        with get_db_session() as session:
            # Перевірити чи користувач вже оцінював цей контент
            existing_rating = session.query(Rating).filter(
                and_(Rating.user_id == user_id, Rating.content_id == content_id)
            ).first()
            
            if existing_rating:
                # Оновити існуючий рейтинг
                old_rating = existing_rating.rating
                existing_rating.rating = rating
                existing_rating.comment = comment
                
                # Оновити статистику контенту
                content = session.query(Content).filter(Content.id == content_id).first()
                if content:
                    if old_rating == 1 and rating == -1:
                        content.likes = max(0, content.likes - 1)
                        content.dislikes += 1
                    elif old_rating == -1 and rating == 1:
                        content.dislikes = max(0, content.dislikes - 1)
                        content.likes += 1
                
                session.commit()
                logger.info(f"🔄 Оновлено рейтинг від {user_id} для контенту {content_id}: {rating}")
                
            else:
                # Створити новий рейтинг
                new_rating = Rating(
                    user_id=user_id,
                    content_id=content_id,
                    rating=rating,
                    comment=comment
                )
                session.add(new_rating)
                
                # Оновити статистику контенту
                content = session.query(Content).filter(Content.id == content_id).first()
                if content:
                    if rating == 1:
                        content.likes += 1
                    elif rating == -1:
                        content.dislikes += 1
                    
                    # Оновити показники перегляду
                    content.views += 1
                
                # Оновити статистику користувача
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if user:
                    if rating == 1:
                        user.likes_given += 1
                    else:
                        user.dislikes_given += 1
                
                session.commit()
                logger.info(f"➕ Додано рейтинг від {user_id} для контенту {content_id}: {rating}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання рейтингу: {e}")
        return False

async def get_content_rating(user_id: int, content_id: int) -> Optional[int]:
    """Отримати рейтинг користувача для контенту"""
    try:
        with get_db_session() as session:
            rating = session.query(Rating).filter(
                and_(Rating.user_id == user_id, Rating.content_id == content_id)
            ).first()
            
            return rating.rating if rating else None
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання рейтингу: {e}")
        return None

async def update_content_rating(user_id: int, content_id: int, new_rating: int) -> bool:
    """Оновити рейтинг (алиас для add_content_rating)"""
    return await add_content_rating(user_id, content_id, new_rating)

# ===== ФУНКЦІЇ ДЛЯ РЕКОМЕНДАЦІЙ =====

async def get_recommended_content(user_id: int, content_type: str) -> Optional[Content]:
    """Отримати рекомендований контент для користувача"""
    try:
        # Поки що використовуємо простий алгоритм
        return await get_random_approved_content(content_type, 1)
    except Exception as e:
        logger.error(f"❌ Помилка отримання рекомендованого контенту: {e}")
        return None

async def record_content_view(user_id: int, content_id: int, source: str = "command") -> bool:
    """Записати перегляд контенту"""
    try:
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                content.views += 1
                session.commit()
                
                # Нарахувати бал за перегляд
                await update_user_points(user_id, 1, f"content_view_{source}")
                
                return True
            return False
            
    except Exception as e:
        logger.error(f"❌ Помилка запису перегляду: {e}")
        return False

# ===== ФУНКЦІЇ СТАТИСТИКИ =====

async def get_bot_statistics() -> Dict[str, Any]:
    """Отримати загальну статистику бота"""
    try:
        with get_db_session() as session:
            # Користувачі
            total_users = session.query(User).count()
            active_today = session.query(User).filter(
                User.last_activity >= datetime.utcnow() - timedelta(days=1)
            ).count()
            active_week = session.query(User).filter(
                User.last_activity >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Контент
            total_content = session.query(Content).count()
            approved_content = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).count()
            pending_content = session.query(Content).filter(
                Content.status == ContentStatus.PENDING
            ).count()
            rejected_content = session.query(Content).filter(
                Content.status == ContentStatus.REJECTED
            ).count()
            
            # Рейтинги (активність)
            today_ratings = session.query(Rating).filter(
                Rating.created_at >= datetime.utcnow() - timedelta(days=1)
            ).count()
            
            return {
                "total_users": total_users,
                "active_today": active_today,
                "active_week": active_week,
                "total_content": total_content,
                "approved_content": approved_content,
                "pending_content": pending_content,
                "rejected_content": rejected_content,
                "today_ratings": today_ratings,
                "last_updated": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики бота: {e}")
        return {
            "total_users": 0,
            "active_today": 0,
            "active_week": 0,
            "total_content": 0,
            "approved_content": 0,
            "pending_content": 0,
            "rejected_content": 0,
            "today_ratings": 0,
            "error": str(e)
        }

async def update_bot_statistics() -> bool:
    """Оновити щоденну статистику бота"""
    try:
        stats = await get_bot_statistics()
        
        with get_db_session() as session:
            today = datetime.utcnow().date()
            
            # Знайти або створити запис за сьогодні
            bot_stats = session.query(BotStatistics).filter(
                func.date(BotStatistics.date) == today
            ).first()
            
            if not bot_stats:
                bot_stats = BotStatistics(date=datetime.utcnow())
                session.add(bot_stats)
            
            # Оновити статистику
            bot_stats.total_users = stats["total_users"]
            bot_stats.active_users_today = stats["active_today"]
            bot_stats.active_users_week = stats["active_week"]
            bot_stats.total_content = stats["total_content"]
            bot_stats.approved_content = stats["approved_content"]
            bot_stats.pending_content = stats["pending_content"]
            bot_stats.rejected_content = stats["rejected_content"]
            
            session.commit()
            logger.info("📊 Статистика бота оновлена")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення статистики бота: {e}")
        return False

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def ensure_admin_exists() -> bool:
    """Переконатися що адміністратор існує"""
    try:
        admin = await get_or_create_user(
            telegram_id=settings.ADMIN_ID,
            username="admin",
            first_name="Administrator",
            is_admin=True,
            total_points=1000
        )
        
        if admin:
            logger.info(f"👑 Адміністратор підтверджений: {settings.ADMIN_ID}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Помилка створення адміністратора: {e}")
        return False

async def add_initial_data():
    """Додати початкові дані з перевіркою"""
    try:
        # Створити адміністратора
        await ensure_admin_exists()
        
        # Додати початкові жарти якщо їх немає
        with get_db_session() as session:
            existing_jokes = session.query(Content).filter(
                and_(Content.content_type == ContentType.JOKE, Content.status == ContentStatus.APPROVED)
            ).count()
            
            if existing_jokes == 0:
                await add_sample_content(session)
        
        logger.info("✅ Початкові дані перевірено та додано")
        
    except Exception as e:
        logger.error(f"❌ Помилка додавання початкових даних: {e}")

async def add_sample_content(session: Session):
    """Додати зразки контенту"""
    sample_jokes = [
        "Чому програмісти не можуть відрізнити Хеловін від Різдва? Бо Oct 31 == Dec 25! 🧠😂",
        "Приходить українець до лікаря: 'Лікарю, у мене болить тут!' Лікар: 'А що там у вас?' Українець: 'Та хата стара, дах тече...' 😂",
        "Чому українські IT-шники найкращі в світі? Бо вони вміють працювати без світла! 🔥😂",
        "Що спільного між українською зимою та JavaScript? Ніколи не знаєш, що очікувати! ❄️😂",
        "Чому українці найкращі програмісти? Бо вони звикли debugити реальність! 🧠🔥"
    ]
    
    try:
        for joke_text in sample_jokes:
            joke = Content(
                content_type=ContentType.JOKE,
                text=joke_text,
                author_id=settings.ADMIN_ID,
                status=ContentStatus.APPROVED,
                topic="tech",
                style="irony",
                difficulty=1,
                quality_score=0.8,
                popularity_score=0.5,
                likes=random.randint(10, 50),
                views=random.randint(50, 200)
            )
            session.add(joke)
        
        session.commit()
        logger.info(f"✅ Додано {len(sample_jokes)} зразків жартів")
        
    except Exception as e:
        logger.error(f"❌ Помилка додавання зразків контенту: {e}")

# ===== ФУНКЦІЇ ДЛЯ ДУЕЛЕЙ =====

async def create_duel(challenger_id: int, challenger_content_id: int) -> Optional[Duel]:
    """Створити новий дуель"""
    try:
        with get_db_session() as session:
            # Знайти потенційних опонентів
            potential_opponents = session.query(User).filter(
                and_(
                    User.telegram_id != challenger_id,
                    User.is_active == True,
                    User.total_points > 10
                )
            ).limit(20).all()
            
            if not potential_opponents:
                logger.warning(f"⚠️ Немає опонентів для дуелі користувача {challenger_id}")
                return None
            
            # Випадковий опонент
            opponent = random.choice(potential_opponents)
            
            duel = Duel(
                challenger_id=challenger_id,
                opponent_id=opponent.telegram_id,
                challenger_content_id=challenger_content_id,
                status="waiting",
                voting_ends_at=datetime.utcnow() + timedelta(minutes=5)
            )
            
            session.add(duel)
            session.commit()
            session.refresh(duel)
            
            logger.info(f"⚔️ Створено дуель між {challenger_id} і {opponent.telegram_id}")
            return duel
            
    except Exception as e:
        logger.error(f"❌ Помилка створення дуелі: {e}")
        return None

async def get_active_duels() -> List[Duel]:
    """Отримати активні дуелі"""
    try:
        with get_db_session() as session:
            active_duels = session.query(Duel).filter(
                Duel.status.in_(["waiting", "active"])
            ).all()
            
            for duel in active_duels:
                session.refresh(duel)
            
            return active_duels
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання активних дуелей: {e}")
        return []

async def vote_in_duel(duel_id: int, voter_id: int, vote: str) -> bool:
    """Проголосувати в дуелі"""
    try:
        with get_db_session() as session:
            # Перевірити чи користувач вже голосував
            existing_vote = session.query(DuelVote).filter(
                and_(DuelVote.duel_id == duel_id, DuelVote.voter_id == voter_id)
            ).first()
            
            if existing_vote:
                logger.warning(f"⚠️ Користувач {voter_id} вже голосував в дуелі {duel_id}")
                return False
            
            # Додати голос
            new_vote = DuelVote(
                duel_id=duel_id,
                voter_id=voter_id,
                vote=vote
            )
            session.add(new_vote)
            
            # Оновити лічильники в дуелі
            duel = session.query(Duel).filter(Duel.id == duel_id).first()
            if duel:
                if vote == "challenger":
                    duel.challenger_votes += 1
                elif vote == "opponent":
                    duel.opponent_votes += 1
                
                session.commit()
                logger.info(f"🗳️ Голос від {voter_id} в дуелі {duel_id}: {vote}")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Помилка голосування в дуелі: {e}")
        return False

# ===== LEGACY ФУНКЦІЇ ДЛЯ СУМІСНОСТІ =====

async def submit_content(user_id: int, content_type: ContentType, text: str = None, file_id: str = None) -> Optional[Content]:
    """Legacy функція для сумісності"""
    ct_string = "joke" if content_type == ContentType.JOKE else "meme"
    return await add_content_for_moderation(user_id, ct_string, text, file_id)

async def update_user_stats(user_id: int, stats_update: Dict[str, Any]) -> bool:
    """Оновити статистику користувача (спрощений варіант)"""
    try:
        # Конвертуємо в update_user_points якщо це бали
        if "points" in stats_update:
            result = await update_user_points(user_id, stats_update["points"], "stats_update")
            return result is not None
        
        # Інші оновлення статистики можна додати тут
        logger.info(f"📊 Оновлення статистики {user_id}: {stats_update}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка оновлення статистики: {e}")
        return False