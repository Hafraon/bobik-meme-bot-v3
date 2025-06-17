#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Розширені моделі бази даних (ВИПРАВЛЕНІ RELATIONSHIPS) 🧠😂🔥
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum as SQLEnum,
    ForeignKey, Integer, String, Text, Float, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ContentType(Enum):
    """Тип контенту"""
    MEME = "meme"
    JOKE = "joke"

class ContentStatus(Enum):
    """Статус контенту"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DuelStatus(Enum):
    """Статус дуелі"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# НОВІ ENUM'И ДЛЯ ПЕРСОНАЛІЗАЦІЇ
class PreferenceType(Enum):
    """Типи вподобань"""
    TOPIC = "topic"
    STYLE = "style"
    LENGTH = "length"

class User(Base):
    """Модель користувача - РОЗШИРЕНА"""
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
    
    # НОВІ ПОЛЯ ДЛЯ ПЕРСОНАЛІЗАЦІЇ!
    preferred_content_type = Column(String(20), default="mixed")  # "jokes", "memes", "mixed"
    reset_history_days = Column(Integer, default=7)  # Через скільки днів скидати історію
    last_history_reset = Column(DateTime, default=datetime.utcnow)
    
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
    
    # ✅ ВИПРАВЛЕНІ ЗВ'ЯЗКИ з чіткими foreign_keys!
    submissions = relationship(
        "Content", 
        foreign_keys="Content.author_id",
        back_populates="author"
    )
    moderated_content = relationship(
        "Content", 
        foreign_keys="Content.moderator_id",
        back_populates="moderator"
    )
    ratings = relationship("Rating", back_populates="user")
    duel_initiations = relationship(
        "Duel", 
        foreign_keys="Duel.initiator_id", 
        back_populates="initiator"
    )
    duel_participations = relationship(
        "Duel", 
        foreign_keys="Duel.opponent_id", 
        back_populates="opponent"
    )
    duel_wins = relationship(
        "Duel", 
        foreign_keys="Duel.winner_id", 
        back_populates="winner"
    )
    votes = relationship("DuelVote", back_populates="voter")
    content_views = relationship("ContentView", back_populates="user")  # НОВЕ!
    preferences = relationship("UserPreference", back_populates="user")  # НОВЕ!
    admin_actions = relationship(
        "AdminAction", 
        foreign_keys="AdminAction.admin_id",
        back_populates="admin"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, points={self.points})>"

class Content(Base):
    """Модель контенту - РОЗШИРЕНА"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Основна інформація
    content_type = Column(SQLEnum(ContentType), nullable=False)
    text = Column(Text, nullable=True)  # Текст анекдоту або підпис до мему
    file_id = Column(String(255), nullable=True)  # Telegram file_id для мемів
    file_url = Column(String(500), nullable=True)  # URL файлу
    
    # НОВІ ПОЛЯ ДЛЯ КАТЕГОРИЗАЦІЇ!
    topic = Column(String(100), nullable=True)  # "programming", "life", "work", "family"
    style = Column(String(100), nullable=True)  # "irony", "sarcasm", "kind", "absurd"
    difficulty = Column(Integer, default=1)  # 1-5, складність для розуміння
    
    # Модерація
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    moderator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    moderation_comment = Column(Text, nullable=True)
    
    # РОЗШИРЕНА СТАТИСТИКА!
    views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)  # НОВЕ!
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    shares = Column(Integer, default=0)  # НОВЕ!
    
    # НОВІ ПОКАЗНИКИ ПОПУЛЯРНОСТІ!
    popularity_score = Column(Float, default=0.0)  # Розрахункова популярність
    trending_score = Column(Float, default=0.0)  # Популярність за останні дні
    quality_score = Column(Float, default=0.0)  # Оцінка якості від модераторів
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    moderated_at = Column(DateTime, nullable=True)
    last_shown = Column(DateTime, nullable=True)  # НОВЕ! Коли востаннє показували
    
    # ✅ ВИПРАВЛЕНІ ЗВ'ЯЗКИ з чіткими foreign_keys!
    author = relationship(
        "User", 
        foreign_keys=[author_id], 
        back_populates="submissions"
    )
    moderator = relationship(
        "User", 
        foreign_keys=[moderator_id],
        back_populates="moderated_content"
    )
    ratings = relationship("Rating", back_populates="content")
    content_views = relationship("ContentView", back_populates="content")  # НОВЕ!
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

# НОВА ТАБЛИЦЯ ДЛЯ ВІДСТЕЖЕННЯ ПЕРЕГЛЯДІВ!
class ContentView(Base):
    """Відстеження переглядів контенту без повторів"""
    __tablename__ = "content_views"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Деталі перегляду
    viewed_at = Column(DateTime, default=datetime.utcnow)
    view_duration = Column(Integer, nullable=True)  # Секунди
    device_type = Column(String(50), nullable=True)  # "mobile", "desktop"
    
    # Контекст перегляду
    source = Column(String(50), default="random")  # "random", "search", "duel", "daily"
    session_id = Column(String(100), nullable=True)  # Ідентифікатор сесії
    
    # Індекси для швидкого пошуку
    __table_args__ = (
        Index('idx_user_content_date', 'user_id', 'content_id', 'viewed_at'),
    )
    
    # Зв'язки
    user = relationship("User", back_populates="content_views")
    content = relationship("Content", back_populates="content_views")
    
    def __repr__(self):
        return f"<ContentView(user_id={self.user_id}, content_id={self.content_id})>"

# НОВА ТАБЛИЦЯ ДЛЯ ВПОДОБАНЬ КОРИСТУВАЧІВ!
class UserPreference(Base):
    """Вподобання користувачів для персоналізації"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # Тип вподобання
    preference_type = Column(SQLEnum(PreferenceType), nullable=False)
    preference_value = Column(String(100), nullable=False)  # Значення вподобання
    weight = Column(Float, default=1.0)  # Вага вподобання (наскільки важливо)
    
    # Як було отримано
    source = Column(String(50), default="implicit")  # "explicit", "implicit", "ai_detected"
    confidence = Column(Float, default=0.5)  # Впевненість в точності
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Унікальне обмеження - одне вподобання на тип
    __table_args__ = (
        UniqueConstraint('user_id', 'preference_type', 'preference_value', name='uq_user_pref'),
    )
    
    # Зв'язки
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, type={self.preference_type}, value={self.preference_value})>"

# НОВА ТАБЛИЦЯ ДЛЯ СТАТИСТИКИ ПОПУЛЯРНОСТІ!
class ContentPopularity(Base):
    """Статистика популярності контенту по часу"""
    __tablename__ = "content_popularity"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Статистика за період
    date = Column(DateTime, default=datetime.utcnow)
    period_type = Column(String(20), default="daily")  # "hourly", "daily", "weekly"
    
    # Метрики
    views_count = Column(Integer, default=0)
    unique_views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    dislikes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Розрахункові показники
    engagement_rate = Column(Float, default=0.0)  # (likes + dislikes) / views
    satisfaction_rate = Column(Float, default=0.0)  # likes / (likes + dislikes)
    virality_score = Column(Float, default=0.0)  # Наскільки швидко поширюється
    
    # Зв'язки
    content = relationship("Content")
    
    def __repr__(self):
        return f"<ContentPopularity(content_id={self.content_id}, date={self.date})>"

# ІСНУЮЧІ МОДЕЛІ З ВИПРАВЛЕНИМИ RELATIONSHIPS
class Rating(Base):
    """Модель оцінок контенту - РОЗШИРЕНА"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Тип дії
    action_type = Column(String(50), nullable=False)  # "like", "dislike", "view", "share", "report"
    points_awarded = Column(Integer, default=0)
    
    # НОВІ ПОЛЯ!
    reaction_time = Column(Float, nullable=True)  # Час реакції в секундах
    comment = Column(Text, nullable=True)  # Коментар користувача
    emotion_detected = Column(String(50), nullable=True)  # "happy", "funny", "boring"
    
    # Часова мітка
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, content_id={self.content_id}, action={self.action_type})>"

class Duel(Base):
    """Модель дуелі жартів"""
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Учасники
    initiator_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    opponent_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    # Контент дуелі
    initiator_content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    opponent_content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    
    # Статус та результати
    status = Column(SQLEnum(DuelStatus), default=DuelStatus.ACTIVE)
    winner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    # Голосування
    initiator_votes = Column(Integer, default=0)
    opponent_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Налаштування
    voting_ends_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    is_public = Column(Boolean, default=True)
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # ✅ ВИПРАВЛЕНІ ЗВ'ЯЗКИ з чіткими foreign_keys!
    initiator = relationship(
        "User", 
        foreign_keys=[initiator_id], 
        back_populates="duel_initiations"
    )
    opponent = relationship(
        "User", 
        foreign_keys=[opponent_id], 
        back_populates="duel_participations"
    )
    winner = relationship(
        "User", 
        foreign_keys=[winner_id],
        back_populates="duel_wins"
    )
    initiator_content = relationship(
        "Content", 
        foreign_keys=[initiator_content_id]
    )
    opponent_content = relationship(
        "Content", 
        foreign_keys=[opponent_content_id]
    )
    votes = relationship("DuelVote", back_populates="duel")
    
    def __repr__(self):
        return f"<Duel(id={self.id}, initiator={self.initiator_id}, opponent={self.opponent_id}, status={self.status})>"

class DuelVote(Base):
    """Модель голосів у дуелі"""
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    duel_id = Column(Integer, ForeignKey("duels.id"), nullable=False)
    voter_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # Голос: "initiator" або "opponent"
    vote_for = Column(String(20), nullable=False)
    
    # Часова мітка
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Унікальне обмеження - один голос від користувача
    __table_args__ = (
        UniqueConstraint('duel_id', 'voter_id', name='uq_duel_voter'),
    )
    
    # Зв'язки
    duel = relationship("Duel", back_populates="votes")
    voter = relationship("User", back_populates="votes")
    
    def __repr__(self):
        return f"<DuelVote(duel_id={self.duel_id}, voter_id={self.voter_id}, vote_for={self.vote_for})>"

class AdminAction(Base):
    """Модель дій адміністраторів"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # Тип дії
    action_type = Column(String(50), nullable=False)  # "approve", "reject", "ban", "unban"
    target_type = Column(String(50), nullable=False)  # "content", "user", "duel"
    target_id = Column(Integer, nullable=False)
    
    # Додаткова інформація
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Часова мітка
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ✅ ВИПРАВЛЕНИЙ ЗВ'ЯЗОК!
    admin = relationship(
        "User", 
        foreign_keys=[admin_id],
        back_populates="admin_actions"
    )
    
    def __repr__(self):
        return f"<AdminAction(admin_id={self.admin_id}, action={self.action_type}, target={self.target_type}:{self.target_id})>"

class BotStatistics(Base):
    """Модель статистики бота"""
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Дата статистики
    date = Column(DateTime, default=datetime.utcnow)
    
    # Загальна статистика
    total_users = Column(Integer, default=0)
    active_users_today = Column(Integer, default=0)
    new_users_today = Column(Integer, default=0)
    
    # Контент
    total_content = Column(Integer, default=0)
    pending_content = Column(Integer, default=0)
    approved_content_today = Column(Integer, default=0)
    
    # Дуелі
    active_duels = Column(Integer, default=0)
    completed_duels_today = Column(Integer, default=0)
    
    # Взаємодії
    commands_executed_today = Column(Integer, default=0)
    memes_sent_today = Column(Integer, default=0)
    jokes_sent_today = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<BotStatistics(date={self.date}, users={self.total_users})>"