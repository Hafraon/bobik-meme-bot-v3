#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Централізовані сервіси для роботи з базою даних 🧠😂🔥
Безпечна робота з SQLAlchemy 2.0+ та уникнення detached objects
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc, and_, or_

from database.database import get_db_session
from database.models import (
    User, Content, Rating, Duel, DuelVote, 
    ContentType, ContentStatus, DuelStatus
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """Централізований сервіс для роботи з БД"""
    
    # ===== СТАТИСТИКА =====
    
    @staticmethod
    def get_basic_stats() -> Dict[str, int]:
        """Отримання базової статистики (без detached objects!)"""
        with get_db_session() as session:
            return {
                "total_users": session.query(User).count(),
                "total_content": session.query(Content).count(),
                "pending_content": session.query(Content).filter(
                    Content.status == ContentStatus.PENDING
                ).count(),
                "approved_content": session.query(Content).filter(
                    Content.status == ContentStatus.APPROVED
                ).count(),
                "today_ratings": session.query(Rating).filter(
                    Rating.created_at >= datetime.utcnow().date()
                ).count(),
                "active_duels": session.query(Duel).filter(
                    Duel.status == DuelStatus.ACTIVE
                ).count()
            }
    
    @staticmethod
    def get_detailed_stats() -> Dict[str, Any]:
        """Детальна статистика з безпечним доступом до даних"""
        with get_db_session() as session:
            # Базові дані
            basic_stats = DatabaseService.get_basic_stats()
            
            # ТОП користувачі (безпечно!)
            top_users_query = session.query(
                User.id,
                User.first_name,
                User.username,
                User.points,
                User.rank
            ).order_by(desc(User.points)).limit(10)
            
            top_users = []
            for user_data in top_users_query:
                top_users.append({
                    "id": user_data.id,
                    "name": user_data.first_name or "Невідомий",
                    "username": user_data.username,
                    "points": user_data.points,
                    "rank": user_data.rank
                })
            
            # Статистика по типах контенту
            content_stats = session.query(
                Content.content_type,
                func.count(Content.id).label('count')
            ).filter(
                Content.status == ContentStatus.APPROVED
            ).group_by(Content.content_type).all()
            
            content_by_type = {}
            for content_type, count in content_stats:
                content_by_type[content_type.value] = count
            
            # Активність за тиждень
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_activity = session.query(
                func.date(Rating.created_at).label('date'),
                func.count(Rating.id).label('activity')
            ).filter(
                Rating.created_at >= week_ago
            ).group_by(func.date(Rating.created_at)).all()
            
            # Компіляція результатів
            return {
                **basic_stats,
                "top_users": top_users,
                "content_by_type": content_by_type,
                "weekly_activity": [
                    {"date": str(date), "activity": activity}
                    for date, activity in weekly_activity
                ]
            }
    
    # ===== КОРИСТУВАЧІ =====
    
    @staticmethod
    def get_users_management_data(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Дані для управління користувачами"""
        with get_db_session() as session:
            # Основний запит з пагінацією
            offset = (page - 1) * per_page
            
            users_query = session.query(
                User.id,
                User.first_name,
                User.username,
                User.points,
                User.rank,
                User.is_active,
                User.last_activity,
                func.count(Content.id).label('submissions_count')
            ).outerjoin(
                Content, User.id == Content.author_id
            ).group_by(User.id).order_by(
                desc(User.points)
            ).offset(offset).limit(per_page)
            
            users_data = []
            for user_row in users_query:
                users_data.append({
                    "id": user_row.id,
                    "name": user_row.first_name or "Невідомий",
                    "username": user_row.username,
                    "points": user_row.points,
                    "rank": user_row.rank,
                    "is_active": user_row.is_active,
                    "last_activity": user_row.last_activity.strftime('%d.%m.%Y %H:%M') if user_row.last_activity else "Немає",
                    "submissions": user_row.submissions_count
                })
            
            # Загальна кількість
            total_users = session.query(User).count()
            
            return {
                "users": users_data,
                "page": page,
                "per_page": per_page,
                "total": total_users,
                "total_pages": (total_users + per_page - 1) // per_page
            }
    
    @staticmethod
    def toggle_user_status(user_id: int) -> bool:
        """Перемикання статусу користувача"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = not user.is_active
                session.commit()
                return user.is_active
            return False
    
    # ===== КОНТЕНТ =====
    
    @staticmethod
    def get_content_analytics() -> Dict[str, Any]:
        """Аналітика контенту"""
        with get_db_session() as session:
            # Статистика по статусах
            status_stats = session.query(
                Content.status,
                func.count(Content.id).label('count')
            ).group_by(Content.status).all()
            
            # ТОП контент за переглядами
            top_content = session.query(
                Content.id,
                Content.text,
                Content.content_type,
                Content.views,
                Content.likes,
                Content.dislikes,
                User.first_name.label('author_name')
            ).join(
                User, Content.author_id == User.id
            ).filter(
                Content.status == ContentStatus.APPROVED
            ).order_by(desc(Content.views)).limit(10).all()
            
            # Контент за останній тиждень
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_content = session.query(
                func.date(Content.created_at).label('date'),
                func.count(Content.id).label('count')
            ).filter(
                Content.created_at >= week_ago
            ).group_by(func.date(Content.created_at)).all()
            
            return {
                "status_distribution": {
                    status.value: count for status, count in status_stats
                },
                "top_content": [
                    {
                        "id": row.id,
                        "text": (row.text[:100] + "...") if row.text and len(row.text) > 100 else row.text,
                        "type": row.content_type.value,
                        "views": row.views,
                        "likes": row.likes,
                        "dislikes": row.dislikes,
                        "author": row.author_name or "Невідомий"
                    }
                    for row in top_content
                ],
                "recent_submissions": [
                    {"date": str(date), "count": count}
                    for date, count in recent_content
                ]
            }
    
    @staticmethod
    def get_trending_content(days: int = 7) -> List[Dict[str, Any]]:
        """Трендовий контент за період"""
        with get_db_session() as session:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Складна формула трендинга: (лайки - дизлайки) * 2 + перегляди
            trending = session.query(
                Content.id,
                Content.text,
                Content.content_type,
                Content.views,
                Content.likes,
                Content.dislikes,
                Content.created_at,
                User.first_name.label('author_name'),
                ((Content.likes - Content.dislikes) * 2 + Content.views).label('trend_score')
            ).join(
                User, Content.author_id == User.id
            ).filter(
                and_(
                    Content.status == ContentStatus.APPROVED,
                    Content.created_at >= since_date
                )
            ).order_by(desc('trend_score')).limit(20).all()
            
            return [
                {
                    "id": row.id,
                    "text": (row.text[:150] + "...") if row.text and len(row.text) > 150 else row.text,
                    "type": row.content_type.value,
                    "views": row.views,
                    "likes": row.likes,
                    "dislikes": row.dislikes,
                    "author": row.author_name or "Невідомий",
                    "trend_score": int(row.trend_score),
                    "created": row.created_at.strftime('%d.%m.%Y')
                }
                for row in trending
            ]
    
    # ===== МОДЕРАЦІЯ =====
    
    @staticmethod
    def get_pending_content(limit: int = 1) -> List[Dict[str, Any]]:
        """Контент на модерації"""
        with get_db_session() as session:
            pending = session.query(
                Content.id,
                Content.text,
                Content.file_id,
                Content.content_type,
                Content.created_at,
                User.first_name.label('author_name'),
                User.username.label('author_username')
            ).join(
                User, Content.author_id == User.id
            ).filter(
                Content.status == ContentStatus.PENDING
            ).order_by(Content.created_at).limit(limit).all()
            
            return [
                {
                    "id": row.id,
                    "text": row.text,
                    "file_id": row.file_id,
                    "type": row.content_type.value,
                    "author_name": row.author_name or "Невідомий",
                    "author_username": row.author_username,
                    "created": row.created_at.strftime('%d.%m.%Y %H:%M')
                }
                for row in pending
            ]
    
    @staticmethod
    def moderate_content(content_id: int, approve: bool, moderator_id: int, comment: str = None) -> bool:
        """Модерація контенту"""
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            if not content:
                return False
            
            # Встановлюємо новий статус
            content.status = ContentStatus.APPROVED if approve else ContentStatus.REJECTED
            content.moderator_id = moderator_id
            content.moderated_at = datetime.utcnow()
            if comment:
                content.moderation_comment = comment
            
            # Нараховуємо бали автору за схвалення
            if approve:
                author = session.query(User).filter(User.id == content.author_id).first()
                if author:
                    author.points += 20  # Бонус за схвалений контент
            
            session.commit()
            return True
    
    # ===== ДУЕЛІ =====
    
    @staticmethod
    def get_active_duels() -> List[Dict[str, Any]]:
        """Активні дуелі"""
        with get_db_session() as session:
            duels = session.query(
                Duel.id,
                Duel.initiator_votes,
                Duel.opponent_votes,
                Duel.created_at,
                User.first_name.label('initiator_name')
            ).join(
                User, Duel.initiator_id == User.id
            ).filter(
                Duel.status == DuelStatus.ACTIVE
            ).order_by(desc(Duel.created_at)).all()
            
            return [
                {
                    "id": row.id,
                    "initiator": row.initiator_name or "Невідомий",
                    "votes_a": row.initiator_votes,
                    "votes_b": row.opponent_votes,
                    "created": row.created_at.strftime('%d.%m.%Y %H:%M')
                }
                for row in duels
            ]