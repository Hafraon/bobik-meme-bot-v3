#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Додавання відсутніх функцій до database.py 🧠😂🔥
ДОДАТИ ЦІ ФУНКЦІЇ ДО ІСНУЮЧОГО database/database.py
"""

import logging
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З РЕЙТИНГАМИ =====

async def add_content_rating(user_id: int, content_id: int, rating: int, comment: str = None) -> bool:
    """Додати рейтинг до контенту"""
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
                session.commit()
                
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
                return True
            else:
                # Створити новий рейтинг
                new_rating = Rating(
                    user_id=user_id,
                    content_id=content_id,
                    rating=rating,
                    comment=comment
                )
                session.add(new_rating)
                session.commit()
                
                # Оновити статистику контенту
                content = session.query(Content).filter(Content.id == content_id).first()
                if content:
                    if rating == 1:
                        content.likes += 1
                    elif rating == -1:
                        content.dislikes += 1
                    session.commit()
                
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

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З КОРИСТУВАЧАМИ =====

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Отримати користувача за telegram_id"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if user:
                # Оновити час останньої активності
                user.last_activity = func.now()
                session.commit()
            return user
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
        return None

async def update_user_stats(user_id: int, stats_update: Dict[str, Any]) -> bool:
    """Оновити статистику користувача"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                return False
            
            # Оновити статистику
            for field, increment in stats_update.items():
                if hasattr(user, field):
                    current_value = getattr(user, field) or 0
                    setattr(user, field, current_value + increment)
            
            user.last_activity = func.now()
            session.commit()
            logger.info(f"📊 Оновлено статистику користувача {user_id}: {stats_update}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення статистики {user_id}: {e}")
        return False

async def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Отримати детальну статистику користувача"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                return {}
            
            # Базова статистика користувача
            stats = {
                "user_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "total_points": user.total_points,
                "current_rank": user.current_rank.value if user.current_rank else "Новачок",
                "is_premium": user.is_premium,
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
            
            # Додаткова статистика з інших таблиць
            total_content_created = session.query(Content).filter(
                Content.author_id == user_id
            ).count()
            
            approved_content = session.query(Content).filter(
                and_(Content.author_id == user_id, Content.status == ContentStatus.APPROVED)
            ).count()
            
            total_ratings_given = session.query(Rating).filter(Rating.user_id == user_id).count()
            
            stats.update({
                "total_content_created": total_content_created,
                "approved_content": approved_content,
                "total_ratings_given": total_ratings_given,
                "approval_rate": (approved_content / total_content_created * 100) if total_content_created > 0 else 0
            })
            
            return stats
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики {user_id}: {e}")
        return {}

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З КОНТЕНТОМ =====

async def get_content_by_id(content_id: int) -> Optional[Content]:
    """Отримати контент за ID"""
    try:
        with get_db_session() as session:
            return session.query(Content).filter(Content.id == content_id).first()
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту {content_id}: {e}")
        return None

async def get_random_approved_content(content_type: str = "mixed", limit: int = 1) -> List[Content]:
    """Отримати випадковий схвалений контент"""
    try:
        with get_db_session() as session:
            query = session.query(Content).filter(Content.status == ContentStatus.APPROVED)
            
            if content_type != "mixed":
                if content_type == "joke":
                    query = query.filter(Content.content_type == ContentType.JOKE)
                elif content_type == "meme":
                    query = query.filter(Content.content_type == ContentType.MEME)
            
            # Сортувати випадково та обмежити
            content_list = query.order_by(func.random()).limit(limit).all()
            return content_list if limit > 1 else content_list[0] if content_list else None
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання випадкового контенту: {e}")
        return [] if limit > 1 else None

# ===== ФУНКЦІЇ ДЛЯ ДУЕЛЕЙ =====

async def create_duel(challenger_id: int, challenger_content_id: int) -> Optional[Duel]:
    """Створити новий дуель"""
    try:
        with get_db_session() as session:
            # Знайти опонента (випадкового активного користувача)
            potential_opponents = session.query(User).filter(
                and_(
                    User.telegram_id != challenger_id,
                    User.is_active == True,
                    User.total_points > 10  # Мінімальна активність
                )
            ).limit(20).all()
            
            if not potential_opponents:
                return None
            
            # Випадковий опонент
            import random
            opponent = random.choice(potential_opponents)
            
            duel = Duel(
                challenger_id=challenger_id,
                opponent_id=opponent.telegram_id,
                challenger_content_id=challenger_content_id,
                status="waiting",
                voting_ends_at=datetime.now() + timedelta(minutes=5)  # 5 хвилин на голосування
            )
            
            session.add(duel)
            session.commit()
            
            logger.info(f"⚔️ Створено дуель між {challenger_id} і {opponent.telegram_id}")
            return duel
            
    except Exception as e:
        logger.error(f"❌ Помилка створення дуелі: {e}")
        return None

async def get_active_duels() -> List[Duel]:
    """Отримати активні дуелі"""
    try:
        with get_db_session() as session:
            return session.query(Duel).filter(
                Duel.status.in_(["waiting", "active"])
            ).all()
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
                return False  # Вже голосував
            
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
            
    except Exception as e:
        logger.error(f"❌ Помилка голосування в дуелі: {e}")
        return False

# ===== ФУНКЦІЇ ДЛЯ СТАТИСТИКИ БОТА =====

async def get_bot_statistics() -> Dict[str, Any]:
    """Отримати загальну статистику бота"""
    try:
        with get_db_session() as session:
            # Користувачі
            total_users = session.query(User).count()
            active_today = session.query(User).filter(
                User.last_activity >= datetime.now() - timedelta(days=1)
            ).count()
            active_week = session.query(User).filter(
                User.last_activity >= datetime.now() - timedelta(days=7)
            ).count()
            
            # Контент
            total_content = session.query(Content).count()
            approved_content = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).count()
            pending_content = session.query(Content).filter(
                Content.status == ContentStatus.PENDING
            ).count()
            
            # Дуелі
            total_duels = session.query(Duel).count()
            active_duels = session.query(Duel).filter(
                Duel.status.in_(["waiting", "active"])
            ).count()
            
            return {
                "users": {
                    "total": total_users,
                    "active_today": active_today,
                    "active_week": active_week
                },
                "content": {
                    "total": total_content,
                    "approved": approved_content,
                    "pending": pending_content,
                    "rejected": total_content - approved_content - pending_content
                },
                "duels": {
                    "total": total_duels,
                    "active": active_duels
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики бота: {e}")
        return {}

async def update_bot_statistics():
    """Оновити щоденну статистику бота"""
    try:
        stats = await get_bot_statistics()
        
        with get_db_session() as session:
            today = datetime.now().date()
            
            # Знайти або створити запис за сьогодні
            bot_stats = session.query(BotStatistics).filter(
                func.date(BotStatistics.date) == today
            ).first()
            
            if not bot_stats:
                bot_stats = BotStatistics(date=datetime.now())
                session.add(bot_stats)
            
            # Оновити статистику
            bot_stats.total_users = stats["users"]["total"]
            bot_stats.active_users_today = stats["users"]["active_today"]
            bot_stats.active_users_week = stats["users"]["active_week"]
            bot_stats.total_content = stats["content"]["total"]
            bot_stats.approved_content = stats["content"]["approved"]
            bot_stats.pending_content = stats["content"]["pending"]
            bot_stats.rejected_content = stats["content"]["rejected"]
            bot_stats.total_duels = stats["duels"]["total"]
            bot_stats.active_duels = stats["duels"]["active"]
            
            session.commit()
            logger.info("📊 Статистика бота оновлена")
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення статистики бота: {e}")

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def ensure_user_exists(user_id: int, username: str = None, first_name: str = None) -> User:
    """Переконатися що користувач існує в БД"""
    try:
        user = await get_user_by_id(user_id)
        if not user:
            user = await get_or_create_user(
                telegram_id=user_id,
                username=username,
                first_name=first_name
            )
        return user
    except Exception as e:
        logger.error(f"❌ Помилка забезпечення існування користувача {user_id}: {e}")
        return None

# ===== ДОДАТИ ДО КІНЦЯ ІСНУЮЧОГО database/database.py =====