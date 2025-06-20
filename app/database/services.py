#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Global database objects
engine = None
SessionLocal = None

def init_database(database_url: str) -> bool:
    """Ініціалізація бази даних"""
    global engine, SessionLocal
    
    try:
        from .models import Base
        
        # Створення engine
        if database_url.startswith('sqlite'):
            engine = create_engine(database_url, echo=False)
        else:
            engine = create_engine(
                database_url, 
                echo=False, 
                pool_pre_ping=True,
                pool_recycle=3600
            )
        
        # Створення session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Створення таблиць
        Base.metadata.create_all(engine)
        
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False

@contextmanager
def get_db_session():
    """Контекстний менеджер для сесії БД"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

# ===== КОРИСТУВАЧІ =====

def get_or_create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> Optional[Dict]:
    """Отримання або створення користувача"""
    try:
        from .models import User
        
        with get_db_session() as session:
            # Пошук існуючого користувача
            user = session.query(User).filter(User.user_id == user_id).first()
            
            if user:
                # Оновлення інформації
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                
                user.last_activity = datetime.now()
                user.updated_at = datetime.now()
                
            else:
                # Створення нового користувача
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    created_at=datetime.now(),
                    last_activity=datetime.now()
                )
                session.add(user)
            
            session.commit()
            
            return {
                'id': user.id,
                'user_id': user.user_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'points': user.points,
                'rank': user.rank,
                'created_at': user.created_at
            }
            
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {e}")
        return None

def update_user_points(user_id: int, points_change: int, reason: str = "") -> bool:
    """Оновлення балів користувача"""
    try:
        from .models import User
        
        with get_db_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            
            if user:
                old_points = user.points
                user.points = max(0, user.points + points_change)
                user.updated_at = datetime.now()
                
                session.commit()
                
                logger.info(f"User {user_id} points: {old_points} -> {user.points} ({reason})")
                return True
            else:
                logger.warning(f"User {user_id} not found for points update")
                return False
                
    except Exception as e:
        logger.error(f"Error updating user points: {e}")
        return False

def get_user_stats(user_id: int) -> Optional[Dict]:
    """Отримання статистики користувача"""
    try:
        from .models import User
        
        with get_db_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            
            if user:
                return {
                    'user_id': user.user_id,
                    'points': user.points,
                    'rank': user.rank,
                    'total_views': user.total_views,
                    'total_likes': user.total_likes,
                    'total_submissions': user.total_submissions,
                    'total_approvals': user.total_approvals,
                    'total_duels': user.total_duels,
                    'created_at': user.created_at,
                    'last_activity': user.last_activity
                }
            return None
            
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return None

def get_top_users(limit: int = 10) -> List[Dict]:
    """Отримання топ користувачів по балах"""
    try:
        from .models import User
        
        with get_db_session() as session:
            users = session.query(User)\
                          .filter(User.is_active == True)\
                          .order_by(User.points.desc())\
                          .limit(limit)\
                          .all()
            
            return [
                {
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'username': user.username,
                    'points': user.points,
                    'rank': user.rank
                }
                for user in users
            ]
            
    except Exception as e:
        logger.error(f"Error getting top users: {e}")
        return []

# ===== КОНТЕНТ =====

def add_content(author_user_id: int, content_type: str, text: str, media_url: str = None) -> Optional[int]:
    """Додавання нового контенту"""
    try:
        from .models import Content, User
        
        with get_db_session() as session:
            # Знаходимо автора
            user = session.query(User).filter(User.user_id == author_user_id).first()
            if not user:
                logger.warning(f"User {author_user_id} not found for content creation")
                return None
            
            # Створюємо контент
            content = Content(
                content_type=content_type,
                text=text,
                media_url=media_url,
                author_id=user.id,
                author_user_id=author_user_id,
                created_at=datetime.now()
            )
            
            session.add(content)
            session.commit()
            
            # Оновлюємо статистику користувача
            user.total_submissions += 1
            session.commit()
            
            logger.info(f"Content {content.id} created by user {author_user_id}")
            return content.id
            
    except Exception as e:
        logger.error(f"Error adding content: {e}")
        return None

def get_random_approved_content(content_type: str = None) -> Optional[Dict]:
    """Отримання випадкового схваленого контенту"""
    try:
        from .models import Content, ContentStatus
        
        with get_db_session() as session:
            query = session.query(Content)\
                          .filter(Content.status == ContentStatus.APPROVED.value)
            
            if content_type:
                query = query.filter(Content.content_type == content_type)
            
            content = query.order_by(func.random()).first()
            
            if content:
                # Збільшуємо лічильник переглядів
                content.views += 1
                session.commit()
                
                return {
                    'id': content.id,
                    'type': content.content_type,
                    'text': content.text,
                    'media_url': content.media_url,
                    'views': content.views,
                    'likes': content.likes,
                    'author_user_id': content.author_user_id
                }
            return None
            
    except Exception as e:
        logger.error(f"Error getting random content: {e}")
        return None

# ===== СТАТИСТИКА ТА АНАЛІТИКА =====

def get_basic_stats() -> Dict[str, int]:
    """Отримання базової статистики бота"""
    try:
        from .models import User, Content, Duel, ContentStatus
        
        with get_db_session() as session:
            total_users = session.query(User).filter(User.is_active == True).count()
            total_content = session.query(Content).count()
            approved_content = session.query(Content).filter(Content.status == ContentStatus.APPROVED.value).count()
            pending_content = session.query(Content).filter(Content.status == ContentStatus.PENDING.value).count()
            rejected_content = session.query(Content).filter(Content.status == ContentStatus.REJECTED.value).count()
            total_duels = session.query(Duel).count()
            
            return {
                'total_users': total_users,
                'total_content': total_content,
                'approved_content': approved_content,
                'pending_content': pending_content,
                'rejected_content': rejected_content,
                'total_duels': total_duels
            }
            
    except Exception as e:
        logger.error(f"Error getting basic stats: {e}")
        return {
            'total_users': 0,
            'total_content': 0,
            'approved_content': 0,
            'pending_content': 0,
            'rejected_content': 0,
            'total_duels': 0
        }

def get_detailed_admin_stats() -> Dict[str, Any]:
    """Отримання детальної статистики для адміна"""
    try:
        from .models import User, Content, ContentStatus, AdminAction
        from datetime import datetime, timedelta
        
        with get_db_session() as session:
            # Загальна статистика
            total_users = session.query(User).filter(User.is_active == True).count()
            
            # Активність за останній день
            yesterday = datetime.now() - timedelta(days=1)
            active_today = session.query(User).filter(
                User.last_activity >= yesterday,
                User.is_active == True
            ).count()
            
            # Нові користувачі за тиждень
            week_ago = datetime.now() - timedelta(days=7)
            new_users_week = session.query(User).filter(
                User.created_at >= week_ago,
                User.is_active == True
            ).count()
            
            # Статистика контенту
            total_content = session.query(Content).count()
            approved_content = session.query(Content).filter(Content.status == ContentStatus.APPROVED.value).count()
            pending_content = session.query(Content).filter(Content.status == ContentStatus.PENDING.value).count()
            rejected_content = session.query(Content).filter(Content.status == ContentStatus.REJECTED.value).count()
            
            # Контент за тиждень
            new_content_week = session.query(Content).filter(Content.created_at >= week_ago).count()
            
            # Топ користувачі по балах
            top_users = session.query(User).filter(User.is_active == True).order_by(User.points.desc()).limit(5).all()
            
            # Активність адміна
            admin_actions_week = session.query(AdminAction).filter(AdminAction.created_at >= week_ago).count()
            
            return {
                'total_users': total_users,
                'active_today': active_today,
                'new_users_week': new_users_week,
                'total_content': total_content,
                'approved_content': approved_content,
                'pending_content': pending_content,
                'rejected_content': rejected_content,
                'new_content_week': new_content_week,
                'admin_actions_week': admin_actions_week,
                'top_users': [
                    {
                        'user_id': user.user_id,
                        'first_name': user.first_name,
                        'username': user.username,
                        'points': user.points,
                        'rank': user.rank
                    }
                    for user in top_users
                ],
                'approval_rate': round((approved_content / max(total_content, 1)) * 100, 1) if total_content > 0 else 0
            }
            
    except Exception as e:
        logger.error(f"Error getting detailed admin stats: {e}")
        return get_basic_stats()  # Fallback до базової статистики

def get_pending_content_list(limit: int = 10) -> List[Dict]:
    """Отримання списку контенту на модерації"""
    try:
        from .models import Content, ContentStatus, User
        
        with get_db_session() as session:
            pending_content = session.query(Content)\
                                   .filter(Content.status == ContentStatus.PENDING.value)\
                                   .order_by(Content.created_at.asc())\
                                   .limit(limit)\
                                   .all()
            
            result = []
            for content in pending_content:
                # Отримуємо автора
                author = session.query(User).filter(User.id == content.author_id).first()
                author_name = "Невідомий"
                if author:
                    author_name = author.first_name or author.username or f"User{author.user_id}"
                
                result.append({
                    'id': content.id,
                    'type': content.content_type,
                    'text': content.text,
                    'author_name': author_name,
                    'author_user_id': content.author_user_id,
                    'created_at': content.created_at
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting pending content list: {e}")
        return []

def get_content_by_id(content_id: int) -> Optional[Dict]:
    """Отримання контенту по ID"""
    try:
        from .models import Content, User
        
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if not content:
                return None
            
            # Отримуємо автора
            author = session.query(User).filter(User.id == content.author_id).first()
            author_name = "Невідомий"
            if author:
                author_name = author.first_name or author.username or f"User{author.user_id}"
            
            return {
                'id': content.id,
                'type': content.content_type,
                'status': content.status,
                'text': content.text,
                'media_url': content.media_url,
                'author_name': author_name,
                'author_user_id': content.author_user_id,
                'views': content.views,
                'likes': content.likes,
                'dislikes': content.dislikes,
                'created_at': content.created_at,
                'moderated_at': content.moderated_at,
                'moderated_by': content.moderated_by,
                'rejection_reason': content.rejection_reason
            }
            
    except Exception as e:
        logger.error(f"Error getting content by ID {content_id}: {e}")
        return None

# ===== ТЕСТУВАННЯ =====

def test_database_connection() -> bool:
    """Тестування з'єднання з базою даних"""
    try:
        with get_db_session() as session:
            # Простий тестовий запит
            result = session.execute("SELECT 1").fetchone()
            return result is not None
            
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False