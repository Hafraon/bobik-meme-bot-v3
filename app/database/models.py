#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class ContentType(Enum):
    """Типи контенту"""
    MEME = "meme"
    JOKE = "joke"
    ANEKDOT = "anekdot"

class ContentStatus(Enum):
    """Статуси контенту"""
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

class DuelStatus(Enum):
    """Статуси дуелей"""
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class User(Base):
    """Модель користувача"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Статистика
    points = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)
    total_approvals = Column(Integer, default=0)
    total_duels = Column(Integer, default=0)
    
    # Налаштування
    daily_notifications = Column(Boolean, default=True)
    language = Column(String(10), default="uk")
    timezone = Column(String(50), default="Europe/Kiev")
    
    # Системні поля
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime, default=func.now())
    
    # Зв'язки
    content = relationship("Content", back_populates="author")
    ratings = relationship("Rating", back_populates="user")
    duel_votes = relationship("DuelVote", back_populates="user")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"
    
    @property
    def rank(self):
        """Отримання рангу користувача по балах"""
        from config.settings import get_rank_by_points
        return get_rank_by_points(self.points)
    
    @property
    def full_name(self):
        """Повне ім'я користувача"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.username or f"User{self.user_id}"

class Content(Base):
    """Модель контенту"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(20), nullable=False)
    status = Column(String(20), default=ContentStatus.PENDING.value)
    
    # Контент
    text = Column(Text, nullable=False)
    media_url = Column(String(1000), nullable=True)
    media_type = Column(String(50), nullable=True)
    
    # Автор
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_user_id = Column(Integer, nullable=False)
    
    # Модерація
    moderated_by = Column(Integer, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Статистика
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Системні поля
    is_featured = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Зв'язки
    author = relationship("User", back_populates="content")
    ratings = relationship("Rating", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

class Rating(Base):
    """Модель рейтингу контенту"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Рейтинг
    rating = Column(Integer, nullable=False)  # 1-5 зірок
    reaction = Column(String(20), nullable=True)  # like, dislike, love, laugh
    
    # Системні поля
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, content_id={self.content_id}, rating={self.rating})>"

class Duel(Base):
    """Модель дуелі жартів"""
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True)
    status = Column(String(20), default=DuelStatus.ACTIVE.value)
    
    # Контенти для дуелі
    content1_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    content2_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Створювач дуелі
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Результати
    winner_content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    content1_votes = Column(Integer, default=0)
    content2_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Налаштування
    voting_duration = Column(Integer, default=300)  # секунд
    min_votes = Column(Integer, default=3)
    
    # Системні поля
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    # Зв'язки
    content1 = relationship("Content", foreign_keys=[content1_id])
    content2 = relationship("Content", foreign_keys=[content2_id])
    winner_content = relationship("Content", foreign_keys=[winner_content_id])
    creator = relationship("User")
    votes = relationship("DuelVote", back_populates="duel")
    
    def __repr__(self):
        return f"<Duel(id={self.id}, status={self.status})>"

class DuelVote(Base):
    """Модель голосування в дуелі"""
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True)
    duel_id = Column(Integer, ForeignKey("duels.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Системні поля
    created_at = Column(DateTime, default=func.now())
    
    # Зв'язки
    duel = relationship("Duel", back_populates="votes")
    user = relationship("User", back_populates="duel_votes")
    content = relationship("Content")
    
    def __repr__(self):
        return f"<DuelVote(duel_id={self.duel_id}, user_id={self.user_id})>"

class AdminAction(Base):
    """Модель дій адміністратора"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True)  # user, content, duel
    target_id = Column(Integer, nullable=True)
    
    # Деталі дії
    description = Column(Text, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    
    # Системні поля
    created_at = Column(DateTime, default=func.now())
    ip_address = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<AdminAction(admin_id={self.admin_id}, action={self.action_type})>"

class BotStatistics(Base):
    """Модель статистики бота"""
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=func.now())
    
    # Користувачі
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    
    # Контент
    total_content = Column(Integer, default=0)
    new_content = Column(Integer, default=0)
    approved_content = Column(Integer, default=0)
    rejected_content = Column(Integer, default=0)
    
    # Активність
    total_messages = Column(Integer, default=0)
    total_commands = Column(Integer, default=0)
    total_reactions = Column(Integer, default=0)
    
    # Дуелі
    total_duels = Column(Integer, default=0)
    new_duels = Column(Integer, default=0)
    finished_duels = Column(Integer, default=0)
    
    # Системні метрики
    uptime_seconds = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<BotStatistics(date={self.date}, users={self.total_users})>"