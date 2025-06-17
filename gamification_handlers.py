#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери гейміфікації 🧠😂🔥
"""

import logging
from datetime import datetime, timedelta

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from settings import settings, EMOJI

logger = logging.getLogger(__name__)

# Тимчасова база користувачів (поки БД не налаштована)
USERS_DB = {}

def get_or_create_user(user_id: int, username: str = None, first_name: str = None):
    """Отримання або створення користувача"""
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'points': 0,
            'rank': settings.RANKS[0],
            'jokes_submitted': 0,
            'jokes_approved': 0,
            'memes_submitted': 0,
            'memes_approved': 0,
            'reactions_given': 0,
            'duels_won': 0,
            'duels_lost': 0,
            'daily_subscription': False,
            'created_at': datetime.now(),
            'last_active': datetime.now()
        }
    else:
        # Оновлення інформації
        USERS_DB[user_id]['username'] = username
        USERS_DB[user_id]['first_name'] = first_name
        USERS_DB[user_id]['last_active'] = datetime.now()
    
    return USERS_DB[user_id]

def update_user_points(user_id: int, points: int, reason: str = ""):
    """Оновлення балів користувача"""
    user = get_or_create_user(user_id)
    old_points = user['points']
    user['points'] += points
    
    # Оновлення рангу
    new_rank = get_rank_by_points(user['points'])
    old_rank = user['rank']
    user['rank'] = new_rank
    
    # Логування
    logger.info(f"😂 Користувач {user_id} отримав {points} балів за: {reason}")
    
    # Повертаємо інформацію про зміну рангу
    rank_changed = old_rank != new_rank
    return {
        'points_added': points,
        'total_points': user['points'],
        'old_rank': old_rank,
        'new_rank': new_rank,
        'rank_changed': rank_changed
    }

def get_rank_by_points(points: int) -> str:
    """Визначення рангу по балах"""
    for min_points in sorted(settings.RANKS.keys(), reverse=True):
        if points >= min_points:
            return settings.RANKS[min_points]
    return settings.RANKS[0]

def get_leaderboard(limit: int = 10):
    """Отримання таблиці лідерів"""
    users_list = list(USERS_DB.values())
    users_list.sort(key=lambda x: x['points'], reverse=True)
    return users_list[:limit]

async def cmd_profile(message: Message):
    """Команда /profile"""
    await show_profile(message, message.from_user.id)

async def show_profile(message: Message, user_id: int):
    """Показ профілю користувача"""
    user = get_or_create_user(
        user_id, 
        message.from_user.username, 
        message.from_user.first_name
    )
    
    # Прогрес до наступного рангу
    current_points = user['points']
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
    days_registered = (datetime.now() - user['created_at']).days + 1
    avg_points_per_day = round(user['points'] / days_registered, 1)
    
    # Позиція в рейтингу
    all_users = list(USERS_DB.values())
    all_users.sort(key=lambda x: x['points'], reverse=True)
    user_position = next((i for i, u in enumerate(all_users, 1) if u['id'] == user_id), 1)
    
    profile_text = (
        f"{EMOJI['profile']} <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
        f"{EMOJI['star']} <b>Ім'я:</b> {user['first_name'] or 'Невідомий'}\n"
        f"{EMOJI['crown']} <b>Ранг:</b> {user['rank']}\n"
        f"{EMOJI['fire']} <b>Балів:</b> {user['points']}{progress_text}\n"
        f"{EMOJI['trophy']} <b>Позиція:</b> #{user_position} з {len(all_users)}\n\n"
        
        f"{EMOJI['brain']} <b>СТАТИСТИКА КОНТЕНТУ:</b>\n"
        f"• Анекдотів надіслано: {user['jokes_submitted']}\n"
        f"• Анекдотів схвалено: {user['jokes_approved']}\n"
        f"• Мемів надіслано: {user['memes_submitted']}\n"
        f"• Мемів схвалено: {user['memes_approved']}\n"
        f"• Реакцій дано: {user['reactions_given']}\n\n"
        
        f"{EMOJI['vs']} <b>ДУЕЛІ:</b>\n"
        f"• Перемог: {user['duels_won']}\n"
        f"• Поразок: {user['duels_lost']}\n"
        f"• Співвідношення: {round(user['duels_won'] / max(user['duels_lost'], 1), 2)}\n\n"
        
        f"{EMOJI['calendar']} <b>АКТИВНІСТЬ:</b>\n"
        f"• Днів в боті: {days_registered}\n"
        f"• Середньо балів/день: {avg_points_per_day}\n"
        f"• Щоденна розсилка: {'✅ Увімкнена' if user['daily_subscription'] else '❌ Вимкнена'}\n"
        f"• Остання активність: {user['last_active'].strftime('%d.%m.%Y %H:%M')}"
    )
    
    # Клавіатура дій
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['calendar']} {'Вимкнути' if user['daily_subscription'] else 'Увімкнути'} розсилку",
                callback_data="toggle_daily"
            )
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['top']} ТОП користувачів", callback_data="show_leaderboard"),
            InlineKeyboardButton(text=f"{EMOJI['fire']} Як заробити бали", callback_data="earn_points_info")
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
    leaders = get_leaderboard(15)
    
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
        total_approved = user['jokes_approved'] + user['memes_approved']
        
        user_line = (
            f"{medal} <b>{user['first_name'] or 'Невідомий'}</b>\n"
            f"   {EMOJI['fire']} {user['points']} балів | {user['rank']}\n"
            f"   {EMOJI['check']} Схвалено: {total_approved} жартів\n"
        )
        
        leaderboard_text += user_line + "\n"
    
    # Позиція поточного користувача
    current_user_id = message.from_user.id
    current_user = get_or_create_user(
        current_user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    # Знаходимо позицію користувача
    all_users = list(USERS_DB.values())
    all_users.sort(key=lambda x: x['points'], reverse=True)
    user_position = next((i for i, u in enumerate(all_users, 1) if u['id'] == current_user_id), 1)
    
    leaderboard_text += (
        f"\n{EMOJI['profile']} <b>Твоя позиція:</b> #{user_position}\n"
        f"{EMOJI['fire']} {current_user['points']} балів | {current_user['rank']}"
    )
    
    # Клавіатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['fire']} Заробити бали", callback_data="earn_points_info")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke"),
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
        ]
    ])
    
    await message.answer(leaderboard_text, reply_markup=keyboard)
    logger.info(f"😂 Користувач {current_user_id} переглянув таблицю лідерів")

async def cmd_daily(message: Message):
    """Команда /daily"""
    await toggle_daily_subscription(message, message.from_user.id)

async def toggle_daily_subscription(message: Message, user_id: int):
    """Перемикання щоденної розсилки"""
    user = get_or_create_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    user['daily_subscription'] = not user['daily_subscription']
    
    if user['daily_subscription']:
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
    logger.info(f"📅 Користувач {user_id} {'увімкнув' if user['daily_subscription'] else 'вимкнув'} щоденну розсилку")

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_show_profile(callback_query: CallbackQuery):
    """Callback для показу профілю"""
    await show_profile(callback_query.message, callback_query.from_user.id)
    await callback_query.answer()

async def callback_show_leaderboard(callback_query: CallbackQuery):
    """Callback для показу таблиці лідерів"""
    await show_leaderboard(callback_query.message)
    await callback_query.answer()

async def callback_toggle_daily(callback_query: CallbackQuery):
    """Callback для перемикання щоденної розсилки"""
    await toggle_daily_subscription(callback_query.message, callback_query.from_user.id)
    await callback_query.answer()

async def callback_earn_points_info(callback_query: CallbackQuery):
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
        f"{EMOJI['crown']} <b>РАНГИ ЗА БАЛАМИ:</b>\n"
    )
    
    # Додаємо інформацію про ранги
    for points, rank in sorted(settings.RANKS.items()):
        info_text += f"• {points}+ балів - {rank}\n"
    
    info_text += f"\n{EMOJI['rocket']} <b>Будь активним і ставай легендою гумору!</b>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати жарт", callback_data="submit_content"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile")
        ]
    ])
    
    await callback_query.message.edit_text(info_text, reply_markup=keyboard)
    await callback_query.answer()

async def callback_get_content(callback_query: CallbackQuery):
    """Callback для отримання контенту"""
    # Імпортуємо функції з content_handlers
    try:
        if callback_query.data == "get_joke":
            from content_handlers import send_joke
            await send_joke(callback_query.message, from_callback=True)
        elif callback_query.data == "get_meme":
            from content_handlers import send_meme  
            await send_meme(callback_query.message, from_callback=True)
    except ImportError:
        await callback_query.message.answer(f"{EMOJI['cross']} Модуль контенту не доступний")
    
    await callback_query.answer()

async def callback_submit_content(callback_query: CallbackQuery):
    """Callback для початку подачі контенту"""
    await callback_query.message.answer(
        f"{EMOJI['fire']} <b>Як надіслати свій контент:</b>\n\n"
        f"{EMOJI['brain']} Для анекдоту - напиши /submit і одразу текст анекдоту\n"
        f"{EMOJI['laugh']} Для мему - надішли /submit і прикріпи картинку з підписом\n\n"
        f"{EMOJI['star']} <b>Приклад:</b>\n"
        f"<code>/submit Чому програмісти п'ють каву? Бо без неї код не компілюється! {EMOJI['brain']}</code>"
    )
    await callback_query.answer()

# ===== ФУНКЦІЇ ДЛЯ ІНТЕГРАЦІЇ З ІНШИМИ МОДУЛЯМИ =====

async def award_points_for_action(user_id: int, action: str, bot=None):
    """Нарахування балів за різні дії (для використання в інших модулях)"""
    points_map = {
        'view_content': 1,
        'like_content': settings.POINTS_FOR_REACTION,
        'dislike_content': 1,
        'submit_content': settings.POINTS_FOR_SUBMISSION,
        'approved_content': settings.POINTS_FOR_APPROVAL,
        'top_content': settings.POINTS_FOR_TOP_JOKE,
        'daily_activity': 2,
        'duel_win': 15,
        'duel_vote': 2
    }
    
    points = points_map.get(action, 0)
    if points > 0:
        result = update_user_points(user_id, points, action)
        
        # Повідомлення про зміну рангу
        if result['rank_changed'] and bot:
            try:
                user = USERS_DB.get(user_id)
                if user:
                    await bot.send_message(
                        user_id,
                        f"{EMOJI['party']} <b>ВІТАЮ! Новий ранг!</b>\n\n"
                        f"{EMOJI['crown']} <b>Твій новий ранг:</b> {result['new_rank']}\n"
                        f"{EMOJI['fire']} <b>Балів:</b> {result['total_points']}\n\n"
                        f"{EMOJI['rocket']} Продовжуй у тому ж дусі!"
                    )
            except Exception as e:
                logger.error(f"Помилка повідомлення про ранг: {e}")
        
        return result
    
    return None

def register_gamification_handlers(dp: Dispatcher):
    """Реєстрація хендлерів гейміфікації"""
    
    # Команди
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_top, Command("top"))
    dp.message.register(cmd_daily, Command("daily"))
    
    # Callback запити
    dp.callback_query.register(callback_show_profile, F.data == "show_profile")
    dp.callback_query.register(callback_show_leaderboard, F.data == "show_leaderboard")
    dp.callback_query.register(callback_toggle_daily, F.data == "toggle_daily")
    dp.callback_query.register(callback_earn_points_info, F.data == "earn_points_info")
    dp.callback_query.register(callback_submit_content, F.data == "submit_content")
    dp.callback_query.register(callback_get_content, F.data.in_(["get_joke", "get_meme"]))