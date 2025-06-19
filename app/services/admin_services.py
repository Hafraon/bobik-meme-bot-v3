#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Розширені сервіси для адміністрування бота 🧠😂🔥
"""

import logging
import json
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from database.database import get_db_session
from database.models import User, Content, Rating, Duel, ContentType, ContentStatus

logger = logging.getLogger(__name__)

class BackupService:
    """Сервіс резервного копіювання"""
    
    @staticmethod
    def create_json_backup() -> Dict[str, Any]:
        """Створення JSON бекапу всіх даних"""
        with get_db_session() as session:
            # Користувачі
            users = session.query(User).all()
            users_data = [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "username": user.username,
                    "points": user.points,
                    "rank": user.rank,
                    "is_active": user.is_active,
                    "last_activity": user.last_activity.isoformat() if user.last_activity else None
                }
                for user in users
            ]
            
            # Контент
            content = session.query(Content).all()
            content_data = [
                {
                    "id": c.id,
                    "content_type": c.content_type.value,
                    "text": c.text,
                    "status": c.status.value,
                    "author_id": c.author_id,
                    "views": c.views,
                    "likes": c.likes,
                    "dislikes": c.dislikes,
                    "created_at": c.created_at.isoformat()
                }
                for c in content
            ]
            
            # Рейтинги
            ratings = session.query(Rating).all()
            ratings_data = [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "content_id": r.content_id,
                    "action_type": r.action_type,
                    "points_awarded": r.points_awarded,
                    "created_at": r.created_at.isoformat()
                }
                for r in ratings
            ]
            
            return {
                "backup_info": {
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "2.0",
                    "total_users": len(users_data),
                    "total_content": len(content_data),
                    "total_ratings": len(ratings_data)
                },
                "users": users_data,
                "content": content_data,
                "ratings": ratings_data
            }
    
    @staticmethod
    def create_csv_backup() -> Dict[str, str]:
        """Створення CSV бекапів для кожної таблиці"""
        backups = {}
        
        with get_db_session() as session:
            # CSV для користувачів
            users = session.query(User).all()
            users_csv = io.StringIO()
            users_writer = csv.writer(users_csv)
            users_writer.writerow([
                'id', 'first_name', 'username', 'points', 'rank', 
                'is_active', 'last_activity'
            ])
            
            for user in users:
                users_writer.writerow([
                    user.id, user.first_name or '', user.username or '', 
                    user.points, user.rank, user.is_active,
                    user.last_activity.isoformat() if user.last_activity else ''
                ])
            
            backups['users.csv'] = users_csv.getvalue()
            
            # CSV для контенту
            content = session.query(Content).all()
            content_csv = io.StringIO()
            content_writer = csv.writer(content_csv)
            content_writer.writerow([
                'id', 'content_type', 'text', 'status', 'author_id',
                'views', 'likes', 'dislikes', 'created_at'
            ])
            
            for c in content:
                content_writer.writerow([
                    c.id, c.content_type.value, c.text or '', c.status.value,
                    c.author_id, c.views, c.likes, c.dislikes,
                    c.created_at.isoformat()
                ])
            
            backups['content.csv'] = content_csv.getvalue()
            
            return backups

class BulkActionService:
    """Сервіс масових операцій"""
    
    @staticmethod
    def recalculate_user_ranks() -> Dict[str, int]:
        """Перерахунок рангів всіх користувачів"""
        with get_db_session() as session:
            users = session.query(User).all()
            updated_count = 0
            
            rank_thresholds = [
                (5000, "Гумористичний Геній"),
                (3000, "Легенда Мемів"),
                (1500, "Король Гумору"),
                (750, "Мастер Рофлу"),
                (350, "Комік"),
                (150, "Гуморист"),
                (50, "Сміхун"),
                (0, "Новачок")
            ]
            
            for user in users:
                old_rank = user.rank
                
                for threshold, rank_name in rank_thresholds:
                    if user.points >= threshold:
                        user.rank = rank_name
                        break
                
                if old_rank != user.rank:
                    updated_count += 1
            
            session.commit()
            
            return {
                "total_users": len(users),
                "updated_ranks": updated_count
            }
    
    @staticmethod
    def cleanup_old_data(days: int = 90) -> Dict[str, int]:
        """Очистка старих даних"""
        with get_db_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Видаляємо старі рейтинги неактивних користувачів
            old_ratings = session.query(Rating).filter(
                Rating.created_at < cutoff_date
            ).count()
            
            # Видаляємо відхилений контент старше 30 днів
            old_rejected = session.query(Content).filter(
                Content.status == ContentStatus.REJECTED,
                Content.moderated_at < (datetime.utcnow() - timedelta(days=30))
            ).count()
            
            # Деактивуємо користувачів без активності
            inactive_users = session.query(User).filter(
                User.last_activity < cutoff_date,
                User.is_active == True
            ).count()
            
            session.query(User).filter(
                User.last_activity < cutoff_date,
                User.is_active == True
            ).update({"is_active": False})
            
            session.commit()
            
            return {
                "old_ratings_found": old_ratings,
                "old_rejected_content": old_rejected,
                "deactivated_users": inactive_users
            }
    
    @staticmethod
    def award_bonus_points(user_ids: List[int], points: int, reason: str = "") -> Dict[str, int]:
        """Нарахування бонусних балів"""
        with get_db_session() as session:
            updated_users = 0
            total_points_awarded = 0
            
            for user_id in user_ids:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.points += points
                    updated_users += 1
                    total_points_awarded += points
                    
                    # Створюємо запис про нарахування
                    rating = Rating(
                        user_id=user_id,
                        content_id=None,  # Бонусні бали не пов'язані з контентом
                        action_type=f"bonus_{reason}",
                        points_awarded=points
                    )
                    session.add(rating)
            
            session.commit()
            
            return {
                "users_updated": updated_users,
                "total_points_awarded": total_points_awarded
            }

class AnalyticsService:
    """Сервіс аналітики"""
    
    @staticmethod
    def get_engagement_stats() -> Dict[str, Any]:
        """Статистика залученості користувачів"""
        with get_db_session() as session:
            # Активні користувачі за різні періоди
            now = datetime.utcnow()
            
            active_today = session.query(User).filter(
                User.last_activity >= now.date()
            ).count()
            
            active_week = session.query(User).filter(
                User.last_activity >= (now - timedelta(days=7))
            ).count()
            
            active_month = session.query(User).filter(
                User.last_activity >= (now - timedelta(days=30))
            ).count()
            
            # Статистика контенту
            content_today = session.query(Content).filter(
                Content.created_at >= now.date()
            ).count()
            
            # Статистика взаємодій
            interactions_today = session.query(Rating).filter(
                Rating.created_at >= now.date()
            ).count()
            
            return {
                "active_users": {
                    "today": active_today,
                    "week": active_week,
                    "month": active_month
                },
                "content_submission": {
                    "today": content_today
                },
                "interactions": {
                    "today": interactions_today
                },
                "engagement_rate": {
                    "daily": (interactions_today / max(active_today, 1)) * 100,
                    "weekly": (session.query(Rating).filter(
                        Rating.created_at >= (now - timedelta(days=7))
                    ).count() / max(active_week, 1)) * 100
                }
            }
    
    @staticmethod
    def get_content_performance() -> Dict[str, Any]:
        """Аналіз ефективності контенту"""
        with get_db_session() as session:
            # ТОП контент за різними метриками
            top_by_views = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).order_by(Content.views.desc()).limit(5).all()
            
            top_by_engagement = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).order_by((Content.likes + Content.dislikes).desc()).limit(5).all()
            
            # Статистика по типах контенту
            content_type_stats = {}
            for content_type in ContentType:
                count = session.query(Content).filter(
                    Content.content_type == content_type,
                    Content.status == ContentStatus.APPROVED
                ).count()
                
                avg_views = session.query(Content.views).filter(
                    Content.content_type == content_type,
                    Content.status == ContentStatus.APPROVED
                ).scalar() or 0
                
                content_type_stats[content_type.value] = {
                    "count": count,
                    "avg_views": avg_views / max(count, 1)
                }
            
            return {
                "top_by_views": [
                    {
                        "id": c.id,
                        "text": (c.text[:100] + "...") if c.text and len(c.text) > 100 else c.text,
                        "views": c.views
                    }
                    for c in top_by_views
                ],
                "top_by_engagement": [
                    {
                        "id": c.id,
                        "text": (c.text[:100] + "...") if c.text and len(c.text) > 100 else c.text,
                        "engagement": c.likes + c.dislikes
                    }
                    for c in top_by_engagement
                ],
                "by_content_type": content_type_stats
            }

class NotificationService:
    """Сервіс сповіщень адміністраторів"""
    
    @staticmethod
    def get_pending_notifications() -> Dict[str, Any]:
        """Отримання списку очікуючих сповіщень"""
        with get_db_session() as session:
            # Контент на модерації
            pending_content = session.query(Content).filter(
                Content.status == ContentStatus.PENDING
            ).count()
            
            # Нові користувачі за добу
            new_users = session.query(User).filter(
                User.last_activity >= datetime.utcnow().date()
            ).count()
            
            # Проблемний контент (багато дизлайків)
            problematic_content = session.query(Content).filter(
                Content.dislikes > Content.likes * 2,
                Content.status == ContentStatus.APPROVED
            ).count()
            
            return {
                "pending_moderation": pending_content,
                "new_users_today": new_users,
                "problematic_content": problematic_content,
                "needs_attention": pending_content > 0 or problematic_content > 0
            }