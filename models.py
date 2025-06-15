#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Моделі бази даних 🧠😂🔥
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum as SQLEnum,
    ForeignKey, Integer, String, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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
    submissions = relationship("Content", back_populates="author")
    ratings = relationship("Rating", back_populates="user")
    duel_initiations = relationship("Duel", foreign_keys="Duel.initiator_id", back_populates="initiator")
    duel_participations = relationship("Duel", foreign_keys="Duel.opponent_id", back_populates="opponent")
    votes = relationship("DuelVote", back_populates="voter")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, points={self.points})>"

class Content(Base):
    """Модель контенту (меми та анекдоти)"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Основна інформація
    content_type = Column(SQLEnum(ContentType), nullable=False)
    text = Column(Text, nullable=True)  # Текст анекдоту або підпис до мему
    file_id = Column(String(255), nullable=True)  # Telegram file_id для мемів
    file_url = Column(String(500), nullable=True)  # URL файлу
    
    # Модерація
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    moderator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    moderation_comment = Column(Text, nullable=True)
    
    # Статистика
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    moderated_at = Column(DateTime, nullable=True)
    
    # Зв'язки
    author = relationship("User", foreign_keys=[author_id], back_populates="submissions")
    moderator = relationship("User", foreign_keys=[moderator_id])
    ratings = relationship("Rating", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

class Rating(Base):
    """Модель оцінок контенту"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Тип дії
    action_type = Column(String(50), nullable=False)  # "like", "dislike", "view", "share"
    points_awarded = Column(Integer, default=0)
    
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
    voting_ends_at = Column(DateTime, nullable=True)
    is_public = Column(Boolean, default=True)
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Зв'язки
    initiator = relationship("User", foreign_keys=[initiator_id], back_populates="duel_initiations")
    opponent = relationship("User", foreign_keys=[opponent_id], back_populates="duel_participations")
    winner = relationship("User", foreign_keys=[winner_id])
    initiator_content = relationship("Content", foreign_keys=[initiator_content_id])
    opponent_content = relationship("Content", foreign_keys=[opponent_content_id])
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
    
    # Зв'язки
    admin = relationship("User")
    
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