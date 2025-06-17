#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери для роботи з контентом (меми та анекдоти) 🧠😂🔥
"""

import logging
import random
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

# Fallback імпорти
try:
    from config.settings import Settings
    settings = Settings()
    
    # Додаємо недостатні атрибути
    if not hasattr(settings, 'POINTS_FOR_SUBMISSION'):
        settings.POINTS_FOR_SUBMISSION = 10
    if not hasattr(settings, 'POINTS_FOR_REACTION'):
        settings.POINTS_FOR_REACTION = 5
    if not hasattr(settings, 'MAX_JOKE_LENGTH'):
        settings.MAX_JOKE_LENGTH = 1000
    if not hasattr(settings, 'MAX_MEME_CAPTION_LENGTH'):
        settings.MAX_MEME_CAPTION_LENGTH = 200
        
except ImportError:
    # Fallback settings
    import os
    class FallbackSettings:
        POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
        POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
        MAX_JOKE_LENGTH = int(os.getenv("MAX_JOKE_LENGTH", "1000"))
        MAX_MEME_CAPTION_LENGTH = int(os.getenv("MAX_MEME_CAPTION_LENGTH", "200"))
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    
    settings = FallbackSettings()

# EMOJI константи
EMOJI = {
    "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", 
    "heart": "❤️", "like": "👍", "dislike": "👎", "thinking": "🤔",
    "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
    "new": "🆕", "time": "⏰", "profile": "👤", "vs": "⚔️"
}

# FSM для подачі контенту
class SubmissionStates(StatesGroup):
    waiting_for_content = State()

# Прості моделі даних (fallback)
class ContentItem:
    def __init__(self, id, text, views=0, likes=0, dislikes=0, file_id=None):
        self.id = id
        self.text = text
        self.views = views
        self.likes = likes
        self.dislikes = dislikes
        self.file_id = file_id

# Тимчасове сховище контенту (в продакшені замінити на БД)
SAMPLE_JOKES = [
    ContentItem(1, "Чому програмісти люблять природу? Бо там немає багів!", 150, 23, 2),
    ContentItem(2, "Що робить програміст коли не може заснути? Рахує овець від нуля!", 89, 15, 1),
    ContentItem(3, "Чому програмісти п'ють каву? Бо без неї код не компілюється!", 234, 45, 3),
    ContentItem(4, "Що таке рекурсія? Дивись визначення рекурсії!", 67, 12, 0),
    ContentItem(5, "Скільки програмістів потрібно щоб закрутити лампочку? Жодного - це апаратна проблема!", 178, 34, 2)
]

SAMPLE_MEMES = [
    ContentItem(6, "Коли код нарешті запрацював з першого разу", 345, 67, 4),
    ContentItem(7, "Коли знайшов баг в продакшені о 17:59 в п'ятницю", 289, 54, 8),
    ContentItem(8, "Коли замовник каже 'швидка зміна'", 123, 28, 3)
]

async def get_random_joke():
    """Отримання випадкового анекдоту"""
    try:
        # Спроба отримання з БД
        from database.database import get_random_joke as db_get_joke
        joke = await db_get_joke()
        if joke:
            return joke
    except ImportError:
        pass
    
    # Fallback - використовуємо зразки
    joke = random.choice(SAMPLE_JOKES)
    joke.views += 1
    return joke

async def get_random_meme():
    """Отримання випадкового мему"""
    try:
        # Спроба отримання з БД
        from database.database import get_random_meme as db_get_meme
        meme = await db_get_meme()
        if meme:
            return meme
    except ImportError:
        pass
    
    # Fallback - використовуємо зразки
    meme = random.choice(SAMPLE_MEMES)
    meme.views += 1
    return meme

async def update_user_points(user_id: int, points: int, reason: str):
    """Нарахування балів користувачу"""
    try:
        from database.database import update_user_points as db_update_points
        await db_update_points(user_id, points, reason)
    except ImportError:
        # Fallback - логування
        logger.info(f"👤 Користувач {user_id}: +{points} балів за {reason}")

# Основні команди
async def cmd_meme(message: Message):
    """Команда /meme"""
    await send_meme(message)

async def cmd_anekdot(message: Message):
    """Команда /anekdot"""
    await send_joke(message)

async def send_meme(message: Message, from_callback: bool = False):
    """Надсилання випадкового мему з нарахуванням балів"""
    user_id = message.from_user.id
    
    # Отримання випадкового мему
    meme = await get_random_meme()
    
    if not meme:
        await message.answer("😅 Меми закінчилися! Надішліть свої через /submit")
        return
    
    # Контекстне привітання
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        greeting = f"{EMOJI['fire']} Доброго ранку!"
    elif 12 <= current_hour < 18:
        greeting = f"{EMOJI['laugh']} Гарного дня!"
    elif 18 <= current_hour < 23:
        greeting = f"{EMOJI['star']} Доброго вечора!"
    else:
        greeting = f"{EMOJI['thinking']} Доброї ночі!"
    
    # Клавіатура для взаємодії
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['like']} Подобається (+{settings.POINTS_FOR_REACTION})", 
                callback_data=f"like_content:{meme.id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['dislike']} Не подобається", 
                callback_data=f"dislike_content:{meme.id}"
            )
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Ще мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати свій", callback_data="submit_content"),
            InlineKeyboardButton(text=f"{EMOJI['profile']} Профіль", callback_data="show_profile")
        ]
    ])
    
    caption = (
        f"{greeting}\n\n"
        f"{meme.text}\n\n"
        f"{EMOJI['fire']} Переглядів: {meme.views} | "
        f"{EMOJI['like']} {meme.likes} | "
        f"{EMOJI['dislike']} {meme.dislikes}"
    )
    
    # Надсилання мему
    if meme.file_id:
        try:
            await message.answer_photo(
                photo=meme.file_id,
                caption=caption,
                reply_markup=keyboard
            )
        except:
            await message.answer(caption, reply_markup=keyboard)
    else:
        await message.answer(caption, reply_markup=keyboard)
    
    # Нарахування балів за перегляд
    await update_user_points(user_id, 1, "перегляд мему")
    
    if not from_callback:
        logger.info(f"😂 Користувач {user_id} отримав мем {meme.id}")

async def send_joke(message: Message, from_callback: bool = False):
    """Надсилання випадкового анекдоту з нарахуванням балів"""
    user_id = message.from_user.id
    
    # Отримання випадкового анекдоту
    joke = await get_random_joke()
    
    if not joke:
        await message.answer("😅 Анекдоти закінчилися! Надішліть свої через /submit")
        return
    
    # Контекстне привітання
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        greeting = f"{EMOJI['fire']} Доброго ранку!"
    elif 12 <= current_hour < 18:
        greeting = f"{EMOJI['brain']} Гарного дня!"
    elif 18 <= current_hour < 23:
        greeting = f"{EMOJI['star']} Доброго вечора!"
    else:
        greeting = f"{EMOJI['thinking']} Доброї ночі!"
    
    # Клавіатура для взаємодії
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['like']} Подобається (+{settings.POINTS_FOR_REACTION})", 
                callback_data=f"like_content:{joke.id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['dislike']} Не подобається", 
                callback_data=f"dislike_content:{joke.id}"
            )
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Ще анекдот", callback_data="get_joke"),
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати свій", callback_data="submit_content"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Дуель", callback_data="start_duel")
        ]
    ])
    
    response_text = (
        f"{greeting}\n\n"
        f"{joke.text}\n\n"
        f"{EMOJI['fire']} Переглядів: {joke.views} | "
        f"{EMOJI['like']} {joke.likes} | "
        f"{EMOJI['dislike']} {joke.dislikes}"
    )
    
    await message.answer(response_text, reply_markup=keyboard)
    
    # Нарахування балів за перегляд
    await update_user_points(user_id, 1, "перегляд анекдоту")
    
    if not from_callback:
        logger.info(f"🧠 Користувач {user_id} отримав анекдот {joke.id}")

async def cmd_submit(message: Message, state: FSMContext):
    """Команда /submit для подачі контенту"""
    user_id = message.from_user.id
    
    # Перевіряємо чи є текст після команди
    text_parts = message.text.split(' ', 1)
    if len(text_parts) > 1:
        # Є текст після команди - це анекдот
        joke_text = text_parts[1].strip()
        
        if len(joke_text) > settings.MAX_JOKE_LENGTH:
            await message.answer(
                f"{EMOJI['warning']} Анекдот занадто довгий! "
                f"Максимум {settings.MAX_JOKE_LENGTH} символів."
            )
            return
        
        # Нарахування балів за подачу
        await update_user_points(user_id, settings.POINTS_FOR_SUBMISSION, "подача анекдоту")
        
        await message.answer(
            f"{EMOJI['check']} <b>Дякую за твій анекдот!</b>\n\n"
            f"{EMOJI['brain']} Він відправлений на модерацію\n"
            f"{EMOJI['fire']} Ти отримав +{settings.POINTS_FOR_SUBMISSION} балів\n\n"
            f"{EMOJI['info']} При схваленні отримаєш ще бали!"
        )
        
        # Повідомлення адміністратору
        if settings.ADMIN_ID:
            try:
                await message.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['new']} <b>Новий анекдот на модерацію!</b>\n\n"
                    f"{EMOJI['profile']} <b>Від:</b> {message.from_user.first_name or 'Невідомий'} "
                    f"(@{message.from_user.username or 'без username'})\n"
                    f"{EMOJI['brain']} <b>Текст:</b>\n{joke_text}"
                )
            except Exception as e:
                logger.error(f"Не вдалося повідомити адміністратора: {e}")
        
        logger.info(f"🔥 Користувач {user_id} надіслав анекдот на модерацію")
        
    else:
        # Немає тексту - показуємо інструкції
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="submit_joke"),
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="submit_meme")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['star']} Мій профіль", callback_data="show_profile")
            ]
        ])
        
        await message.answer(
            f"{EMOJI['fire']} <b>Що хочеш надіслати?</b>\n\n"
            f"{EMOJI['brain']} <b>Анекдот</b> - текстовий жарт (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
            f"{EMOJI['laugh']} <b>Мем</b> - картинка з підписом (+{settings.POINTS_FOR_SUBMISSION} балів)\n\n"
            f"{EMOJI['thinking']} <b>Приклад анекдоту:</b>\n"
            f"<code>/submit Чому програмісти п'ють каву? Бо без неї код не компілюється!</code>",
            reply_markup=keyboard
        )

async def handle_photo_submission(message: Message):
    """Обробка надісланого фото як мему"""
    if not message.photo:
        return
    
    user_id = message.from_user.id
    photo = message.photo[-1]  # Найбільший розмір
    caption = message.caption or f"{EMOJI['laugh']} Мем без підпису"
    
    if len(caption) > settings.MAX_MEME_CAPTION_LENGTH:
        await message.answer(
            f"{EMOJI['warning']} Підпис занадто довгий! "
            f"Максимум {settings.MAX_MEME_CAPTION_LENGTH} символів."
        )
        return
    
    # Нарахування балів за подачу
    await update_user_points(user_id, settings.POINTS_FOR_SUBMISSION, "подача мему")
    
    await message.answer(
        f"{EMOJI['check']} <b>Дякую за твій мем!</b>\n\n"
        f"{EMOJI['laugh']} Він відправлений на модерацію\n"
        f"{EMOJI['fire']} Ти отримав +{settings.POINTS_FOR_SUBMISSION} балів\n\n"
        f"{EMOJI['info']} При схваленні отримаєш ще бали!"
    )
    
    # Повідомлення адміністратору
    if settings.ADMIN_ID:
        try:
            await message.bot.send_photo(
                settings.ADMIN_ID,
                photo=photo.file_id,
                caption=f"{EMOJI['new']} <b>Новий мем на модерацію!</b>\n\n"
                       f"{EMOJI['profile']} <b>Від:</b> {message.from_user.first_name or 'Невідомий'}\n"
                       f"{EMOJI['laugh']} <b>Підпис:</b> {caption}"
            )
        except Exception as e:
            logger.error(f"Не вдалося повідомити адміністратора: {e}")
    
    logger.info(f"🔥 Користувач {user_id} надіслав мем на модерацію")

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_like_content(callback_query: CallbackQuery):
    """Обробка лайка контенту"""
    content_id = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    
    # Нарахування балів за лайк
    await update_user_points(user_id, settings.POINTS_FOR_REACTION, "лайк контенту")
    
    await callback_query.answer(
        f"{EMOJI['like']} Дякую за оцінку! +{settings.POINTS_FOR_REACTION} балів"
    )

async def callback_dislike_content(callback_query: CallbackQuery):
    """Обробка дизлайка контенту"""
    content_id = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    
    # Мінімальні бали за дизлайк (теж активність)
    await update_user_points(user_id, 1, "дизлайк контенту")
    
    await callback_query.answer(f"{EMOJI['dislike']} Дякую за відгук! +1 бал")

async def callback_get_meme(callback_query: CallbackQuery):
    """Callback для отримання мему"""
    await send_meme(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_get_joke(callback_query: CallbackQuery):
    """Callback для отримання анекдоту"""
    await send_joke(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_submit_content(callback_query: CallbackQuery):
    """Callback для подачі контенту"""
    await callback_query.message.answer(
        f"{EMOJI['fire']} <b>Як надіслати контент:</b>\n\n"
        f"{EMOJI['brain']} <b>Анекдот:</b> /submit і текст анекдоту\n"
        f"{EMOJI['laugh']} <b>Мем:</b> надішли картинку з підписом\n\n"
        f"{EMOJI['star']} За кожну подачу: +{settings.POINTS_FOR_SUBMISSION} балів\n\n"
        f"{EMOJI['thinking']} <b>Приклад:</b>\n"
        f"<code>/submit Чому програмісти люблять природу? Бо там немає багів!</code>"
    )
    await callback_query.answer()

async def callback_submit_joke(callback_query: CallbackQuery):
    """Callback для подачі анекдоту"""
    await callback_query.message.answer(
        f"{EMOJI['brain']} <b>Надішли свій анекдот!</b>\n\n"
        f"Просто напиши текст анекдоту у наступному повідомленні\n"
        f"Максимум {settings.MAX_JOKE_LENGTH} символів\n\n"
        f"{EMOJI['thinking']} <b>Приклад:</b>\n"
        f"Чому програмісти люблять природу? Бо в ній немає багів!"
    )
    await callback_query.answer()

async def callback_submit_meme(callback_query: CallbackQuery):
    """Callback для подачі мему"""
    await callback_query.message.answer(
        f"{EMOJI['laugh']} <b>Надішли свій мем!</b>\n\n"
        f"Прикріпи картинку з підписом\n"
        f"Максимум {settings.MAX_MEME_CAPTION_LENGTH} символів у підписі\n\n"
        f"{EMOJI['brain']} Картинка + підпис = готовий мем!"
    )
    await callback_query.answer()

def register_content_handlers(dp: Dispatcher):
    """Реєстрація хендлерів контенту"""
    
    # Команди
    dp.message.register(cmd_meme, Command("meme"))
    dp.message.register(cmd_anekdot, Command("anekdot"))
    dp.message.register(cmd_submit, Command("submit"))
    
    # Обробка фото
    dp.message.register(handle_photo_submission, F.photo)
    
    # Callback запити
    dp.callback_query.register(callback_like_content, F.data.startswith("like_content:"))
    dp.callback_query.register(callback_dislike_content, F.data.startswith("dislike_content:"))
    dp.callback_query.register(callback_get_meme, F.data == "get_meme")
    dp.callback_query.register(callback_get_joke, F.data == "get_joke")
    dp.callback_query.register(callback_submit_content, F.data == "submit_content")
    dp.callback_query.register(callback_submit_joke, F.data == "submit_joke")
    dp.callback_query.register(callback_submit_meme, F.data == "submit_meme")
    
    logger.info("✅ Content handlers зареєстровані")