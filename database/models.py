#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Моделі бази даних (ВИПРАВЛЕНО enum для PostgreSQL) 🧠😂🔥
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum as SQLEnum,
    ForeignKey, Integer, String, Text, Float, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# 🔥 ВИПРАВЛЕНІ ENUM'И ДЛЯ POSTGRESQL
class ContentType(Enum):
    """Тип контенту - ВИПРАВЛЕНО для PostgreSQL"""
    MEME = "MEME"  # ✅ Верхній регістр
    JOKE = "JOKE"  # ✅ Верхній регістр

class ContentStatus(Enum):
    """Статус контенту - ВИПРАВЛЕНО для PostgreSQL"""
    PENDING = "PENDING"      # ✅ Верхній регістр
    APPROVED = "APPROVED"    # ✅ Верхній регістр  
    REJECTED = "REJECTED"    # ✅ Верхній регістр

class DuelStatus(Enum):
    """Статус дуелі"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class User(Base):
    """Модель користувача"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Гейміфікація
    points = Column(Integer, default=0)
    rank = Column(String(100), default="🤡 Новачок")
    
    # Налаштування
    daily_subscription = Column(Boolean, default=False)
    language_code = Column(String(10), default="uk")
    
    # Статистика
    jokes_submitted = Column(Integer, default=0)
    jokes_approved = Column(Integer, default=0)
    memes_submitted = Column(Integer, default=0)
    memes_approved = Column(Integer, default=0)
    reactions_given = Column(Integer, default=0)
    duels_won = Column(Integer, default=0)
    duels_lost = Column(Integer, default=0)
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    authored_content = relationship("Content", back_populates="author", foreign_keys="Content.author_id")
    moderated_content = relationship("Content", back_populates="moderator", foreign_keys="Content.moderator_id")
    ratings = relationship("Rating", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class Content(Base):
    """Модель контенту"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 🔥 ВИПРАВЛЕНО: Використовуємо правильні enum значення
    content_type = Column(SQLEnum(ContentType), default=ContentType.JOKE)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)  # ✅ ВИПРАВЛЕНО
    
    text = Column(Text, nullable=True)
    file_id = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    
    # Автор і модератор
    author_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    moderator_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    # Модерація
    moderation_comment = Column(Text, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    
    # Статистика
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    reports = Column(Integer, default=0)
    
    # Метрики якості
    quality_score = Column(Float, default=0.0)
    popularity_score = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    virality_score = Column(Float, default=0.0)
    
    # Класифікація
    topic = Column(String(100), nullable=True)
    style = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=True)
    target_age = Column(String(20), default="18+")
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_shown_at = Column(DateTime, nullable=True)
    
    # Метадані
    original_message_id = Column(String(100), nullable=True)
    hashtags = Column(Text, nullable=True)
    mentions = Column(Text, nullable=True)
    
    # Зв'язки
    author = relationship("User", back_populates="authored_content", foreign_keys=[author_id])
    moderator = relationship("User", back_populates="moderated_content", foreign_keys=[moderator_id])
    ratings = relationship("Rating", back_populates="content")
    
    # Індекси
    __table_args__ = (
        Index('ix_content_status', 'status'),
        Index('ix_content_type', 'content_type'),
        Index('ix_content_author_id', 'author_id'),
        Index('ix_content_created_at', 'created_at'),
        Index('ix_content_quality_score', 'quality_score'),
        Index('ix_content_popularity_score', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

class Rating(Base):
    """Модель оцінки контенту"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    content_id = Column(Integer, ForeignKey('content.id'), nullable=False)
    
    action_type = Column(String(50), nullable=False)  # 'like', 'dislike', 'share', 'report'
    points_awarded = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")
    
    # Унікальність
    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', 'action_type', name='unique_user_content_action'),
        Index('ix_rating_user_id', 'user_id'),
        Index('ix_rating_content_id', 'content_id'),
    )
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, content_id={self.content_id}, action={self.action_type})>"

class Duel(Base):
    """Модель дуелі жартів"""
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Учасники
    challenger_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    opponent_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    # Контент
    challenger_content_id = Column(Integer, ForeignKey('content.id'), nullable=True)
    opponent_content_id = Column(Integer, ForeignKey('content.id'), nullable=True)
    
    # Статус і результати
    status = Column(SQLEnum(DuelStatus), default=DuelStatus.ACTIVE)
    winner_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    # Голосування
    challenger_votes = Column(Integer, default=0)
    opponent_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Зв'язки
    challenger = relationship("User", foreign_keys=[challenger_id])
    opponent = relationship("User", foreign_keys=[opponent_id])
    winner = relationship("User", foreign_keys=[winner_id])
    challenger_content = relationship("Content", foreign_keys=[challenger_content_id])
    opponent_content = relationship("Content", foreign_keys=[opponent_content_id])
    votes = relationship("DuelVote", back_populates="duel")
    
    def __repr__(self):
        return f"<Duel(id={self.id}, challenger_id={self.challenger_id}, status={self.status})>"

class DuelVote(Base):
    """Модель голосу в дуелі"""
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    duel_id = Column(Integer, ForeignKey('duels.id'), nullable=False)
    voter_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    
    voted_for = Column(String(20), nullable=False)  # 'challenger' або 'opponent'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    duel = relationship("Duel", back_populates="votes")
    voter = relationship("User")
    
    # Унікальність
    __table_args__ = (
        UniqueConstraint('duel_id', 'voter_id', name='unique_duel_voter'),
        Index('ix_duel_vote_duel_id', 'duel_id'),
    )
    
    def __repr__(self):
        return f"<DuelVote(duel_id={self.duel_id}, voter_id={self.voter_id}, voted_for={self.voted_for})>"

class AdminAction(Base):
    """Модель дій адміністратора"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)  # 'user', 'content', 'duel'
    target_id = Column(String(100), nullable=False)
    
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    admin = relationship("User")
    
    def __repr__(self):
        return f"<AdminAction(admin_id={self.admin_id}, action={self.action_type})>"

class BotStatistics(Base):
    """Модель статистики бота"""
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Загальна статистика
    total_users = Column(Integer, default=0)
    active_users_today = Column(Integer, default=0)
    active_users_week = Column(Integer, default=0)
    active_users_month = Column(Integer, default=0)
    
    # Контент
    total_content = Column(Integer, default=0)
    pending_content = Column(Integer, default=0)
    approved_content = Column(Integer, default=0)
    rejected_content = Column(Integer, default=0)
    
    # Активність
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_dislikes = Column(Integer, default=0)
    
    # Дуелі
    active_duels = Column(Integer, default=0)
    completed_duels = Column(Integer, default=0)
    
    # Часова мітка
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BotStatistics(total_users={self.total_users}, updated_at={self.updated_at})>"