#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Ініціалізація пакету database з усіма функціями 🧠😂🔥
"""

import logging
from datetime import datetime

# Основні імпорти
from .database import get_db_session, init_db
from .models import (
    Base, User, Content, Rating, Duel, DuelVote,
    AdminAction, BotStatistics, ContentType, ContentStatus, DuelStatus
)

logger = logging.getLogger(__name__)

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З КОРИСТУВАЧАМИ =====

async def get_or_create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Створення або отримання користувача"""
    try:
        with get_db_session() as session:
            # Спробуємо знайти існуючого користувача
            user = session.query(User).filter(User.id == user_id).first()
            
            if user:
                # Оновлюємо дані якщо змінились
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
                
                # Оновлюємо час останньої активності
                user.last_activity = datetime.utcnow()
                
                if updated:
                    logger.info(f"👤 Оновлено дані користувача {user_id}")
                
                return user
            else:
                # Створюємо нового користувача
                user = User(
                    id=user_id,
                    username=username,
                    first_name=first_name or "Невідомий",
                    last_name=last_name,
                    points=0,
                    rank="🤡 Новачок",
                    is_active=True,
                    last_activity=datetime.utcnow()
                )
                
                session.add(user)
                session.commit()
                
                logger.info(f"🎉 Створено нового користувача: {user_id} ({first_name})")
                return user
                
    except Exception as e:
        logger.error(f"❌ Помилка створення/отримання користувача {user_id}: {e}")
        return None

def get_user_by_id(user_id: int):
    """Отримання користувача за ID"""
    try:
        with get_db_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
        return None

def update_user_points(user_id: int, points_delta: int, action_description: str = ""):
    """Оновлення балів користувача"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                old_points = user.points
                user.points += points_delta
                
                # Перевіряємо чи змінився ранг
                old_rank = user.rank
                user.rank = calculate_rank_by_points(user.points)
                
                session.commit()
                
                logger.info(f"💰 Користувач {user_id}: {old_points} → {user.points} (+{points_delta}) {action_description}")
                
                if old_rank != user.rank:
                    logger.info(f"🏆 Користувач {user_id} підвищився до рангу: {user.rank}")
                
                return user
            else:
                logger.warning(f"⚠️ Користувач {user_id} не знайдений для оновлення балів")
                return None
                
    except Exception as e:
        logger.error(f"❌ Помилка оновлення балів користувача {user_id}: {e}")
        return None

def calculate_rank_by_points(points: int) -> str:
    """Розрахунок рангу за балами"""
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

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З КОНТЕНТОМ =====

def add_content(author_id: int, content_type: str, text: str = None, file_id: str = None):
    """Додавання нового контенту"""
    try:
        with get_db_session() as session:
            content = Content(
                author_id=author_id,
                content_type=ContentType.JOKE if content_type.lower() == 'joke' else ContentType.MEME,
                text=text,
                file_id=file_id,
                status=ContentStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            session.add(content)
            session.commit()
            
            logger.info(f"📝 Додано новий контент від користувача {author_id}: {content_type}")
            return content
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту: {e}")
        return None

def get_random_approved_content(content_type: str = None):
    """Отримання випадкового схваленого контенту"""
    try:
        with get_db_session() as session:
            query = session.query(Content).filter(Content.status == ContentStatus.APPROVED)
            
            if content_type:
                if content_type.lower() == 'joke':
                    query = query.filter(Content.content_type == ContentType.JOKE)
                elif content_type.lower() == 'meme':
                    query = query.filter(Content.content_type == ContentType.MEME)
            
            content = query.order_by(Content.id.desc()).first()  # Fallback якщо немає функції random
            return content
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту: {e}")
        return None

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З РЕЙТИНГАМИ =====

def add_rating(user_id: int, content_id: int, action_type: str, points_awarded: int = 0):
    """Додавання рейтингу/реакції"""
    try:
        with get_db_session() as session:
            # Перевіряємо чи не голосував вже цей користувач за цей контент
            existing_rating = session.query(Rating).filter(
                Rating.user_id == user_id,
                Rating.content_id == content_id,
                Rating.action_type == action_type
            ).first()
            
            if existing_rating:
                logger.info(f"⚠️ Користувач {user_id} вже голосував за контент {content_id}")
                return existing_rating
            
            rating = Rating(
                user_id=user_id,
                content_id=content_id,
                action_type=action_type,
                points_awarded=points_awarded,
                created_at=datetime.utcnow()
            )
            
            session.add(rating)
            
            # Оновлюємо статистику контенту
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                if action_type == "like":
                    content.likes += 1
                elif action_type == "dislike":
                    content.dislikes += 1
                elif action_type == "view":
                    content.views += 1
            
            session.commit()
            
            logger.info(f"⭐ Додано рейтинг: користувач {user_id} → контент {content_id} ({action_type})")
            return rating
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання рейтингу: {e}")
        return None

# ===== СТАТИСТИЧНІ ФУНКЦІЇ =====

def get_user_stats(user_id: int):
    """Отримання статистики користувача"""
    try:
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Контент користувача
            user_content = session.query(Content).filter(Content.author_id == user_id).count()
            approved_content = session.query(Content).filter(
                Content.author_id == user_id,
                Content.status == ContentStatus.APPROVED
            ).count()
            
            # Активність користувача
            user_ratings = session.query(Rating).filter(Rating.user_id == user_id).count()
            
            return {
                "user": user,
                "total_submissions": user_content,
                "approved_submissions": approved_content,
                "total_interactions": user_ratings,
                "points": user.points,
                "rank": user.rank
            }
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики користувача {user_id}: {e}")
        return None

def get_leaderboard(limit: int = 10):
    """Отримання таблиці лідерів"""
    try:
        with get_db_session() as session:
            top_users = session.query(User).filter(
                User.is_active == True
            ).order_by(User.points.desc()).limit(limit).all()
            
            return [{
                "id": user.id,
                "name": user.first_name or "Невідомий",
                "username": user.username,
                "points": user.points,
                "rank": user.rank
            } for user in top_users]
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання leaderboard: {e}")
        return []

# ===== ЕКСПОРТ ФУНКЦІЙ =====

__all__ = [
    # Основні класи та функції
    'get_db_session', 'init_db',
    'Base', 'User', 'Content', 'Rating', 'Duel', 'DuelVote',
    'AdminAction', 'BotStatistics', 
    'ContentType', 'ContentStatus', 'DuelStatus',
    
    # Функції для роботи з користувачами
    'get_or_create_user', 'get_user_by_id', 'update_user_points', 'calculate_rank_by_points',
    
    # Функції для роботи з контентом
    'add_content', 'get_random_approved_content',
    
    # Функції для роботи з рейтингами
    'add_rating',
    
    # Статистичні функції
    'get_user_stats', 'get_leaderboard'
]