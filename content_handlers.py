#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери для роботи з контентом 🧠😂🔥
"""

import logging
import random
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.settings import TEXTS, EMOJI, TIME_GREETINGS, settings
from database.database import (
    get_random_joke, get_random_meme, submit_content, 
    update_user_points, get_or_create_user
)
from database.models import ContentType

logger = logging.getLogger(__name__)

# FSM для подачі контенту
class SubmissionStates(StatesGroup):
    waiting_for_content = State()

async def cmd_meme(message: Message):
    """Команда /meme"""
    await send_meme(message)

async def cmd_anekdot(message: Message):
    """Команда /anekdot"""
    await send_joke(message)

async def send_meme(message: Message, from_callback: bool = False):
    """Надсилання випадкового мему"""
    user_id = message.from_user.id
    
    # Отримання випадкового мему
    meme = await get_random_meme()
    
    if not meme:
        await message.answer(TEXTS["no_content"])
        return
    
    # Контекстне привітання залежно від часу
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        greeting = random.choice(TIME_GREETINGS["morning"])
    elif 12 <= current_hour < 18:
        greeting = random.choice(TIME_GREETINGS["day"])
    elif 18 <= current_hour < 23:
        greeting = random.choice(TIME_GREETINGS["evening"])
    else:
        greeting = random.choice(TIME_GREETINGS["night"])
    
    # Клавіатура для взаємодії
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['like']} Подобається", callback_data=f"like_content:{meme.id}"),
            InlineKeyboardButton(text=f"{EMOJI['dislike']} Не подобається", callback_data=f"dislike_content:{meme.id}")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Ще мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
        ]
    ])
    
    caption = f"{greeting}\n\n{meme.text}\n\n{EMOJI['fire']} Переглядів: {meme.views}"
    
    try:
        if meme.file_id:
            # Якщо є file_id, надсилаємо через нього
            await message.answer_photo(
                photo=meme.file_id,
                caption=caption,
                reply_markup=keyboard
            )
        elif meme.file_url:
            # Якщо є URL, надсилаємо як фото
            await message.answer_photo(
                photo=meme.file_url,
                caption=caption,
                reply_markup=keyboard
            )
        else:
            # Якщо немає файлу, надсилаємо як текст
            await message.answer(
                f"{caption}\n\n{EMOJI['brain']} {meme.text}",
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Помилка надсилання мему: {e}")
        await message.answer(
            f"{caption}\n\n{EMOJI['brain']} {meme.text}",
            reply_markup=keyboard
        )
    
    # Нарахування балів за перегляд
    await update_user_points(user_id, 1, "перегляд мему")
    
    if not from_callback:
        logger.info(f"😂 Користувач {user_id} отримав мем {meme.id}")

async def send_joke(message: Message, from_callback: bool = False):
    """Надсилання випадкового анекдоту"""
    user_id = message.from_user.id
    
    # Отримання випадкового анекдоту
    joke = await get_random_joke()
    
    if not joke:
        await message.answer(TEXTS["no_content"])
        return
    
    # Контекстне привітання
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        greeting = random.choice(TIME_GREETINGS["morning"])
    elif 12 <= current_hour < 18:
        greeting = random.choice(TIME_GREETINGS["day"])
    elif 18 <= current_hour < 23:
        greeting = random.choice(TIME_GREETINGS["evening"])
    else:
        greeting = random.choice(TIME_GREETINGS["night"])
    
    # Клавіатура для взаємодії
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['like']} Подобається", callback_data=f"like_content:{joke.id}"),
            InlineKeyboardButton(text=f"{EMOJI['dislike']} Не подобається", callback_data=f"dislike_content:{joke.id}")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Ще анекдот", callback_data="get_joke"),
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
        ]
    ])
    
    response_text = f"{greeting}\n\n{joke.text}\n\n{EMOJI['fire']} Переглядів: {joke.views}"
    
    await message.answer(
        response_text,
        reply_markup=keyboard
    )
    
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
        
        # Подача анекдоту
        content = await submit_content(
            user_id=user_id,
            content_type=ContentType.JOKE,
            text=joke_text
        )
        
        # Нарахування балів
        await update_user_points(user_id, settings.POINTS_FOR_SUBMISSION, "подача анекдоту")
        
        await message.answer(TEXTS["submission_received"])
        
        # Повідомлення адміністратору
        try:
            await message.bot.send_message(
                settings.ADMIN_ID,
                f"{EMOJI['new']} <b>Новий анекдот на модерацію!</b>\n\n"
                f"{EMOJI['profile']} <b>Від:</b> {message.from_user.first_name or 'Невідомий'} "
                f"(@{message.from_user.username or 'без username'})\n"
                f"{EMOJI['brain']} <b>Текст:</b>\n{joke_text}\n\n"
                f"Команди: /approve_{content.id} або /reject_{content.id}"
            )
        except Exception as e:
            logger.error(f"Не вдалося повідомити адміністратора: {e}")
        
        logger.info(f"🔥 Користувач {user_id} надіслав анекдот на модерацію")
        
    else:
        # Немає тексту - запитуємо що хоче надіслати
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="submit_joke"),
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="submit_meme")
            ]
        ])
        
        await message.answer(
            f"{EMOJI['fire']} <b>Що хочеш надіслати?</b>\n\n"
            f"{EMOJI['brain']} <b>Анекдот</b> - текстовий жарт\n"
            f"{EMOJI['laugh']} <b>Мем</b> - картинка з підписом",
            reply_markup=keyboard
        )

async def handle_photo_submission(message: Message):
    """Обробка надісланого фото як мему"""
    user_id = message.from_user.id
    
    if not message.photo:
        return
    
    # Отримання найбільшого розміру фото
    photo = message.photo[-1]
    
    # Підпис до мему
    caption = message.caption or f"{EMOJI['laugh']} Мем без підпису"
    
    if len(caption) > settings.MAX_MEME_CAPTION_LENGTH:
        await message.answer(
            f"{EMOJI['warning']} Підпис занадто довгий! "
            f"Максимум {settings.MAX_MEME_CAPTION_LENGTH} символів."
        )
        return
    
    # Подача мему
    content = await submit_content(
        user_id=user_id,
        content_type=ContentType.MEME,
        text=caption,
        file_id=photo.file_id
    )
    
    # Нарахування балів
    await update_user_points(user_id, settings.POINTS_FOR_SUBMISSION, "подача мему")
    
    await message.answer(TEXTS["submission_received"])
    
    # Повідомлення адміністратору
    try:
        await message.bot.send_photo(
            settings.ADMIN_ID,
            photo=photo.file_id,
            caption=f"{EMOJI['new']} <b>Новий мем на модерацію!</b>\n\n"
                   f"{EMOJI['profile']} <b>Від:</b> {message.from_user.first_name or 'Невідомий'} "
                   f"(@{message.from_user.username or 'без username'})\n"
                   f"{EMOJI['laugh']} <b>Підпис:</b> {caption}\n\n"
                   f"Команди: /approve_{content.id} або /reject_{content.id}"
        )
    except Exception as e:
        logger.error(f"Не вдалося повідомити адміністратора: {e}")
    
    logger.info(f"🔥 Користувач {user_id} надіслав мем на модерацію")

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_like_content(callback_query: CallbackQuery):
    """Обробка лайка контенту"""
    content_id = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    
    # Логіка лайка (можна додати перевірку чи вже лайкав)
    from database.database import get_db_session
    from database.models import Content, Rating
    
    with get_db_session() as session:
        # Перевірка чи не лайкав вже
        existing_rating = session.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.content_id == content_id,
            Rating.action_type == "like"
        ).first()
        
        if existing_rating:
            await callback_query.answer(f"{EMOJI['warning']} Ти вже оцінив цей контент!")
            return
        
        # Додавання лайка
        content = session.query(Content).filter(Content.id == content_id).first()
        if content:
            content.likes += 1
            
            # Додавання запису про рейтинг
            rating = Rating(
                user_id=user_id,
                content_id=content_id,
                action_type="like",
                points_awarded=settings.POINTS_FOR_REACTION
            )
            session.add(rating)
            session.commit()
    
    # Нарахування балів користувачу
    await update_user_points(user_id, settings.POINTS_FOR_REACTION, "лайк контенту")
    
    await callback_query.answer(f"{EMOJI['like']} Дякую за оцінку! +{settings.POINTS_FOR_REACTION} балів")

async def callback_dislike_content(callback_query: CallbackQuery):
    """Обробка дизлайка контенту"""
    content_id = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    
    # Аналогічна логіка для дизлайка
    from database.database import get_db_session
    from database.models import Content, Rating
    
    with get_db_session() as session:
        existing_rating = session.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.content_id == content_id,
            Rating.action_type == "dislike"
        ).first()
        
        if existing_rating:
            await callback_query.answer(f"{EMOJI['warning']} Ти вже оцінив цей контент!")
            return
        
        content = session.query(Content).filter(Content.id == content_id).first()
        if content:
            content.dislikes += 1
            
            rating = Rating(
                user_id=user_id,
                content_id=content_id,
                action_type="dislike",
                points_awarded=1  # Менше балів за дизлайк
            )
            session.add(rating)
            session.commit()
    
    await update_user_points(user_id, 1, "дизлайк контенту")
    await callback_query.answer(f"{EMOJI['dislike']} Дякую за відгук! +1 бал")

async def callback_submit_joke(callback_query: CallbackQuery):
    """Callback для подачі анекдоту"""
    await callback_query.message.answer(
        f"{EMOJI['brain']} <b>Надішли свій анекдот!</b>\n\n"
        f"{EMOJI['fire']} Просто напиши текст анекдоту у наступному повідомленні\n"
        f"{EMOJI['star']} Максимум {settings.MAX_JOKE_LENGTH} символів\n\n"
        f"{EMOJI['thinking']} <b>Приклад:</b>\n"
        f"Чому програмісти люблять природу? Бо в ній немає багів! {EMOJI['laugh']}"
    )
    await callback_query.answer()

async def callback_submit_meme(callback_query: CallbackQuery):
    """Callback для подачі мему"""
    await callback_query.message.answer(
        f"{EMOJI['laugh']} <b>Надішли свій мем!</b>\n\n"
        f"{EMOJI['fire']} Прикріпи картинку з підписом\n"
        f"{EMOJI['star']} Максимум {settings.MAX_MEME_CAPTION_LENGTH} символів у підписі\n\n"
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
    dp.callback_query.register(callback_submit_joke, F.data == "submit_joke")
    dp.callback_query.register(callback_submit_meme, F.data == "submit_meme")