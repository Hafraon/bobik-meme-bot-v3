#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Ініціалізація та робота з базою даних 🧠😂🔥
"""

import logging
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings
from database.models import (
    Base, User, Content, Rating, Duel, DuelVote, 
    AdminAction, BotStatistics, ContentType, ContentStatus
)

logger = logging.getLogger(__name__)

# Створення движка бази даних
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Встановіть True для debug SQL запитів
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Створення фабрики сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def init_db():
    """Ініціалізація бази даних"""
    try:
        # Створення всіх таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("🔥 Таблиці бази даних створено!")
        
        # Додавання початкових даних
        await add_initial_data()
        
    except Exception as e:
        logger.error(f"😂 Помилка ініціалізації БД: {e}")
        raise

@contextmanager
def get_db_session():
    """Контекстний менеджер для роботи з БД"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"🧠 Помилка БД: {e}")
        raise
    finally:
        session.close()

async def add_initial_data():
    """Додавання початкових даних"""
    with get_db_session() as session:
        # Перевірка чи є вже дані
        existing_jokes = session.query(Content).filter_by(
            content_type=ContentType.JOKE,
            status=ContentStatus.APPROVED
        ).count()
        
        if existing_jokes == 0:
            await add_sample_jokes(session)
            
        existing_memes = session.query(Content).filter_by(
            content_type=ContentType.MEME,
            status=ContentStatus.APPROVED
        ).count()
        
        if existing_memes == 0:
            await add_sample_memes(session)

async def add_sample_jokes(session: Session):
    """Додавання зразкових анекдотів"""
    sample_jokes = [
        "🧠 Приходить программіст до лікаря:\n- Доктор, в мене болить рука!\n- А де саме?\n- В лівому кліку! 😂",
        
        "🔥 Зустрічаються два українці:\n- Як справи?\n- Та нормально, працюю в IT.\n- А що робиш?\n- Борщ доставляю через додаток! 😂",
        
        "😂 Учитель запитує:\n- Петрику, скільки буде 2+2?\n- А ви про що? Про гривні чи про долари? 🧠",
        
        "🔥 Покупець у магазині:\n- Скільки коштує хліб?\n- 20 гривень.\n- А вчора був 15!\n- Вчора ви його і не купили! 😂",
        
        "🧠 Дружина чоловікові:\n- Любий, я схудла на 5 кг!\n- А де вони?\n- В холодильнику! 😂🔥",
        
        "😂 Син питає батька:\n- Тату, а що таке політика?\n- Це коли багато людей говорять, а нічого не роблять.\n- А що таке демократія?\n- Це коли всі мають право говорити, але слухає тільки мама! 🧠",
        
        "🔥 Лікар пацієнтові:\n- Ви кури?\n- Ні.\n- П'єте?\n- Ні.\n- Тоді живіть як хочете - все одно довго протягнете! 😂",
        
        "🧠 Заходить чоловік до аптеки:\n- Дайте щось від голови!\n- А що саме болить?\n- Дружина! 😂🔥",
        
        "😂 Розмова в офісі:\n- Ти чому такий веселий?\n- Зарплату підняли!\n- На скільки?\n- На другий поверх! 🧠",
        
        "🔥 Студент здає екзамен:\n- Розкажіть про Наполеона.\n- Не можу, ми не знайомі особисто.\n- Тоді про Пушкіна.\n- Теж не знайомі.\n- Незадовільно!\n- А з ким ви знайомі?\n- З вами... і то погано! 😂"
    ]
    
    for joke_text in sample_jokes:
        joke = Content(
            content_type=ContentType.JOKE,
            text=joke_text,
            status=ContentStatus.APPROVED,
            author_id=settings.ADMIN_ID,  # Від імені адміністратора
            views=0,
            likes=0
        )
        session.add(joke)
    
    logger.info(f"🔥 Додано {len(sample_jokes)} початкових анекдотів")

async def add_sample_memes(session: Session):
    """Додавання зразкових мемів (посилання)"""
    sample_memes = [
        {
            "caption": "🧠 Коли нарешті зрозумів як працює async/await 😂",
            "url": "https://i.imgur.com/placeholder1.jpg"
        },
        {
            "caption": "🔥 Настрій понеділка vs настрій п'ятниці 😂",
            "url": "https://i.imgur.com/placeholder2.jpg"
        },
        {
            "caption": "🧠 Коли код працює з першого разу 😂🔥",
            "url": "https://i.imgur.com/placeholder3.jpg"
        }
    ]
    
    for meme_data in sample_memes:
        meme = Content(
            content_type=ContentType.MEME,
            text=meme_data["caption"],
            file_url=meme_data["url"],
            status=ContentStatus.APPROVED,
            author_id=settings.ADMIN_ID,
            views=0,
            likes=0
        )
        session.add(meme)
    
    logger.info(f"🔥 Додано {len(sample_memes)} початкових мемів")

# ===== ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ РОБОТИ З КОРИСТУВАЧАМИ =====

async def get_or_create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
    """Отримання або створення користувача"""
    with get_db_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            session.commit()
            logger.info(f"🧠 Створено нового користувача: {user_id}")
        else:
            # Оновлення інформації користувача
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.last_active = datetime.utcnow()
            session.commit()
        
        return user

async def update_user_points(user_id: int, points: int, reason: str = ""):
    """Оновлення балів користувача"""
    with get_db_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.points += points
            
            # Оновлення рангу
            new_rank = get_rank_by_points(user.points)
            if new_rank != user.rank:
                user.rank = new_rank
                logger.info(f"🔥 Користувач {user_id} отримав новий ранг: {new_rank}")
            
            session.commit()
            logger.info(f"😂 Користувач {user_id} отримав {points} балів за: {reason}")

def get_rank_by_points(points: int) -> str:
    """Визначення рангу по балах"""
    for min_points in sorted(settings.RANKS.keys(), reverse=True):
        if points >= min_points:
            return settings.RANKS[min_points]
    return settings.RANKS[0]

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З КОНТЕНТОМ =====

async def get_random_joke() -> Optional[Content]:
    """Отримання випадкового анекдоту"""
    with get_db_session() as session:
        joke = session.query(Content).filter(
            Content.content_type == ContentType.JOKE,
            Content.status == ContentStatus.APPROVED
        ).order_by(func.random()).first()
        
        if joke:
            joke.views += 1
            session.commit()
        
        return joke

async def get_random_meme() -> Optional[Content]:
    """Отримання випадкового мему"""
    with get_db_session() as session:
        meme = session.query(Content).filter(
            Content.content_type == ContentType.MEME,
            Content.status == ContentStatus.APPROVED
        ).order_by(func.random()).first()
        
        if meme:
            meme.views += 1
            session.commit()
        
        return meme

# ===== НОВА ФУНКЦІЯ! =====
async def add_content_for_moderation(user_id: int, content_type: str, text: str, file_id: str = None) -> Content:
    """Додати контент на модерацію"""
    with get_db_session() as session:
        # Конвертуємо string в enum
        if content_type == "joke":
            ct = ContentType.JOKE
        elif content_type == "meme":
            ct = ContentType.MEME
        else:
            raise ValueError(f"Невідомий тип контенту: {content_type}")
        
        content = Content(
            content_type=ct,
            text=text,
            file_id=file_id,
            author_id=user_id,
            status=ContentStatus.PENDING
        )
        session.add(content)
        session.commit()
        
        # Оновлення статистики користувача
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            if ct == ContentType.JOKE:
                user.jokes_submitted += 1
            else:
                user.memes_submitted += 1
            session.commit()
        
        logger.info(f"🧠 Новий контент на модерацію від {user_id}: {content.id}")
        return content

async def submit_content(user_id: int, content_type: ContentType, text: str = None, file_id: str = None) -> Content:
    """Подача контенту на модерацію (стара функція для сумісності)"""
    ct_string = "joke" if content_type == ContentType.JOKE else "meme"
    return await add_content_for_moderation(user_id, ct_string, text, file_id)

async def get_pending_content() -> List[Content]:
    """Отримання контенту на модерацію"""
    with get_db_session() as session:
        return session.query(Content).filter(
            Content.status == ContentStatus.PENDING
        ).order_by(Content.created_at).all()

async def moderate_content(content_id: int, moderator_id: int, approve: bool, comment: str = None):
    """Модерація контенту"""
    with get_db_session() as session:
        content = session.query(Content).filter(Content.id == content_id).first()
        if content:
            content.status = ContentStatus.APPROVED if approve else ContentStatus.REJECTED
            content.moderator_id = moderator_id
            content.moderation_comment = comment
            content.moderated_at = func.now()
            
            # Оновлення статистики автора
            author = session.query(User).filter(User.id == content.author_id).first()
            if author and approve:
                if content.content_type == ContentType.JOKE:
                    author.jokes_approved += 1
                else:
                    author.memes_approved += 1
                
                # НОВЕ! Нарахування балів за схвалення
                author.points += settings.POINTS_FOR_APPROVAL
                new_rank = get_rank_by_points(author.points)
                if new_rank != author.rank:
                    author.rank = new_rank
                
                session.commit()
                logger.info(f"🔥 Автор {author.id} отримав +{settings.POINTS_FOR_APPROVAL} балів за схвалення контенту")
            
            # Запис дії адміністратора
            admin_action = AdminAction(
                admin_id=moderator_id,
                action_type="approve" if approve else "reject",
                target_type="content",
                target_id=content_id,
                reason=comment
            )
            session.add(admin_action)
            session.commit()
            
            logger.info(f"🔥 Контент {content_id} {'схвалено' if approve else 'відхилено'}")

# ===== НОВА ФУНКЦІЯ ДЛЯ НАРАХУВАННЯ БАЛІВ ЗА ЛАЙКИ! =====
async def add_content_rating(user_id: int, content_id: int, action_type: str, points: int = 0) -> bool:
    """Додати оцінку контенту та нарахувати бали автору"""
    with get_db_session() as session:
        # Перевіряємо чи не ставив вже оцінку
        existing_rating = session.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.content_id == content_id,
            Rating.action_type == action_type
        ).first()
        
        if existing_rating:
            return False  # Вже ставив оцінку
        
        # Додаємо нову оцінку
        rating = Rating(
            user_id=user_id,
            content_id=content_id,
            action_type=action_type,
            points_awarded=points
        )
        session.add(rating)
        
        # Оновлюємо статистику контенту
        content = session.query(Content).filter(Content.id == content_id).first()
        if content:
            if action_type == "like":
                content.likes += 1
                
                # НОВЕ! Нарахування балів автору за лайк
                author = session.query(User).filter(User.id == content.author_id).first()
                if author and author.id != user_id:  # Не можна лайкати свій контент
                    # Перевіряємо ліміт балів за лайки на день
                    today = datetime.utcnow().date()
                    today_bonus_points = session.query(func.sum(Rating.points_awarded)).filter(
                        Rating.content_id.in_(
                            session.query(Content.id).filter(Content.author_id == author.id)
                        ),
                        Rating.action_type == "like",
                        func.date(Rating.created_at) == today
                    ).scalar() or 0
                    
                    if today_bonus_points < 10:  # Максимум 10 балів на день за лайки
                        author.points += 1
                        rating.points_awarded = 1  # Записуємо що автор отримав бал
                        
                        # Оновлюємо ранг якщо потрібно
                        new_rank = get_rank_by_points(author.points)
                        if new_rank != author.rank:
                            author.rank = new_rank
                        
                        logger.info(f"💖 Автор {author.id} отримав +1 бал за лайк контенту {content_id}")
                    
            elif action_type == "dislike":
                content.dislikes += 1
            elif action_type == "share":
                content.likes += 1  # Поки що як лайк
        
        session.commit()
        return True

# ===== ФУНКЦІЇ ДЛЯ СТАТИСТИКИ =====

async def get_user_stats(user_id: int) -> dict:
    """Отримання статистики користувача"""
    with get_db_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        return {
            "user": user,
            "total_submissions": user.jokes_submitted + user.memes_submitted,
            "total_approved": user.jokes_approved + user.memes_approved,
            "approval_rate": round(
                (user.jokes_approved + user.memes_approved) / max(user.jokes_submitted + user.memes_submitted, 1) * 100,
                1
            )
        }

async def get_leaderboard(limit: int = 10) -> List[User]:
    """Отримання таблиці лідерів"""
    with get_db_session() as session:
        return session.query(User).order_by(User.points.desc()).limit(limit).all()