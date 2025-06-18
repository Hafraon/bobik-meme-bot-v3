#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНІ МОДЕЛІ БАЗИ ДАНИХ (ПОВНА ВЕРСІЯ) 🧠😂🔥
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

# ===== ОСНОВНІ МОДЕЛІ =====

class User(Base):
    """
    Модель користувача з повним набором полів для гейміфікації
    """
    __tablename__ = "users"
    
    # ===== ОСНОВНІ ПОЛЯ =====
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # ===== СТАТУСИ ТА ПРАВА =====
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # ✅ ВИПРАВЛЕНО!
    is_premium = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False, index=True)
    is_banned = Column(Boolean, default=False, nullable=False)
    
    # ===== ГЕЙМІФІКАЦІЯ =====
    total_points = Column(Integer, default=0, index=True)
    current_rank = Column(SQLEnum(UserRank), default=UserRank.NEWBIE, nullable=False)
    
    # ===== ЛІЧИЛЬНИКИ КОНТЕНТУ =====
    jokes_submitted = Column(Integer, default=0)
    jokes_approved = Column(Integer, default=0)
    memes_submitted = Column(Integer, default=0)
    memes_approved = Column(Integer, default=0)
    
    # ===== ЛІЧИЛЬНИКИ ВЗАЄМОДІЇ =====
    likes_given = Column(Integer, default=0)
    dislikes_given = Column(Integer, default=0)
    comments_made = Column(Integer, default=0)
    content_views = Column(Integer, default=0)
    
    # ===== ДУЕЛІ =====
    duels_won = Column(Integer, default=0)
    duels_lost = Column(Integer, default=0)
    duels_participated = Column(Integer, default=0)
    
    # ===== НАЛАШТУВАННЯ =====
    daily_subscription = Column(Boolean, default=False)
    last_daily_content = Column(DateTime, nullable=True)
    notification_settings = Column(Text, nullable=True)  # JSON формат
    
    # ===== ПЕРСОНАЛІЗАЦІЯ =====
    preferred_content_type = Column(String(20), default="mixed")  # joke, meme, mixed
    content_difficulty = Column(Integer, default=1)  # 1-5
    favorite_topics = Column(Text, nullable=True)  # JSON список тем
    language_preference = Column(String(10), default="uk")
    
    # ===== МЕТАДАНІ =====
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime, server_default=func.now(), index=True)
    last_seen_content_id = Column(Integer, nullable=True)
    
    # ===== СТАТИСТИКА СЕСІЙ =====
    total_sessions = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # секунди
    average_session_length = Column(Float, default=0.0)
    
    # ===== ЗВ'ЯЗКИ =====
    submitted_content = relationship("Content", foreign_keys="[Content.author_id]", back_populates="author")
    moderated_content = relationship("Content", foreign_keys="[Content.moderator_id]", back_populates="moderator")
    ratings = relationship("Rating", back_populates="user")
    admin_actions = relationship("AdminAction", back_populates="admin")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username}, rank={self.current_rank})>"
    
    def get_full_name(self) -> str:
        """Отримати повне ім'я користувача"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) or self.username or f"User {self.telegram_id}"
    
    def get_rank_progress(self) -> dict:
        """Отримати прогрес рангу"""
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
        
        ranks = list(UserRank)
        current_index = ranks.index(current_rank)
        
        next_rank = None
        points_to_next = 0
        progress_percent = 100
        
        if current_index < len(ranks) - 1:
            next_rank = ranks[current_index + 1]
            points_to_next = rank_requirements[next_rank] - current_points
            current_rank_min = rank_requirements[current_rank]
            next_rank_min = rank_requirements[next_rank]
            progress_percent = min(100, ((current_points - current_rank_min) / (next_rank_min - current_rank_min)) * 100)
        
        return {
            "current_rank": current_rank.value,
            "current_points": current_points,
            "next_rank": next_rank.value if next_rank else None,
            "points_to_next": max(0, points_to_next) if next_rank else 0,
            "progress_percent": round(progress_percent, 1)
        }

class Content(Base):
    """
    Модель контенту з розширеними можливостями
    """
    __tablename__ = "content"
    
    # ===== ОСНОВНІ ПОЛЯ =====
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    text = Column(Text, nullable=True)
    file_id = Column(String(500), nullable=True)
    
    # ===== АВТОР ТА МОДЕРАТОР =====
    author_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, index=True)
    moderator_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    
    # ===== СТАТУС МОДЕРАЦІЇ =====
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING, nullable=False, index=True)
    moderation_comment = Column(Text, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    
    # ===== СТАТИСТИКА ПОПУЛЯРНОСТІ =====
    views = Column(Integer, default=0, index=True)
    likes = Column(Integer, default=0, index=True)
    dislikes = Column(Integer, default=0, index=True)
    shares = Column(Integer, default=0)
    reports = Column(Integer, default=0)
    
    # ===== ПЕРСОНАЛІЗАЦІЯ КОНТЕНТУ =====
    topic = Column(String(50), default="general", index=True)  # life, work, tech, family, etc.
    style = Column(String(50), default="neutral")  # irony, sarcasm, wholesome, absurd
    difficulty = Column(Integer, default=1)  # 1-5 складність для розуміння
    target_age = Column(String(20), default="all")  # teen, adult, all
    
    # ===== АЛГОРИТМІЧНІ ПОКАЗНИКИ =====
    quality_score = Column(Float, default=0.5)  # 0.0-1.0 якість контенту
    popularity_score = Column(Float, default=0.0)  # розрахований показник популярності
    engagement_rate = Column(Float, default=0.0)  # рівень залученості
    virality_score = Column(Float, default=0.0)  # вірусний потенціал
    
    # ===== МЕТАДАНІ =====
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_shown_at = Column(DateTime, nullable=True)
    
    # ===== ТЕХНІЧНІ ДАНІ =====
    original_message_id = Column(Integer, nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON список хештегів
    mentions = Column(Text, nullable=True)  # JSON список згадок
    
    # ===== ЗВ'ЯЗКИ =====
    author = relationship("User", foreign_keys=[author_id], back_populates="submitted_content")
    moderator = relationship("User", foreign_keys=[moderator_id], back_populates="moderated_content")
    ratings = relationship("Rating", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status}, likes={self.likes})>"
    
    def get_engagement_stats(self) -> dict:
        """Статистика залученості"""
        total_interactions = self.likes + self.dislikes + self.shares
        engagement_rate = (total_interactions / max(self.views, 1)) * 100 if self.views > 0 else 0
        like_ratio = (self.likes / max(total_interactions, 1)) * 100 if total_interactions > 0 else 0
        
        return {
            "views": self.views,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "shares": self.shares,
            "total_interactions": total_interactions,
            "engagement_rate": round(engagement_rate, 2),
            "like_ratio": round(like_ratio, 2)
        }

class Rating(Base):
    """
    Модель оцінок контенту
    """
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False, index=True)
    
    # ===== ОСНОВНА ОЦІНКА =====
    rating = Column(Integer, nullable=False)  # 1 для like, -1 для dislike
    comment = Column(Text, nullable=True)
    
    # ===== ДОДАТКОВІ ОЦІНКИ =====
    funniness = Column(Integer, nullable=True)  # 1-5
    originality = Column(Integer, nullable=True)  # 1-5
    appropriateness = Column(Integer, nullable=True)  # 1-5
    
    # ===== МЕТАДАНІ =====
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # для запобігання зловживанням
    
    # ===== ЗВ'ЯЗКИ =====
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, content_id={self.content_id}, rating={self.rating})>"

class Duel(Base):
    """
    Модель дуелей жартів
    """
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ===== УЧАСНИКИ =====
    challenger_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    opponent_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    
    # ===== КОНТЕНТ ДУЕЛІ =====
    challenger_content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    opponent_content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    
    # ===== СТАТУС ТА РЕЗУЛЬТАТИ =====
    status = Column(String(20), default="waiting", index=True)  # waiting, active, completed, cancelled
    winner_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    
    # ===== ГОЛОСУВАННЯ =====
    challenger_votes = Column(Integer, default=0)
    opponent_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # ===== ПРИЗОВІ БАЛИ =====
    prize_points = Column(Integer, default=15)
    
    # ===== ЧАСОВІ РАМКИ =====
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    voting_ends_at = Column(DateTime, nullable=True, index=True)
    
    # ===== МЕТАДАНІ =====
    category = Column(String(50), default="general")
    difficulty_level = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<Duel(id={self.id}, challenger={self.challenger_id}, opponent={self.opponent_id}, status={self.status})>"

class DuelVote(Base):
    """
    Модель голосів у дуелях
    """
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    duel_id = Column(Integer, ForeignKey("duels.id"), nullable=False, index=True)
    voter_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, index=True)
    
    # ===== ГОЛОС =====
    vote = Column(String(20), nullable=False)  # "challenger" або "opponent"
    confidence = Column(Integer, default=5)  # 1-10 впевненість у виборі
    
    # ===== МЕТАДАНІ =====
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    
    def __repr__(self):
        return f"<DuelVote(duel_id={self.duel_id}, voter_id={self.voter_id}, vote={self.vote})>"

class AdminAction(Base):
    """
    Модель дій адміністраторів для аудиту
    """
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, index=True)
    
    # ===== ДІЯ =====
    action_type = Column(String(50), nullable=False, index=True)  # moderate_content, ban_user, etc.
    target_type = Column(String(50), nullable=True)  # user, content, duel
    target_id = Column(Integer, nullable=True)
    
    # ===== ДЕТАЛІ =====
    details = Column(Text, nullable=True)  # JSON з деталями дії
    reason = Column(Text, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # ===== МЕТАДАНІ =====
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    
    # ===== ЗВ'ЯЗКИ =====
    admin = relationship("User", back_populates="admin_actions")
    
    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin_id={self.admin_id}, action={self.action_type})>"

class BotStatistics(Base):
    """
    Модель щоденної статистики бота
    """
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ===== СТАТИСТИКА КОРИСТУВАЧІВ =====
    total_users = Column(Integer, default=0)
    new_users_today = Column(Integer, default=0)
    active_users_today = Column(Integer, default=0)
    active_users_week = Column(Integer, default=0)
    active_users_month = Column(Integer, default=0)
    
    # ===== СТАТИСТИКА КОНТЕНТУ =====
    total_content = Column(Integer, default=0)
    new_content_today = Column(Integer, default=0)
    approved_content = Column(Integer, default=0)
    pending_content = Column(Integer, default=0)
    rejected_content = Column(Integer, default=0)
    
    # ===== СТАТИСТИКА ВЗАЄМОДІЇ =====
    total_likes_today = Column(Integer, default=0)
    total_views_today = Column(Integer, default=0)
    total_shares_today = Column(Integer, default=0)
    
    # ===== СТАТИСТИКА ДУЕЛЕЙ =====
    total_duels = Column(Integer, default=0)
    active_duels = Column(Integer, default=0)
    completed_duels_today = Column(Integer, default=0)
    
    # ===== ТЕХНІЧНА СТАТИСТИКА =====
    average_response_time = Column(Float, default=0.0)
    error_count_today = Column(Integer, default=0)
    uptime_percentage = Column(Float, default=100.0)
    
    # ===== ЧАСОВІ МІТКИ =====
    date = Column(DateTime, server_default=func.now(), unique=True, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<BotStatistics(date={self.date}, users={self.total_users}, content={self.total_content})>"

# ===== ІНДЕКСИ ДЛЯ ОПТИМІЗАЦІЇ =====

# Створюємо складені індекси для часто використовуваних запитів
from sqlalchemy import Index

# Індекс для пошуку активного контенту
Index('idx_content_status_type', Content.status, Content.content_type)

# Індекс для статистики користувачів
Index('idx_user_activity', User.is_active, User.last_activity)

# Індекс для рейтингів
Index('idx_rating_user_content', Rating.user_id, Rating.content_id)

# Індекс для дуелей
Index('idx_duel_status_voting', Duel.status, Duel.voting_ends_at)