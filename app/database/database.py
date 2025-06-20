#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 ПОВНІСТЮ ВИПРАВЛЕНА БАЗА ДАНИХ - POSTGRESQL СУМІСНА 💾

ВИПРАВЛЕННЯ:
✅ String значення замість enum'ів для PostgreSQL
✅ Правильна обробка User.id як BigInteger для Telegram
✅ Усунено конфлікт полів User.telegram_id
✅ Додано розширені функції для нових можливостей
✅ Покращена обробка помилок та fallback режим
✅ Підтримка досягнень та розширеної статистики
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager
import random
import json

# SQLAlchemy імпорти
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger(__name__)

# Глобальні змінні для БД
engine = None
SessionLocal = None
MODELS_LOADED = False
DATABASE_AVAILABLE = False

# ===== БЕЗПЕЧНИЙ ІМПОРТ КОНФІГУРАЦІЇ =====
try:
    from config.settings import (
        DATABASE_URL, 
        ADMIN_ID,
        POINTS_FOR_SUBMISSION,
        POINTS_FOR_APPROVAL,
        POINTS_FOR_LIKE,
        POINTS_FOR_DUEL_WIN
    )
    SETTINGS_LOADED = True
    logger.info("✅ Settings завантажено з config.settings")
except ImportError as e:
    # Fallback налаштування
    DATABASE_URL = "postgresql://user:password@localhost/dbname"
    ADMIN_ID = 603047391
    POINTS_FOR_SUBMISSION = 5
    POINTS_FOR_APPROVAL = 15
    POINTS_FOR_LIKE = 1
    POINTS_FOR_DUEL_WIN = 20
    SETTINGS_LOADED = False
    logger.warning(f"⚠️ Fallback settings: {e}")

# ===== БЕЗПЕЧНИЙ ІМПОРТ МОДЕЛЕЙ =====
try:
    from .models import (
        Base, User, Content, Rating, Duel, DuelVote, 
        AdminAction, BotStatistics, Achievement, UserAchievement,
        ContentType, ContentStatus, DuelStatus, UserRank,
        CONTENT_TYPES, CONTENT_STATUSES, DUEL_STATUSES
    )
    MODELS_LOADED = True
    logger.info("✅ Моделі БД завантажено успішно")
except ImportError as e:
    MODELS_LOADED = False
    logger.error(f"❌ Помилка імпорту models: {e}")

# ===== ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ =====
async def init_db() -> bool:
    """Ініціалізація бази даних з повною обробкою помилок"""
    global engine, SessionLocal, DATABASE_AVAILABLE
    
    logger.info("💾 Початок ініціалізації бази даних...")
    
    try:
        if not MODELS_LOADED:
            logger.error("❌ Моделі БД не завантажені!")
            return False
        
        # Створення engine з правильними параметрами для PostgreSQL
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Вимкнути SQL логування для production
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_pre_ping=True,  # Перевірка з'єднання перед використанням
            connect_args={
                "connect_timeout": 10,
                "application_name": "ukraian_telegram_bot"
            }
        )
        
        # Створення фабрики сесій
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        logger.info("✅ Database engine створено успішно")
        
        # Створення всіх таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблиці БД створено/оновлено")
        
        # Перевірка підключення
        with get_db_session() as session:
            result = session.execute(text("SELECT 1")).fetchone()
            if result:
                DATABASE_AVAILABLE = True
                logger.info("✅ З'єднання з БД підтверджено")
            else:
                logger.error("❌ Не вдалося підтвердити з'єднання")
                return False
        
        # Створення початкових даних
        await ensure_admin_exists()
        await add_initial_data()
        await create_default_achievements()
        
        logger.info("✅ База даних повністю ініціалізована!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації БД: {e}")
        DATABASE_AVAILABLE = False
        return False

@contextmanager
def get_db_session():
    """Контекстний менеджер для роботи з сесією БД"""
    if not DATABASE_AVAILABLE or not SessionLocal:
        raise Exception("База даних недоступна")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Помилка БД сесії: {e}")
        raise
    finally:
        session.close()

# ===== ФУНКЦІЇ КОРИСТУВАЧІВ =====
async def get_or_create_user(telegram_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None) -> Optional[User]:
    """Отримати або створити користувача - ВИПРАВЛЕНО для нової моделі"""
    try:
        if not DATABASE_AVAILABLE:
            return None
            
        with get_db_session() as session:
            # ✅ ВИПРАВЛЕНО: використовуємо telegram_id -> id
            user = session.query(User).filter(User.id == telegram_id).first()
            
            if user:
                # Оновлення існуючого користувача
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                user.last_active = datetime.utcnow()
                user.updated_at = datetime.utcnow()
                
                session.commit()
                logger.info(f"✅ Користувач {telegram_id} оновлений")
                return user
            else:
                # Створення нового користувача
                new_user = User(
                    id=telegram_id,  # ✅ ВИПРАВЛЕНО: id = telegram_id
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    created_at=datetime.utcnow(),
                    last_active=datetime.utcnow()
                )
                
                session.add(new_user)
                session.commit()
                logger.info(f"✅ Створено нового користувача {telegram_id}")
                return new_user
                
    except Exception as e:
        logger.error(f"❌ Помилка створення користувача {telegram_id}: {e}")
        return None

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Отримати користувача за ID"""
    try:
        if not DATABASE_AVAILABLE:
            return None
            
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
        return None

async def update_user_points(user_id: int, points_delta: int, reason: str = "") -> bool:
    """Оновити бали користувача з автоматичним підвищенням рангу"""
    try:
        if not DATABASE_AVAILABLE:
            return False
            
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            old_points = user.points
            user.points += points_delta
            user.experience += max(points_delta, 0)  # Досвід тільки від позитивних дій
            
            # Автоматичне підвищення рангу
            new_rank = get_rank_by_points(user.points)
            if new_rank != user.rank:
                old_rank = user.rank
                user.rank = new_rank
                user.level += 1
                logger.info(f"🎉 Користувач {user_id} підвищився з '{old_rank}' до '{new_rank}'!")
            
            user.updated_at = datetime.utcnow()
            session.commit()
            
            logger.info(f"✅ Користувач {user_id}: {old_points} + {points_delta} = {user.points} балів ({reason})")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка оновлення балів користувача {user_id}: {e}")
        return False

def get_rank_by_points(points: int) -> str:
    """Отримати ранг за кількістю балів - РОЗШИРЕНО"""
    if points >= 10000:
        return UserRank.LEGEND.value      # 🚀 Гумористичний Геній
    elif points >= 5000:
        return UserRank.VIRTUOSO.value    # 🌟 Легенда Мемів
    elif points >= 2500:
        return UserRank.EXPERT.value      # 🏆 Король Гумору
    elif points >= 1000:
        return UserRank.MASTER.value      # 👑 Мастер Рофлу
    elif points >= 500:
        return UserRank.HUMORIST.value    # 🎭 Комік
    elif points >= 250:
        return UserRank.COMEDIAN.value    # 😂 Гуморист
    elif points >= 100:
        return UserRank.JOKER.value       # 😄 Сміхун
    else:
        return UserRank.NEWBIE.value      # 🤡 Новачок

# ===== ФУНКЦІЇ КОНТЕНТУ =====
async def add_content_for_moderation(author_id: int, text: str, content_type: str = "joke", 
                                   media_url: str = None, media_type: str = None) -> Optional[Content]:
    """Додати контент на модерацію - ВИПРАВЛЕНО для string enum"""
    try:
        if not DATABASE_AVAILABLE:
            return None
            
        # ✅ ВИПРАВЛЕНО: Перевірка валідності content_type як string
        if content_type not in CONTENT_TYPES:
            content_type = "joke"
            
        with get_db_session() as session:
            new_content = Content(
                author_id=author_id,
                author_user_id=author_id,  # Backup поле
                text=text,
                content_type=content_type,    # ✅ String замість enum
                status="pending",             # ✅ String замість enum
                media_url=media_url,
                media_type=media_type,
                created_at=datetime.utcnow()
            )
            
            session.add(new_content)
            session.commit()
            
            # Нарахування балів за подачу
            await update_user_points(author_id, POINTS_FOR_SUBMISSION, "подача контенту")
            
            # Оновлення статистики користувача
            user = session.query(User).filter(User.id == author_id).first()
            if user:
                if content_type == "joke":
                    user.jokes_submitted += 1
                elif content_type == "meme":
                    user.memes_submitted += 1
                elif content_type == "anekdot":
                    user.anekdots_submitted += 1
                user.last_content_submission = datetime.utcnow()
                session.commit()
            
            logger.info(f"✅ Контент #{new_content.id} додано на модерацію від користувача {author_id}")
            return new_content
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання контенту: {e}")
        return None

async def get_pending_content(limit: int = 10) -> List[Content]:
    """Отримати контент на модерації"""
    try:
        if not DATABASE_AVAILABLE:
            return []
            
        with get_db_session() as session:
            # ✅ ВИПРАВЛЕНО: Використовуємо string замість enum
            content_list = session.query(Content).filter(
                Content.status == "pending"  # ✅ String замість ContentStatus.PENDING
            ).order_by(Content.created_at.asc()).limit(limit).all()
            
            return content_list
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту на модерації: {e}")
        return []

async def moderate_content(content_id: int, action: str, moderator_id: int, 
                         comment: str = None) -> bool:
    """Модерувати контент - ВИПРАВЛЕНО для string enum"""
    try:
        if not DATABASE_AVAILABLE:
            return False
            
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            if not content:
                logger.warning(f"⚠️ Контент {content_id} не знайдено")
                return False
            
            # ✅ ВИПРАВЛЕНО: Використовуємо string значення
            if action.upper() == "APPROVE":
                content.status = "approved"  # ✅ String замість enum
                
                # Нарахування балів автору
                await update_user_points(content.author_id, POINTS_FOR_APPROVAL, "схвалення контенту")
                
                # Оновлення статистики користувача
                user = session.query(User).filter(User.id == content.author_id).first()
                if user:
                    if content.content_type == "joke":
                        user.jokes_approved += 1
                    elif content.content_type == "meme":
                        user.memes_approved += 1
                    elif content.content_type == "anekdot":
                        user.anekdots_approved += 1
                
                content.published_at = datetime.utcnow()
                logger.info(f"✅ Контент {content_id} схвалено")
                
            elif action.upper() == "REJECT":
                content.status = "rejected"  # ✅ String замість enum
                content.rejection_reason = comment
                logger.info(f"❌ Контент {content_id} відхилено: {comment}")
            else:
                logger.warning(f"⚠️ Невідома дія модерації: {action}")
                return False
            
            content.moderator_id = moderator_id
            content.moderation_notes = comment
            content.moderated_at = datetime.utcnow()
            content.updated_at = datetime.utcnow()
            
            # Додавання запису в логи адміністратора
            admin_action = AdminAction(
                admin_id=moderator_id,
                action_type="moderate_content",
                target_type="content",
                target_id=content_id,
                action_details=json.dumps({
                    "action": action.lower(),
                    "content_type": content.content_type,
                    "author_id": content.author_id
                }),
                reason=comment,
                created_at=datetime.utcnow()
            )
            session.add(admin_action)
            
            session.commit()
            logger.info(f"✅ Контент {content_id} {action.lower()}ed модератором {moderator_id}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка модерації контенту {content_id}: {e}")
        return False

async def get_random_approved_content(content_type: str = None, exclude_user_id: int = None) -> Optional[Content]:
    """Отримати випадковий схвалений контент - ВИПРАВЛЕНО"""
    try:
        if not DATABASE_AVAILABLE:
            return None
            
        with get_db_session() as session:
            # ✅ ВИПРАВЛЕНО: Використовуємо string замість enum
            query = session.query(Content).filter(
                Content.status == "approved"  # ✅ String замість ContentStatus.APPROVED
            )
            
            # Фільтр по типу контенту
            if content_type and content_type in CONTENT_TYPES:
                query = query.filter(Content.content_type == content_type)
            
            # Виключити контент конкретного користувача
            if exclude_user_id:
                query = query.filter(Content.author_id != exclude_user_id)
            
            # Отримання випадкового контенту
            all_content = query.all()
            if not all_content:
                logger.warning("⚠️ Немає схваленого контенту")
                return None
            
            selected_content = random.choice(all_content)
            
            # Збільшення лічильника переглядів
            selected_content.views += 1
            session.commit()
            
            return selected_content
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання випадкового контенту: {e}")
        return None

# ===== ФУНКЦІЇ ДУЕЛЕЙ =====
async def create_duel(challenger_id: int, challenger_content_id: int, 
                     target_id: int = None, duel_type: str = "classic") -> Optional[Duel]:
    """Створити нову дуель"""
    try:
        if not DATABASE_AVAILABLE:
            return None
            
        with get_db_session() as session:
            new_duel = Duel(
                challenger_id=challenger_id,
                target_id=target_id,
                challenger_content_id=challenger_content_id,
                status="active",  # ✅ String замість enum
                duel_type=duel_type,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow()
            )
            
            session.add(new_duel)
            session.commit()
            
            logger.info(f"✅ Створена дуель #{new_duel.id} між {challenger_id} та {target_id}")
            return new_duel
            
    except Exception as e:
        logger.error(f"❌ Помилка створення дуелі: {e}")
        return None

async def vote_in_duel(duel_id: int, voter_id: int, voted_for: str, 
                      comment: str = None) -> bool:
    """Голосувати в дуелі"""
    try:
        if not DATABASE_AVAILABLE:
            return False
            
        if voted_for not in ["challenger", "target"]:
            return False
            
        with get_db_session() as session:
            # Перевірка чи вже голосував
            existing_vote = session.query(DuelVote).filter(
                DuelVote.duel_id == duel_id,
                DuelVote.voter_id == voter_id
            ).first()
            
            if existing_vote:
                logger.warning(f"⚠️ Користувач {voter_id} вже голосував у дуелі {duel_id}")
                return False
            
            # Створення нового голосу
            new_vote = DuelVote(
                duel_id=duel_id,
                voter_id=voter_id,
                voted_for=voted_for,
                comment=comment,
                created_at=datetime.utcnow()
            )
            session.add(new_vote)
            
            # Оновлення статистики дуелі
            duel = session.query(Duel).filter(Duel.id == duel_id).first()
            if duel:
                if voted_for == "challenger":
                    duel.challenger_votes += 1
                else:
                    duel.target_votes += 1
                duel.total_votes += 1
            
            # Оновлення статистики голосуючого
            voter = session.query(User).filter(User.id == voter_id).first()
            if voter:
                voter.votes_cast += 1
            
            session.commit()
            
            logger.info(f"✅ Голос у дуелі {duel_id}: {voter_id} → {voted_for}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка голосування в дуелі {duel_id}: {e}")
        return False

# ===== ФУНКЦІЇ ДОСЯГНЕНЬ =====
async def create_default_achievements():
    """Створити початкові досягнення"""
    try:
        if not DATABASE_AVAILABLE:
            return
            
        achievements_data = [
            # Контент досягнення
            ("Перший крок", "Подайте свій перший жарт", "🎯", "content", "submissions", 1, 10, None),
            ("Автор", "Подайте 10 жартів", "✍️", "content", "submissions", 10, 50, None),
            ("Продуктивний", "Подайте 50 жартів", "📝", "content", "submissions", 50, 200, None),
            ("Мегаавтор", "Подайте 100 жартів", "🚀", "content", "submissions", 100, 500, None),
            
            # Схвалення
            ("Схвалений", "Отримайте перше схвалення", "✅", "content", "approvals", 1, 25, None),
            ("Популярний", "Отримайте 10 схвалень", "⭐", "content", "approvals", 10, 100, None),
            ("Зірка", "Отримайте 25 схвалень", "🌟", "content", "approvals", 25, 300, None),
            
            # Дуелі
            ("Боєць", "Виграйте першу дуель", "⚔️", "duels", "wins", 1, 15, None),
            ("Переможець", "Виграйте 5 дуелів", "🏆", "duels", "wins", 5, 75, None),
            ("Чемпіон", "Виграйте 20 дуелів", "👑", "duels", "wins", 20, 300, None),
            
            # Бали
            ("Початківець", "Наберіть 100 балів", "💎", "points", "total", 100, 0, None),
            ("Досвідчений", "Наберіть 500 балів", "💰", "points", "total", 500, 0, None),
            ("Експерт", "Наберіть 1000 балів", "🎖️", "points", "total", 1000, 0, None),
            ("Легенда", "Наберіть 5000 балів", "🏅", "points", "total", 5000, 0, "Король Гумору"),
            
            # Спеціальні досягнення
            ("Щоденник", "Активність 7 днів поспіль", "📅", "special", "streak", 7, 100, None),
            ("Марафонець", "Активність 30 днів поспіль", "🏃", "special", "streak", 30, 500, "Невтомний"),
        ]
        
        with get_db_session() as session:
            for name, desc, icon, category, req_type, req_value, reward_points, reward_title in achievements_data:
                # Перевірка чи вже існує
                existing = session.query(Achievement).filter(Achievement.name == name).first()
                if not existing:
                    achievement = Achievement(
                        name=name,
                        description=desc,
                        icon=icon,
                        category=category,
                        requirement_type=req_type,
                        requirement_value=req_value,
                        reward_points=reward_points,
                        reward_title=reward_title,
                        created_at=datetime.utcnow()
                    )
                    session.add(achievement)
            
            session.commit()
            logger.info("✅ Початкові досягнення створені")
            
    except Exception as e:
        logger.error(f"❌ Помилка створення досягнень: {e}")

async def check_user_achievements(user_id: int):
    """Перевірити та нарахувати досягнення користувача"""
    try:
        if not DATABASE_AVAILABLE:
            return []
            
        new_achievements = []
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Отримання всіх досягнень
            all_achievements = session.query(Achievement).filter(Achievement.is_active == True).all()
            
            for achievement in all_achievements:
                # Перевірка чи вже має це досягнення
                user_achievement = session.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement.id,
                    UserAchievement.is_completed == True
                ).first()
                
                if user_achievement:
                    continue  # Вже має це досягнення
                
                # Перевірка умов досягнення
                current_value = 0
                if achievement.requirement_type == "submissions":
                    current_value = user.jokes_submitted + user.memes_submitted + user.anekdots_submitted
                elif achievement.requirement_type == "approvals":
                    current_value = user.jokes_approved + user.memes_approved + user.anekdots_approved
                elif achievement.requirement_type == "wins":
                    current_value = user.duels_won
                elif achievement.requirement_type == "total":
                    current_value = user.points
                elif achievement.requirement_type == "streak":
                    current_value = user.streak_days
                
                # Перевірка чи виконана умова
                if current_value >= achievement.requirement_value:
                    # Нарахування досягнення
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        progress=1.0,
                        is_completed=True,
                        earned_at=datetime.utcnow(),
                        created_at=datetime.utcnow()
                    )
                    session.add(user_achievement)
                    
                    # Нарахування нагороди
                    if achievement.reward_points > 0:
                        user.points += achievement.reward_points
                    
                    new_achievements.append(achievement)
                    logger.info(f"🏆 Користувач {user_id} отримав досягнення '{achievement.name}'!")
            
            session.commit()
            return new_achievements
            
    except Exception as e:
        logger.error(f"❌ Помилка перевірки досягнень користувача {user_id}: {e}")
        return []

# ===== АДМІНІСТРАТИВНІ ФУНКЦІЇ =====
async def ensure_admin_exists() -> bool:
    """Переконатися що адміністратор існує"""
    try:
        if not DATABASE_AVAILABLE:
            logger.warning("⚠️ БД недоступна - адміністратор не створений")
            return False
            
        admin_user = await get_or_create_user(
            telegram_id=ADMIN_ID,
            username="admin",
            first_name="Адміністратор"
        )
        
        if admin_user:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == ADMIN_ID).first()
                if user and not user.is_admin:
                    user.is_admin = True
                    user.is_moderator = True
                    user.points = max(user.points, 10000)  # Мінімум балів для адміна
                    user.rank = UserRank.LEGEND.value
                    session.commit()
                    logger.info(f"✅ Адміністратор {ADMIN_ID} підтверджений")
            return True
        else:
            logger.error(f"❌ Не вдалося створити адміністратора {ADMIN_ID}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Помилка створення адміністратора: {e}")
        return False

async def add_initial_data():
    """Додати початкові дані в БД"""
    try:
        if not DATABASE_AVAILABLE:
            logger.warning("⚠️ БД недоступна - початкові дані не додані")
            return
            
        # Перевірка чи вже є схвалений контент
        with get_db_session() as session:
            existing_content = session.query(Content).filter(
                Content.status == "approved"  # ✅ String замість enum
            ).first()
            
            if existing_content:
                logger.info("✅ Початкові дані вже існують")
                return
            
            # Додавання зразків контенту
            sample_content = [
                ("🤣 Українець купує новий iPhone. Продавець каже:\n- Тримайте, не загубіть!\n- Не переживайте, у мене є Find My iPhone!\n- А якщо воно не знайде?\n- То значить його вкрали москалі! 😂", "joke"),
                ("😂 Запитання: Що спільного між українським програмістом та борщем?\nВідповідь: Обидва можуть працювати на Python! 🐍🧠", "joke"),
                ("🔥 Зустрічаються два IT-шники:\n- Як справи?\n- Та нормально, працюю віддалено.\n- З дому?\n- Ні, з іншої планети! 🚀", "anekdot"),
                ("💰 Український стартап:\nДень 1: 'Ми зробимо революцію!'\nДень 30: 'Мам, можна грошей на хостинг?' 🤣", "meme"),
                ("🎯 Коли український розробник каже 'зараз полагодимо':\n⏰ Зараз = через годину\n📅 Скоро = через день\n🗓️ Незабаром = купуйте новий комп'ютер! 😄", "joke")
            ]
            
            for text, content_type in sample_content:
                content = Content(
                    author_id=ADMIN_ID,
                    author_user_id=ADMIN_ID,
                    text=text,
                    content_type=content_type,
                    status="approved",  # ✅ String замість enum
                    created_at=datetime.utcnow(),
                    published_at=datetime.utcnow()
                )
                session.add(content)
            
            session.commit()
            logger.info("✅ Додано зразків контенту")
            
    except Exception as e:
        logger.error(f"❌ Помилка додавання початкових даних: {e}")

# ===== СТАТИСТИЧНІ ФУНКЦІЇ =====
async def get_bot_statistics() -> Dict[str, Any]:
    """Отримати статистику бота"""
    try:
        if not DATABASE_AVAILABLE:
            return {
                "total_users": 0,
                "total_content": 0,
                "active_duels": 0,
                "database_status": "offline"
            }
            
        with get_db_session() as session:
            stats = {
                "total_users": session.query(User).count(),
                "active_users": session.query(User).filter(
                    User.last_active >= datetime.utcnow() - timedelta(days=7)
                ).count(),
                "total_content": session.query(Content).count(),
                "approved_content": session.query(Content).filter(
                    Content.status == "approved"
                ).count(),
                "pending_content": session.query(Content).filter(
                    Content.status == "pending"
                ).count(),
                "active_duels": session.query(Duel).filter(
                    Duel.status == "active"
                ).count(),
                "total_votes": session.query(DuelVote).count(),
                "database_status": "online"
            }
            
            return stats
            
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики: {e}")
        return {"database_status": "error", "error": str(e)}

# ===== ФУНКЦІЇ ОЧИСТКИ ТА ОПТИМІЗАЦІЇ =====
async def cleanup_old_data():
    """Очистка старих даних"""
    try:
        if not DATABASE_AVAILABLE:
            return
            
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        with get_db_session() as session:
            # Видалення старих відхилених заявок
            old_rejected = session.query(Content).filter(
                Content.status == "rejected",
                Content.created_at < cutoff_date
            ).count()
            
            if old_rejected > 0:
                session.query(Content).filter(
                    Content.status == "rejected",
                    Content.created_at < cutoff_date
                ).delete()
                
                logger.info(f"🧹 Видалено {old_rejected} старих відхилених контентів")
            
            # Завершення старих дуелей
            old_duels = session.query(Duel).filter(
                Duel.status == "active",
                Duel.created_at < cutoff_date
            ).count()
            
            if old_duels > 0:
                session.query(Duel).filter(
                    Duel.status == "active",
                    Duel.created_at < cutoff_date
                ).update({"status": "cancelled"})
                
                logger.info(f"🧹 Скасовано {old_duels} старих дуелей")
            
            session.commit()
            
    except Exception as e:
        logger.error(f"❌ Помилка очистки даних: {e}")

# ===== ЕКСПОРТ ФУНКЦІЙ =====
__all__ = [
    # Ініціалізація
    'init_db', 'get_db_session',
    
    # Користувачі
    'get_or_create_user', 'get_user_by_id', 'update_user_points', 'get_rank_by_points',
    
    # Контент
    'add_content_for_moderation', 'get_pending_content', 'moderate_content', 'get_random_approved_content',
    
    # Дуелі
    'create_duel', 'vote_in_duel',
    
    # Досягнення
    'create_default_achievements', 'check_user_achievements',
    
    # Адміністрування
    'ensure_admin_exists', 'add_initial_data', 'get_bot_statistics', 'cleanup_old_data',
    
    # Константи
    'CONTENT_TYPES', 'CONTENT_STATUSES', 'DUEL_STATUSES',
    'DATABASE_AVAILABLE', 'MODELS_LOADED'
]

logger.info(f"📦 Database функції завантажено: {len(__all__)} функцій")
logger.info(f"💾 Database доступна: {'✅' if DATABASE_AVAILABLE else '❌'}")
logger.info(f"📋 Models завантажені: {'✅' if MODELS_LOADED else '❌'}")