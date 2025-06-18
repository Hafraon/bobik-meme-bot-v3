#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 РОБОЧІ МОДЕЛІ БД (ВИПРАВЛЕНО) 🧠😂🔥
ЗАМІНІТЬ ВЕСЬ ІСНУЮЧИЙ database/models.py НА ЦЕЙ КОД
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

Base = declarative_base()

# ===== ЕНУМИ =====

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

# ===== МОДЕЛЬ USER (ВИПРАВЛЕНА) =====

class User(Base):
    """Модель користувача з усіма необхідними полями"""
    __tablename__ = "users"
    
    # Основні поля
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)  # ✅ ГОЛОВНЕ ПОЛЕ!
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Статуси (ВИПРАВЛЕНО - додано is_active!)
    is_active = Column(Boolean, default=True, nullable=False)  # ✅ ВИПРАВЛЕНО!
    is_premium = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    
    # Гейміфікація
    total_points = Column(Integer, default=0)
    current_rank = Column(SQLEnum(UserRank), default=UserRank.NEWBIE)
    
    # Лічильники контенту
    jokes_submitted = Column(Integer, default=0)
    jokes_approved = Column(Integer, default=0)
    memes_submitted = Column(Integer, default=0)
    memes_approved = Column(Integer, default=0)
    
    # Лічильники активності
    likes_given = Column(Integer, default=0)
    dislikes_given = Column(Integer, default=0)
    comments_made = Column(Integer, default=0)
    content_views = Column(Integer, default=0)
    
    # Дуелі
    duels_won = Column(Integer, default=0)
    duels_lost = Column(Integer, default=0)
    duels_participated = Column(Integer, default=0)
    
    # Налаштування
    daily_subscription = Column(Boolean, default=False)
    last_daily_content = Column(DateTime, nullable=True)
    preferred_content_type = Column(String(20), default="mixed")
    
    # Метадані
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"

# ===== МОДЕЛЬ CONTENT =====

class Content(Base):
    """Модель контенту"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(SQLEnum(ContentType), default=ContentType.JOKE)
    text = Column(Text, nullable=True)
    file_id = Column(String(500), nullable=True)
    
    # Автор та модератор
    author_id = Column(Integer, nullable=False)  # ForeignKey до User.telegram_id
    moderator_id = Column(Integer, nullable=True)
    
    # Статус
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    moderation_comment = Column(Text, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    
    # Статистика
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Метадані
    topic = Column(String(50), default="general")
    style = Column(String(50), default="neutral")
    difficulty = Column(Integer, default=1)
    quality_score = Column(Float, default=0.5)
    popularity_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

# ===== МОДЕЛЬ RATING =====

class Rating(Base):
    """Модель оцінок"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ForeignKey до User.telegram_id
    content_id = Column(Integer, nullable=False)  # ForeignKey до Content.id
    
    rating = Column(Integer, nullable=False)  # 1 для like, -1 для dislike
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, content_id={self.content_id}, rating={self.rating})>"

# ===== МОДЕЛЬ DUEL =====

class Duel(Base):
    """Модель дуелей"""
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Учасники
    challenger_id = Column(Integer, nullable=False)
    opponent_id = Column(Integer, nullable=False)
    
    # Контент дуелі
    challenger_content_id = Column(Integer, nullable=False)
    opponent_content_id = Column(Integer, nullable=True)
    
    # Статус
    status = Column(String(20), default="waiting")
    winner_id = Column(Integer, nullable=True)
    
    # Голосування
    challenger_votes = Column(Integer, default=0)
    opponent_votes = Column(Integer, default=0)
    
    # Час
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    voting_ends_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Duel(id={self.id}, challenger={self.challenger_id}, opponent={self.opponent_id})>"

# ===== МОДЕЛЬ DUEL_VOTE =====

class DuelVote(Base):
    """Модель голосів у дуелях"""
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    duel_id = Column(Integer, nullable=False)
    voter_id = Column(Integer, nullable=False)
    
    vote = Column(String(20), nullable=False)  # "challenger" або "opponent"
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DuelVote(duel_id={self.duel_id}, voter_id={self.voter_id}, vote={self.vote})>"

# ===== МОДЕЛЬ ADMIN_ACTION =====

class AdminAction(Base):
    """Модель дій адміністраторів"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False)
    
    action_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin_id={self.admin_id}, action={self.action_type})>"

# ===== МОДЕЛЬ BOT_STATISTICS =====

class BotStatistics(Base):
    """Модель статистики бота"""
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Статистика користувачів
    total_users = Column(Integer, default=0)
    active_users_today = Column(Integer, default=0)
    active_users_week = Column(Integer, default=0)
    active_users_month = Column(Integer, default=0)
    
    # Статистика контенту
    total_content = Column(Integer, default=0)
    approved_content = Column(Integer, default=0)
    pending_content = Column(Integer, default=0)
    rejected_content = Column(Integer, default=0)
    
    # Дуелі
    total_duels = Column(Integer, default=0)
    active_duels = Column(Integer, default=0)
    completed_duels = Column(Integer, default=0)
    
    # Метадані
    date = Column(DateTime, server_default=func.now(), unique=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<BotStatistics(date={self.date}, users={self.total_users})>"

# ===== ДОДАТКОВІ ПОЛЯ ДЛЯ СУМІСНОСТІ =====

# Додаємо поля які можуть бути потрібні для повної сумісності
try:
    # Додаткові поля для Content якщо потрібно
    if not hasattr(Content, 'reports'):
        Content.reports = Column(Integer, default=0)
    if not hasattr(Content, 'target_age'):
        Content.target_age = Column(String(20), default="all")
    if not hasattr(Content, 'engagement_rate'):
        Content.engagement_rate = Column(Float, default=0.0)
    if not hasattr(Content, 'virality_score'):
        Content.virality_score = Column(Float, default=0.0)
    if not hasattr(Content, 'last_shown_at'):
        Content.last_shown_at = Column(DateTime, nullable=True)
    if not hasattr(Content, 'original_message_id'):
        Content.original_message_id = Column(Integer, nullable=True)
    if not hasattr(Content, 'hashtags'):
        Content.hashtags = Column(Text, nullable=True)
    if not hasattr(Content, 'mentions'):
        Content.mentions = Column(Text, nullable=True)
        
except Exception:
    # Якщо не вдається додати поля, просто ігноруємо
    pass

# ===== ІНДЕКСИ ДЛЯ ОПТИМІЗАЦІЇ =====

from sqlalchemy import Index

# Індекс для швидкого пошуку користувачів
Index('idx_user_telegram_id', User.telegram_id)
Index('idx_user_active', User.is_active, User.last_activity)

# Індекс для контенту
Index('idx_content_status', Content.status)
Index('idx_content_author', Content.author_id)

# Індекс для рейтингів
Index('idx_rating_user_content', Rating.user_id, Rating.content_id)