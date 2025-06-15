#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Основні команди бота 🧠😂🔥
"""

import logging
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import TEXTS, EMOJI
from database.database import get_or_create_user, update_user_points

logger = logging.getLogger(__name__)

async def cmd_start(message: Message):
    """Обробка команди /start"""
    user = message.from_user
    
    # Створення або оновлення користувача
    await get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Клавіатура швидких дій
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати жарт", callback_data="submit_content"),
            InlineKeyboardButton(text=f"{EMOJI['profile']} Профіль", callback_data="show_profile")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['calendar']} Щоденна розсилка", callback_data="toggle_daily"),
            InlineKeyboardButton(text=f"{EMOJI['top']} ТОП користувачів", callback_data="show_leaderboard")
        ]
    ])
    
    await message.answer(
        TEXTS["start"],
        reply_markup=keyboard
    )
    
    logger.info(f"🧠 Користувач {user.id} запустив бота")

async def cmd_help(message: Message):
    """Обробка команди /help"""
    user = message.from_user
    
    # Клавіатура з корисними посиланнями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Спробувати мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Спробувати анекдот", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Почати заробляти бали", callback_data="submit_content")
        ]
    ])
    
    await message.answer(
        TEXTS["help"],
        reply_markup=keyboard
    )
    
    logger.info(f"😂 Користувач {user.id} подивився довідку")

async def cmd_stats(message: Message):
    """Обробка команди /stats - загальна статистика бота"""
    from database.database import get_db_session
    from database.models import User, Content, Duel
    
    with get_db_session() as session:
        total_users = session.query(User).count()
        total_content = session.query(Content).count()
        total_duels = session.query(Duel).count()
        
        # Топ користувач
        top_user = session.query(User).order_by(User.points.desc()).first()
        
        stats_text = (
            f"{EMOJI['stats']} <b>СТАТИСТИКА БОТА</b> {EMOJI['stats']}\n\n"
            f"{EMOJI['profile']} <b>Користувачів:</b> {total_users}\n"
            f"{EMOJI['brain']}{EMOJI['laugh']} <b>Контенту:</b> {total_content}\n"
            f"{EMOJI['vs']} <b>Дуелей:</b> {total_duels}\n\n"
        )
        
        if top_user:
            stats_text += (
                f"{EMOJI['crown']} <b>Лідер:</b> {top_user.first_name or 'Невідомий'}\n"
                f"{EMOJI['fire']} <b>Балів:</b> {top_user.points}\n"
                f"{EMOJI['star']} <b>Ранг:</b> {top_user.rank}"
            )
        
        await message.answer(stats_text)

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_get_meme(callback_query):
    """Callback для отримання мему"""
    from handlers.content_handlers import send_meme
    await send_meme(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_get_joke(callback_query):
    """Callback для отримання анекдоту"""
    from handlers.content_handlers import send_joke
    await send_joke(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_show_profile(callback_query):
    """Callback для показу профілю"""
    from handlers.gamification_handlers import show_profile
    await show_profile(callback_query.message, callback_query.from_user.id)
    await callback_query.answer()

async def callback_show_leaderboard(callback_query):
    """Callback для показу таблиці лідерів"""
    from handlers.gamification_handlers import show_leaderboard
    await show_leaderboard(callback_query.message)
    await callback_query.answer()

async def callback_toggle_daily(callback_query):
    """Callback для перемикання щоденної розсилки"""
    from handlers.gamification_handlers import toggle_daily_subscription
    await toggle_daily_subscription(callback_query.message, callback_query.from_user.id)
    await callback_query.answer()

async def callback_submit_content(callback_query):
    """Callback для початку подачі контенту"""
    await callback_query.message.answer(
        f"{EMOJI['fire']} <b>Як надіслати свій контент:</b>\n\n"
        f"{EMOJI['brain']} Для анекдоту - напиши /submit і одразу текст анекдоту\n"
        f"{EMOJI['laugh']} Для мему - надішли /submit і прикріпи картинку з підписом\n\n"
        f"{EMOJI['star']} <b>Приклад:</b>\n"
        f"<code>/submit Чому програмісти п'ють каву? Бо без неї код не компілюється! {EMOJI['brain']}</code>"
    )
    await callback_query.answer()

def register_basic_handlers(dp: Dispatcher):
    """Реєстрація основних хендлерів"""
    
    # Команди
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_stats, Command("stats"))
    
    # Callback запити
    dp.callback_query.register(callback_get_meme, F.data == "get_meme")
    dp.callback_query.register(callback_get_joke, F.data == "get_joke")
    dp.callback_query.register(callback_show_profile, F.data == "show_profile")
    dp.callback_query.register(callback_show_leaderboard, F.data == "show_leaderboard")
    dp.callback_query.register(callback_toggle_daily, F.data == "toggle_daily")
    dp.callback_query.register(callback_submit_content, F.data == "submit_content")