#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Моделі бази даних (ВИПРАВЛЕНО User модель) 🧠😂🔥
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
    __tablename__ = "users"
    
    # Основні поля
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # ВИПРАВЛЕНО: додаємо is_active поле
    is_active = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Статистика
    total_points = Column(Integer, default=0)
    current_rank = Column(SQLEnum(UserRank), default=UserRank.NEWBIE)
    
    # Лічильники активності
    jokes_submitted = Column(Integer, default=0)
    jokes_approved = Column(Integer, default=0)
    memes_submitted = Column(Integer, default=0)
    memes_approved = Column(Integer, default=0)
    
    # Лічильники взаємодії
    likes_given = Column(Integer, default=0)
    dislikes_given = Column(Integer, default=0)
    comments_made = Column(Integer, default=0)
    
    # Дуелі
    duels_won = Column(Integer, default=0)
    duels_lost = Column(Integer, default=0)
    duels_participated = Column(Integer, default=0)
    
    # Щоденна розсилка
    daily_subscription = Column(Boolean, default=False)
    last_daily_content = Column(DateTime, nullable=True)
    
    # Персоналізація
    preferred_content_type = Column(String(20), default="mixed")  # joke, meme, mixed
    content_difficulty = Column(Integer, default=1)  # 1-5
    
    # Метадані
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime, server_default=func.now())
    
    # Зв'язки
    submitted_content = relationship("Content", foreign_keys="[Content.author_id]", back_populates="author")
    moderated_content = relationship("Content", foreign_keys="[Content.moderator_id]", back_populates="moderator")
    ratings = relationship("Rating", back_populates="user")
    admin_actions = relationship("AdminAction", back_populates="admin")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    def get_rank_info(self):
        """Отримання інформації про ранг"""
        rank_requirements = {
            UserRank.NEWBIE: 0,
            UserRank.JOKER: 50,
            UserRank.COMEDIAN: 150,
            UserRank.HUMORIST: 300,
            UserRank.MASTER: 600,
            UserRank.EXPERT: 1000,
            UserRank.VIRTUOSO: 1500,
            UserRank.LEGEND: 2500
        }
        
        current_points = self.total_points
        current_rank = self.current_rank
        
        # Знайти наступний ранг
        next_rank = None
        points_to_next = 0
        
        ranks = list(UserRank)
        current_index = ranks.index(current_rank)
        
        if current_index < len(ranks) - 1:
            next_rank = ranks[current_index + 1]
            points_to_next = rank_requirements[next_rank] - current_points
        
        return {
            "current_rank": current_rank.value,
            "current_points": current_points,
            "next_rank": next_rank.value if next_rank else None,
            "points_to_next": max(0, points_to_next) if next_rank else 0,
            "progress_percent": min(100, (current_points / rank_requirements.get(next_rank, current_points + 1)) * 100) if next_rank else 100
        }

# ===== ІНШІ МОДЕЛІ БЕЗ ЗМІН =====

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    text = Column(Text, nullable=True)
    file_id = Column(String(500), nullable=True)
    
    # Автор та модератор
    author_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    moderator_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    
    # Статус та метадані
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    moderation_comment = Column(Text, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    
    # Статистика
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    
    # Персоналізація контенту
    topic = Column(String(50), default="general")  # life, work, tech, etc.
    style = Column(String(50), default="neutral")  # irony, sarcasm, wholesome
    difficulty = Column(Integer, default=1)  # 1-5
    quality_score = Column(Float, default=0.5)  # 0.0-1.0
    popularity_score = Column(Float, default=0.0)
    
    # Часові мітки
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Зв'язки
    author = relationship("User", foreign_keys=[author_id], back_populates="submitted_content")
    moderator = relationship("User", foreign_keys=[moderator_id], back_populates="moderated_content")
    ratings = relationship("Rating", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1 для like, -1 для dislike
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, content_id={self.content_id}, rating={self.rating})>"

class Duel(Base):
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Учасники
    challenger_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    opponent_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    
    # Контент дуелі
    challenger_content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    opponent_content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    
    # Статус та результати
    status = Column(String(20), default="waiting")  # waiting, active, completed, cancelled
    winner_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    
    # Голосування
    challenger_votes = Column(Integer, default=0)
    opponent_votes = Column(Integer, default=0)
    
    # Часові рамки
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    voting_ends_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Duel(id={self.id}, challenger={self.challenger_id}, opponent={self.opponent_id})>"

class DuelVote(Base):
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    duel_id = Column(Integer, ForeignKey("duels.id"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    
    vote = Column(String(20), nullable=False)  # "challenger" або "opponent"
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DuelVote(duel_id={self.duel_id}, voter_id={self.voter_id}, vote={self.vote})>"

class AdminAction(Base):
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    
    action_type = Column(String(50), nullable=False)  # moderate_content, ban_user, etc.
    target_id = Column(Integer, nullable=True)  # ID об'єкта дії
    details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Зв'язки
    admin = relationship("User", back_populates="admin_actions")
    
    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin_id={self.admin_id}, action={self.action_type})>"

class BotStatistics(Base):
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Загальна статистика
    total_users = Column(Integer, default=0)
    active_users_today = Column(Integer, default=0)
    active_users_week = Column(Integer, default=0)
    active_users_month = Column(Integer, default=0)
    
    # Контент
    total_content = Column(Integer, default=0)
    approved_content = Column(Integer, default=0)
    pending_content = Column(Integer, default=0)
    rejected_content = Column(Integer, default=0)
    
    # Дуелі
    total_duels = Column(Integer, default=0)
    active_duels = Column(Integer, default=0)
    completed_duels = Column(Integer, default=0)
    
    # Часові мітки
    date = Column(DateTime, server_default=func.now(), unique=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<BotStatistics(date={self.date}, users={self.total_users})>"