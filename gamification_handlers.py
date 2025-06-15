#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери гейміфікації 🧠😂🔥
"""

import logging
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import EMOJI, settings
from database.database import get_user_stats, get_leaderboard, get_db_session
from database.models import User

logger = logging.getLogger(__name__)

async def cmd_profile(message: Message):
    """Команда /profile"""
    await show_profile(message, message.from_user.id)

async def show_profile(message: Message, user_id: int):
    """Показ профілю користувача"""
    stats = await get_user_stats(user_id)
    
    if not stats:
        await message.answer(f"{EMOJI['warning']} Користувач не знайдений!")
        return
    
    user = stats["user"]
    
    # Прогрес до наступного рангу
    current_points = user.points
    next_rank_points = None
    next_rank_name = None
    
    for points, rank in sorted(settings.RANKS.items()):
        if points > current_points:
            next_rank_points = points
            next_rank_name = rank
            break
    
    progress_text = ""
    if next_rank_points:
        needed_points = next_rank_points - current_points
        progress_text = f"\n{EMOJI['rocket']} До наступного рангу: {needed_points} балів ({next_rank_name})"
    else:
        progress_text = f"\n{EMOJI['crown']} Максимальний ранг досягнуто!"
    
    # Статистика активності
    days_registered = (datetime.utcnow() - user.created_at).days + 1
    avg_points_per_day = round(user.points / days_registered, 1)
    
    profile_text = (
        f"{EMOJI['profile']} <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
        f"{EMOJI['star']} <b>Ім'я:</b> {user.first_name or 'Невідомий'}\n"
        f"{EMOJI['crown']} <b>Ранг:</b> {user.rank}\n"
        f"{EMOJI['fire']} <b>Балів:</b> {user.points}{progress_text}\n\n"
        
        f"{EMOJI['brain']} <b>СТАТИСТИКА КОНТЕНТУ:</b>\n"
        f"• Анекдотів надіслано: {user.jokes_submitted}\n"
        f"• Анекдотів схвалено: {user.jokes_approved}\n"
        f"• Мемів надіслано: {user.memes_submitted}\n"
        f"• Мемів схвалено: {user.memes_approved}\n"
        f"• Успішність схвалення: {stats['approval_rate']}%\n\n"
        
        f"{EMOJI['vs']} <b>ДУЕЛІ:</b>\n"
        f"• Перемог: {user.duels_won}\n"
        f"• Поразок: {user.duels_lost}\n"
        f"• Співвідношення: {round(user.duels_won / max(user.duels_lost, 1), 2)}\n\n"
        
        f"{EMOJI['calendar']} <b>АКТИВНІСТЬ:</b>\n"
        f"• Днів в боті: {days_registered}\n"
        f"• Середньо балів/день: {avg_points_per_day}\n"
        f"• Реакцій дано: {user.reactions_given}\n"
        f"• Щоденна розсилка: {'✅ Увімкнена' if user.daily_subscription else '❌ Вимкнена'}\n"
        f"• Остання активність: {user.last_active.strftime('%d.%m.%Y %H:%M')}"
    )
    
    # Клавіатура дій
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['calendar']} {'Вимкнути' if user.daily_subscription else 'Увімкнути'} розсилку",
                callback_data="toggle_daily"
            )
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['top']} ТОП користувачів", callback_data="show_leaderboard"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke"),
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
        ]
    ])
    
    await message.answer(profile_text, reply_markup=keyboard)
    logger.info(f"🔥 Користувач {user_id} переглянув профіль")

async def cmd_top(message: Message):
    """Команда /top"""
    await show_leaderboard(message)

async def show_leaderboard(message: Message):
    """Показ таблиці лідерів"""
    leaders = await get_leaderboard(15)
    
    if not leaders:
        await message.answer(f"{EMOJI['thinking']} Поки що немає лідерів!")
        return
    
    leaderboard_text = f"{EMOJI['trophy']} <b>ТОП ГУМОРИСТІВ</b> {EMOJI['trophy']}\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, user in enumerate(leaders, 1):
        if i <= 3:
            medal = medals[i-1]
        elif i <= 10:
            medal = f"{EMOJI['star']}"
        else:
            medal = f"{i}."
        
        # Статистика користувача
        total_approved = user.jokes_approved + user.memes_approved
        
        user_line = (
            f"{medal} <b>{user.first_name or 'Невідомий'}</b>\n"
            f"   {EMOJI['fire']} {user.points} балів | {user.rank}\n"
            f"   {EMOJI['check']} Схвалено: {total_approved} жартів\n"
        )
        
        leaderboard_text += user_line + "\n"
    
    # Позиція поточного користувача
    current_user_id = message.from_user.id
    with get_db_session() as session:
        current_user = session.query(User).filter(User.id == current_user_id).first()
        
        if current_user:
            # Знаходимо позицію користувача
            better_users = session.query(User).filter(User.points > current_user.points).count()
            user_position = better_users + 1
            
            leaderboard_text += (
                f"\n{EMOJI['profile']} <b>Твоя позиція:</b> #{user_position}\n"
                f"{EMOJI['fire']} {current_user.points} балів | {current_user.rank}"
            )
    
    # Клавіатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['fire']} Заробити бали", callback_data="earn_points_info")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel")
        ]
    ])
    
    await message.answer(leaderboard_text, reply_markup=keyboard)
    logger.info(f"😂 Користувач {current_user_id} переглянув таблицю лідерів")

async def cmd_daily(message: Message):
    """Команда /daily"""
    await toggle_daily_subscription(message, message.from_user.id)

async def toggle_daily_subscription(message: Message, user_id: int):
    """Перемикання щоденної розсилки"""
    with get_db_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        
        if user:
            user.daily_subscription = not user.daily_subscription
            session.commit()
            
            if user.daily_subscription:
                response_text = (
                    f"{EMOJI['check']} <b>Щоденну розсилку увімкнено!</b>\n\n"
                    f"{EMOJI['calendar']} Щодня о {settings.DAILY_BROADCAST_HOUR}:00 ти отримуватимеш:\n"
                    f"{EMOJI['brain']} Найкращий анекдот дня\n"
                    f"{EMOJI['laugh']} Топовий мем\n"
                    f"{EMOJI['fire']} Мотиваційне повідомлення\n\n"
                    f"{EMOJI['star']} За щоденну активність: +2 бали!"
                )
            else:
                response_text = (
                    f"{EMOJI['cross']} <b>Щоденну розсилку вимкнено</b>\n\n"
                    f"{EMOJI['thinking']} Ти завжди можеш увімкнути її знову через /daily"
                )
            
            await message.answer(response_text)
            logger.info(f"📅 Користувач {user_id} {'увімкнув' if user.daily_subscription else 'вимкнув'} щоденну розсилку")

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_earn_points_info(callback_query):
    """Інформація про способи заробітку балів"""
    info_text = (
        f"{EMOJI['fire']} <b>ЯК ЗАРОБИТИ БАЛИ:</b>\n\n"
        f"{EMOJI['like']} <b>+{settings.POINTS_FOR_REACTION} балів</b> - за реакцію на контент\n"
        f"{EMOJI['brain']} <b>+{settings.POINTS_FOR_SUBMISSION} балів</b> - за надісланий жарт\n"
        f"{EMOJI['check']} <b>+{settings.POINTS_FOR_APPROVAL} балів</b> - якщо жарт схвалено\n"
        f"{EMOJI['trophy']} <b>+{settings.POINTS_FOR_TOP_JOKE} балів</b> - якщо жарт у ТОПі\n"
        f"{EMOJI['vs']} <b>+15 балів</b> - за перемогу в дуелі\n"
        f"{EMOJI['calendar']} <b>+2 бали</b> - за щоденну активність\n"
        f"{EMOJI['star']} <b>+1 бал</b> - за перегляд контенту\n\n"
        f"{EMOJI['rocket']} <b>Будь активним і ставай легендою гумору!</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати жарт", callback_data="submit_content"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel")
        ]
    ])
    
    await callback_query.message.answer(info_text, reply_markup=keyboard)
    await callback_query.answer()

async def callback_start_duel(callback_query):
    """Початок дуелі"""
    await callback_query.message.answer(
        f"{EMOJI['vs']} <b>Дуель жартів!</b>\n\n"
        f"{EMOJI['fire']} Щоб почати дуель, використай команду:\n"
        f"<code>/duel</code>\n\n"
        f"{EMOJI['brain']} Як це працює:\n"
        f"1. Ти надсилаєш свій жарт\n"
        f"2. Бот знаходить опонента\n"
        f"3. Інші користувачі голосують\n"
        f"4. Переможець отримує +15 балів!"
    )
    await callback_query.answer()

def register_gamification_handlers(dp: Dispatcher):
    """Реєстрація хендлерів гейміфікації"""
    
    # Команди
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_top, Command("top"))
    dp.message.register(cmd_daily, Command("daily"))
    
    # Callback запити
    dp.callback_query.register(callback_earn_points_info, F.data == "earn_points_info")
    dp.callback_query.register(callback_start_duel, F.data == "start_duel")