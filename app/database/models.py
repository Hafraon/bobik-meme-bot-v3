#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 ЄДИНА КОНСОЛІДОВАНА МОДЕЛЬ БД - POSTGRESQL СУМІСНА 💾

ВИПРАВЛЕННЯ:
✅ BigInteger для Telegram User ID (підтримка великих ID)
✅ String замість SQLEnum для PostgreSQL сумісності
✅ Узгоджена структура User без конфліктів полів
✅ Додано індекси для продуктивності
✅ Правильні зв'язки між таблицями
✅ Розширена система балів та досягнень
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey, 
    Integer, String, Text, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# 🎯 ENUM'И ДЛЯ PYTHON (не для PostgreSQL)
class ContentType(Enum):
    """Тип контенту - для внутрішнього використання"""
    MEME = "meme"
    JOKE = "joke"
    ANEKDOT = "anekdot"

class ContentStatus(Enum):
    """Статус контенту - для внутрішнього використання"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DuelStatus(Enum):
    """Статус дуелі - для внутрішнього використання"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class UserRank(Enum):
    """Ранги користувачів"""
    NEWBIE = "🤡 Новачок"
    JOKER = "😄 Сміхун"
    COMEDIAN = "😂 Гуморист"
    HUMORIST = "🎭 Комік"
    MASTER = "👑 Мастер Рофлу"
    EXPERT = "🏆 Король Гумору"
    VIRTUOSO = "🌟 Легенда Мемів"
    LEGEND = "🚀 Гумористичний Геній"

# 👥 МОДЕЛЬ КОРИСТУВАЧА
class User(Base):
    """Модель користувача - КОНСОЛІДОВАНА ВЕРСІЯ"""
    __tablename__ = "users"
    
    # 🎯 ОСНОВНІ ПОЛЯ - ВИПРАВЛЕНО
    id = Column(BigInteger, primary_key=True)  # ✅ Telegram User ID (BigInteger)
    username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # 🎮 ГЕЙМІФІКАЦІЯ - РОЗШИРЕНО
    points = Column(Integer, default=0, index=True)
    rank = Column(String(100), default="🤡 Новачок")
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # 📊 СТАТИСТИКА КОНТЕНТУ
    jokes_submitted = Column(Integer, default=0)
    jokes_approved = Column(Integer, default=0)
    memes_submitted = Column(Integer, default=0)
    memes_approved = Column(Integer, default=0)
    anekdots_submitted = Column(Integer, default=0)
    anekdots_approved = Column(Integer, default=0)
    
    # ⚔️ СТАТИСТИКА ДУЕЛЕЙ
    duels_participated = Column(Integer, default=0)
    duels_won = Column(Integer, default=0)
    duels_lost = Column(Integer, default=0)
    duels_draw = Column(Integer, default=0)
    
    # 👍 СТАТИСТИКА ВЗАЄМОДІЙ
    reactions_given = Column(Integer, default=0)
    reactions_received = Column(Integer, default=0)
    comments_made = Column(Integer, default=0)
    votes_cast = Column(Integer, default=0)
    
    # 📈 ПОКАЗНИКИ АКТИВНОСТІ
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)  # Дні поспіль активності
    last_streak_date = Column(DateTime, nullable=True)
    
    # ⚙️ НАЛАШТУВАННЯ
    daily_subscription = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    language_code = Column(String(10), default="uk")
    timezone = Column(String(50), default="Europe/Kiev")
    
    # 🛡️ МОДЕРАЦІЯ ТА БЕЗПЕКА
    is_admin = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    ban_until = Column(DateTime, nullable=True)
    warnings_count = Column(Integer, default=0)
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, index=True)
    last_content_submission = Column(DateTime, nullable=True)
    
    # 🔗 ЗВ'ЯЗКИ
    authored_content = relationship("Content", back_populates="author", foreign_keys="Content.author_id")
    moderated_content = relationship("Content", back_populates="moderator", foreign_keys="Content.moderator_id")
    ratings = relationship("Rating", back_populates="user")
    duel_participations = relationship("Duel", back_populates="challenger", foreign_keys="Duel.challenger_id")
    duel_targets = relationship("Duel", back_populates="target", foreign_keys="Duel.target_id")
    duel_votes = relationship("DuelVote", back_populates="voter")
    admin_actions = relationship("AdminAction", back_populates="admin")
    achievements = relationship("UserAchievement", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, rank={self.rank})>"
    
    @property
    def display_name(self):
        """Відображуване ім'я"""
        if self.username:
            return f"@{self.username}"
        elif self.first_name:
            return self.first_name
        else:
            return f"User_{self.id}"
    
    @property
    def win_rate(self):
        """Відсоток перемог у дуелях"""
        if self.duels_participated == 0:
            return 0.0
        return round((self.duels_won / self.duels_participated) * 100, 1)
    
    @property
    def approval_rate(self):
        """Відсоток схвалення контенту"""
        total_submitted = self.jokes_submitted + self.memes_submitted + self.anekdots_submitted
        if total_submitted == 0:
            return 0.0
        total_approved = self.jokes_approved + self.memes_approved + self.anekdots_approved
        return round((total_approved / total_submitted) * 100, 1)

# 📝 МОДЕЛЬ КОНТЕНТУ
class Content(Base):
    """Модель контенту - ВИПРАВЛЕНО для PostgreSQL"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 🎯 ОСНОВНІ ПОЛЯ - ВИКОРИСТОВУЄМО STRING замість ENUM
    content_type = Column(String(20), default="joke", index=True)  # ✅ String замість Enum
    status = Column(String(20), default="pending", index=True)     # ✅ String замість Enum
    
    # 📄 КОНТЕНТ
    text = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)  # photo, video, document
    file_id = Column(String(500), nullable=True)  # Telegram file_id
    
    # 👤 АВТОР І МОДЕРАТОР
    author_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    author_user_id = Column(BigInteger, nullable=True)  # Backup поле
    moderator_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    # 🛡️ МОДЕРАЦІЯ
    moderated_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    moderation_notes = Column(Text, nullable=True)
    
    # 📊 СТАТИСТИКА
    views = Column(Integer, default=0, index=True)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reports_count = Column(Integer, default=0)
    
    # 🎯 МЕТРИКИ ЯКОСТІ
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    popularity_score = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    virality_score = Column(Float, default=0.0)
    
    # 🏷️ КЛАСИФІКАЦІЯ
    topic = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # JSON строка з тегами
    difficulty = Column(String(20), default="medium")
    target_audience = Column(String(50), default="general")
    
    # ⭐ ОСОБЛИВІ СТАТУСИ
    is_featured = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False, index=True)
    featured_until = Column(DateTime, nullable=True)
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # 🔗 ЗВ'ЯЗКИ
    author = relationship("User", back_populates="authored_content", foreign_keys=[author_id])
    moderator = relationship("User", back_populates="moderated_content", foreign_keys=[moderator_id])
    ratings = relationship("Rating", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, type={self.content_type}, status={self.status})>"

# ⭐ МОДЕЛЬ РЕЙТИНГУ
class Rating(Base):
    """Модель рейтингу контенту"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    content_id = Column(Integer, ForeignKey('content.id'), nullable=False)
    
    # 📊 РЕЙТИНГ
    rating = Column(Integer, nullable=False)  # 1-5 зірок
    reaction_type = Column(String(20), nullable=True)  # like, dislike, love, laugh
    
    # 💬 КОМЕНТАР
    comment = Column(Text, nullable=True)
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 🔗 ЗВ'ЯЗКИ
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")
    
    # Унікальний індекс - один рейтинг від користувача на контент
    __table_args__ = (UniqueConstraint('user_id', 'content_id', name='unique_user_content_rating'),)

# ⚔️ МОДЕЛЬ ДУЕЛІ
class Duel(Base):
    """Модель дуелі жартів"""
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 👥 УЧАСНИКИ
    challenger_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    target_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)  # None для випадкового опонента
    
    # 📝 КОНТЕНТ ДУЕЛІ
    challenger_content_id = Column(Integer, ForeignKey('content.id'), nullable=False)
    target_content_id = Column(Integer, ForeignKey('content.id'), nullable=True)
    
    # 🎯 СТАТУС ТА ПРАВИЛА
    status = Column(String(20), default="active", index=True)  # ✅ String замість Enum
    duel_type = Column(String(50), default="classic")  # classic, tournament, quick
    max_participants = Column(Integer, default=100)
    duration_minutes = Column(Integer, default=1440)  # 24 години за замовчуванням
    
    # 📊 РЕЗУЛЬТАТИ
    challenger_votes = Column(Integer, default=0)
    target_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    winner_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    # 🏆 НАГОРОДИ
    prize_points = Column(Integer, default=10)
    bonus_points = Column(Integer, default=0)
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # 🔗 ЗВ'ЯЗКИ
    challenger = relationship("User", back_populates="duel_participations", foreign_keys=[challenger_id])
    target = relationship("User", back_populates="duel_targets", foreign_keys=[target_id])
    winner = relationship("User", foreign_keys=[winner_id])
    votes = relationship("DuelVote", back_populates="duel")
    
    def __repr__(self):
        return f"<Duel(id={self.id}, status={self.status}, votes={self.total_votes})>"

# 🗳️ МОДЕЛЬ ГОЛОСУВАННЯ В ДУЕЛІ
class DuelVote(Base):
    """Модель голосування в дуелі"""
    __tablename__ = "duel_votes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    duel_id = Column(Integer, ForeignKey('duels.id'), nullable=False)
    voter_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    
    # 🗳️ ГОЛОС
    voted_for = Column(String(20), nullable=False)  # "challenger" або "target"
    vote_weight = Column(Float, default=1.0)  # Можна давати більшу вагу досвідченим користувачам
    
    # 💬 КОМЕНТАР ДО ГОЛОСУ
    comment = Column(Text, nullable=True)
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 🔗 ЗВ'ЯЗКИ
    duel = relationship("Duel", back_populates="votes")
    voter = relationship("User", back_populates="duel_votes")
    
    # Унікальний індекс - один голос від користувача в дуелі
    __table_args__ = (UniqueConstraint('duel_id', 'voter_id', name='unique_duel_voter'),)

# 🛡️ МОДЕЛЬ АДМІН ДІЙSLOGAN
class AdminAction(Base):
    """Модель дій адміністратора"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    
    # 🎯 ДІЯ
    action_type = Column(String(50), nullable=False)  # moderate_content, ban_user, feature_content
    target_type = Column(String(50), nullable=False)  # user, content, duel
    target_id = Column(Integer, nullable=False)
    
    # 📝 ДЕТАЛІ
    action_details = Column(Text, nullable=True)  # JSON з деталями дії
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 🔗 ЗВ'ЯЗКИ
    admin = relationship("User", back_populates="admin_actions")
    
    def __repr__(self):
        return f"<AdminAction(action={self.action_type}, target={self.target_type}:{self.target_id})>"

# 📊 МОДЕЛЬ СТАТИСТИКИ БОТА
class BotStatistics(Base):
    """Модель статистики бота"""
    __tablename__ = "bot_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 📅 ПЕРІОД
    date = Column(DateTime, default=datetime.utcnow, index=True)
    period_type = Column(String(20), default="daily")  # daily, weekly, monthly
    
    # 👥 КОРИСТУВАЧІ
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    
    # 📝 КОНТЕНТ
    total_content = Column(Integer, default=0)
    new_content = Column(Integer, default=0)
    approved_content = Column(Integer, default=0)
    rejected_content = Column(Integer, default=0)
    
    # ⚔️ ДУЕЛІ
    total_duels = Column(Integer, default=0)
    active_duels = Column(Integer, default=0)
    completed_duels = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # 📊 ВЗАЄМОДІЯ
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # 🤖 СИСТЕМА
    bot_uptime_minutes = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<BotStatistics(date={self.date.date()}, users={self.total_users})>"

# 🏆 МОДЕЛЬ ДОСЯГНЕНЬ
class Achievement(Base):
    """Модель досягнень"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 🎯 ДОСЯГНЕННЯ
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon = Column(String(10), default="🏆")
    category = Column(String(50), nullable=False)  # content, duels, social, special
    
    # 📊 УМОВИ
    requirement_type = Column(String(50), nullable=False)  # points, wins, submissions
    requirement_value = Column(Integer, nullable=False)
    
    # 🎁 НАГОРОДА
    reward_points = Column(Integer, default=0)
    reward_title = Column(String(100), nullable=True)
    
    # ⚙️ НАЛАШТУВАННЯ
    is_active = Column(Boolean, default=True)
    is_secret = Column(Boolean, default=False)  # Секретні досягнення
    
    # 🕒 ЧАСОВІ МІТКИ
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Achievement(name={self.name}, category={self.category})>"

# 🏆 МОДЕЛЬ КОРИСТУВАЦЬКИХ ДОСЯГНЕНЬ
class UserAchievement(Base):
    """Модель досягнень користувача"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    
    # 📊 ПРОГРЕС
    progress = Column(Float, default=0.0)  # 0.0 - 1.0
    is_completed = Column(Boolean, default=False)
    
    # 🕒 ЧАСОВІ МІТКИ
    earned_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 🔗 ЗВ'ЯЗКИ
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")
    
    # Унікальний індекс - одне досягнення на користувача
    __table_args__ = (UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)

# 📋 ІНДЕКСИ ДЛЯ ПРОДУКТИВНОСТІ
Index('idx_content_status_created', Content.status, Content.created_at)
Index('idx_content_type_featured', Content.content_type, Content.is_featured)
Index('idx_user_points_rank', User.points, User.rank)
Index('idx_duel_status_created', Duel.status, Duel.created_at)
Index('idx_rating_content_user', Rating.content_id, Rating.user_id)

# 🎯 КОНСТАНТИ ДЛЯ РОБОТИ З БД
CONTENT_TYPES = ["meme", "joke", "anekdot"]
CONTENT_STATUSES = ["pending", "approved", "rejected"]
DUEL_STATUSES = ["active", "completed", "cancelled"]

# Список всіх моделей для експорту
ALL_MODELS = [
    User, Content, Rating, Duel, DuelVote, 
    AdminAction, BotStatistics, Achievement, UserAchievement
]