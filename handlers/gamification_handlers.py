#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери гейміфікації (профілі, бали, ранги) 🧠😂🔥
"""

import logging
from datetime import datetime, timedelta

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)

# Fallback імпорти
try:
    from config.settings import Settings
    settings = Settings()
except ImportError:
    import os
    class FallbackSettings:
        POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
        DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
    settings = FallbackSettings()

# EMOJI константи
EMOJI = {
    "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", 
    "heart": "❤️", "trophy": "🏆", "crown": "👑", "rocket": "🚀",
    "party": "🎉", "profile": "👤", "top": "🔝", "calendar": "📅",
    "stats": "📊", "check": "✅", "thinking": "🤔", "vs": "⚔️"
}

# Система рангів
RANKS = {
    0: "🤡 Новачок",
    50: "😄 Сміхун", 
    150: "😂 Гуморист",
    350: "🎭 Комік",
    750: "👑 Мастер Рофлу",
    1500: "🏆 Король Гумору",
    3000: "🌟 Легенда Мемів",
    5000: "🚀 Гумористичний Геній"
}

def get_rank_by_points(points: int) -> str:
    """Визначення рангу по балах"""
    for min_points in sorted(RANKS.keys(), reverse=True):
        if points >= min_points:
            return RANKS[min_points]
    return RANKS[0]

def get_next_rank_info(points: int) -> dict:
    """Інформація про наступний ранг"""
    current_rank = get_rank_by_points(points)
    
    for min_points in sorted(RANKS.keys()):
        if min_points > points:
            return {
                "next_rank": RANKS[min_points],
                "points_needed": min_points - points,
                "current_points": points
            }
    
    return {
        "next_rank": None,
        "points_needed": 0,
        "current_points": points
    }

# Простий клас користувача (fallback)
class User:
    def __init__(self, user_id, first_name=None, username=None):
        self.id = user_id
        self.first_name = first_name or "Користувач"
        self.username = username
        self.points = 0
        self.rank = get_rank_by_points(0)
        self.daily_subscription = False
        self.jokes_submitted = 0
        self.jokes_approved = 0
        self.memes_submitted = 0
        self.memes_approved = 0
        self.duels_won = 0
        self.duels_lost = 0
        self.last_active = datetime.now()

# Тимчасове сховище користувачів (в продакшені - БД)
USERS_STORAGE = {}

async def get_or_create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Отримання або створення користувача"""
    try:
        # Спроба отримання з БД
        from database.database import get_or_create_user as db_get_user
        return await db_get_user(user_id, username, first_name, last_name)
    except ImportError:
        # Fallback - використовуємо пам'ять
        if user_id not in USERS_STORAGE:
            USERS_STORAGE[user_id] = User(user_id, first_name, username)
        return USERS_STORAGE[user_id]

async def get_user_stats(user_id: int):
    """Отримання статистики користувача"""
    try:
        # Спроба отримання з БД
        from database.database import get_user_stats as db_get_stats
        return await db_get_stats(user_id)
    except ImportError:
        # Fallback
        user = await get_or_create_user(user_id)
        return {"user": user}

async def get_top_users(limit: int = 10):
    """Отримання топ-користувачів"""
    try:
        # Спроба отримання з БД
        from database.database import get_db_session
        from database.models import User as DBUser
        
        with get_db_session() as session:
            return session.query(DBUser).order_by(DBUser.points.desc()).limit(limit).all()
    except ImportError:
        # Fallback - сортування з пам'яті
        sorted_users = sorted(USERS_STORAGE.values(), key=lambda u: u.points, reverse=True)
        return sorted_users[:limit]

async def toggle_daily_subscription_db(user_id: int):
    """Перемикання підписки на щоденну розсилку"""
    try:
        from database.database import get_db_session
        from database.models import User as DBUser
        
        with get_db_session() as session:
            user = session.query(DBUser).filter(DBUser.id == user_id).first()
            if user:
                user.daily_subscription = not user.daily_subscription
                session.commit()
                return user.daily_subscription
    except ImportError:
        # Fallback
        user = await get_or_create_user(user_id)
        user.daily_subscription = not user.daily_subscription
        return user.daily_subscription
    
    return False

# ===== КОМАНДИ ГЕЙМІФІКАЦІЇ =====

async def cmd_profile(message: Message):
    """Команда /profile - показ профілю користувача"""
    await show_profile(message, message.from_user.id)

async def show_profile(message: Message, user_id: int):
    """Показ детального профілю користувача"""
    user_stats = await get_user_stats(user_id)
    user_data = user_stats.get("user") if user_stats else None
    
    if not user_data:
        await message.answer("❌ Користувач не знайдений!")
        return
    
    # Інформація про наступний ранг
    next_rank_info = get_next_rank_info(user_data.points)
    
    # Розрахунок прогресу
    if next_rank_info["points_needed"] > 0:
        progress_text = (
            f"{EMOJI['rocket']} <b>До наступного рангу:</b>\n"
            f"🎯 {next_rank_info['next_rank']}\n"
            f"🔥 Потрібно ще: {next_rank_info['points_needed']} балів"
        )
    else:
        progress_text = f"{EMOJI['crown']} <b>Максимальний ранг досягнуто!</b>"
    
    # Статистика активності
    activity_stats = ""
    if hasattr(user_data, 'jokes_submitted'):
        approval_rate_jokes = round(user_data.jokes_approved / max(user_data.jokes_submitted, 1) * 100)
        approval_rate_memes = round(user_data.memes_approved / max(user_data.memes_submitted, 1) * 100)
        
        activity_stats = (
            f"\n{EMOJI['stats']} <b>Активність:</b>\n"
            f"📝 Анекдотів: {user_data.jokes_submitted} (схвалено {approval_rate_jokes}%)\n"
            f"🖼 Мемів: {user_data.memes_submitted} (схвалено {approval_rate_memes}%)\n"
            f"⚔️ Дуелей: {user_data.duels_won}W/{user_data.duels_lost}L"
        )
    
    profile_text = (
        f"{EMOJI['profile']} <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
        f"👤 <b>Ім'я:</b> {user_data.first_name}\n"
        f"{EMOJI['fire']} <b>Балів:</b> {user_data.points}\n"
        f"{EMOJI['crown']} <b>Ранг:</b> {user_data.rank}\n\n"
        f"{progress_text}"
        f"{activity_stats}\n\n"
        f"{EMOJI['calendar']} Щоденна розсилка: {'✅ Увімкнена' if user_data.daily_subscription else '❌ Вимкнена'}"
    )
    
    # Клавіатура профілю
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['top']} Таблиця лідерів", callback_data="show_leaderboard"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel")
        ],
        [
            InlineKeyboardButton(
                text=f"{'❌ Відписатись' if user_data.daily_subscription else '✅ Підписатись'} на розсилку",
                callback_data="toggle_daily"
            )
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke"),
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
        ]
    ])
    
    await message.answer(profile_text, reply_markup=keyboard)

async def cmd_top(message: Message):
    """Команда /top - таблиця лідерів"""
    await show_leaderboard(message)

async def show_leaderboard(message: Message):
    """Показ таблиці лідерів"""
    top_users = await get_top_users(10)
    
    if not top_users:
        await message.answer("😔 Поки що немає користувачів в рейтингу!")
        return
    
    leaderboard_text = f"{EMOJI['trophy']} <b>ТАБЛИЦЯ ЛІДЕРІВ ТОП-10</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    
    for i, user in enumerate(top_users):
        medal = medals[i] if i < len(medals) else "🏅"
        
        # Маскування імені для анонімності 
        name = user.first_name or "Невідомий"
        if len(name) > 10:
            name = name[:8] + "..."
        
        leaderboard_text += (
            f"{medal} <b>{i+1}.</b> {name}\n"
            f"   {EMOJI['fire']} {user.points} балів | {user.rank}\n"
        )
        
        if i < 2:  # Додаткова інформація для топ-3
            if hasattr(user, 'duels_won'):
                leaderboard_text += f"   ⚔️ Дуелей виграно: {user.duels_won}\n"
        
        leaderboard_text += "\n"
    
    # Статистика користувача
    user_stats = await get_user_stats(message.from_user.id)
    user_data = user_stats.get("user") if user_stats else None
    
    if user_data and user_data.points > 0:
        # Знаходимо позицію користувача
        user_position = next((i+1 for i, u in enumerate(top_users) if u.id == user_data.id), "10+")
        
        leaderboard_text += (
            f"{EMOJI['star']} <b>Твоя позиція:</b>\n"
            f"🏅 #{user_position} | {user_data.points} балів | {user_data.rank}"
        )
    
    # Клавіатура дій
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Заробити бали", callback_data="earn_points_info"),
            InlineKeyboardButton(text=f"🔄 Оновити", callback_data="show_leaderboard")
        ]
    ])
    
    await message.answer(leaderboard_text, reply_markup=keyboard)

async def cmd_daily(message: Message):
    """Команда /daily - управління щоденною розсилкою"""
    await toggle_daily_subscription(message, message.from_user.id)

async def toggle_daily_subscription(message: Message, user_id: int):
    """Перемикання підписки на щоденну розсилку"""
    new_status = await toggle_daily_subscription_db(user_id)
    
    if new_status:
        response_text = (
            f"{EMOJI['check']} <b>Підписка активована!</b>\n\n"
            f"{EMOJI['calendar']} Тепер ти будеш отримувати:\n"
            f"• Щоденний мем о {settings.DAILY_BROADCAST_HOUR}:00\n"
            f"• Анекдот дня\n"
            f"• +{settings.POINTS_FOR_DAILY_ACTIVITY} балів за активність\n\n"
            f"{EMOJI['star']} Для скасування використай /daily знову"
        )
    else:
        response_text = (
            f"{EMOJI['calendar']} <b>Підписку скасовано</b>\n\n"
            f"😔 Ти більше не будеш отримувати щоденну розсилку\n\n"
            f"{EMOJI['thinking']} Для відновлення використай /daily знову"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
        ]
    ])
    
    await message.answer(response_text, reply_markup=keyboard)

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
    """Callback з інформацією про заробіток балів"""
    info_text = (
        f"{EMOJI['fire']} <b>ЯК ЗАРОБИТИ БАЛИ:</b>\n\n"
        f"{EMOJI['brain']} <b>+1 бал</b> - за перегляд мему/анекдоту\n"
        f"{EMOJI['heart']} <b>+5 балів</b> - за лайк контенту\n"
        f"{EMOJI['fire']} <b>+10 балів</b> - за надісланий жарт\n"
        f"{EMOJI['check']} <b>+20 балів</b> - якщо жарт схвалено\n"
        f"{EMOJI['trophy']} <b>+50 балів</b> - якщо жарт у ТОПі\n"
        f"{EMOJI['vs']} <b>+15 балів</b> - за перемогу в дуелі\n"
        f"{EMOJI['calendar']} <b>+2 бали</b> - за щоденну активність\n\n"
        f"{EMOJI['rocket']} <b>Ранги:</b>\n"
        f"🤡 Новачок (0+) → 😄 Сміхун (50+) → 😂 Гуморист (150+)\n"
        f"🎭 Комік (350+) → 👑 Мастер (750+) → 🏆 Король (1500+)\n"
        f"🌟 Легенда (3000+) → 🚀 Геній (5000+)\n\n"
        f"{EMOJI['party']} <b>Будь активним і ставай легендою гумору!</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати жарт", callback_data="submit_content"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile")
        ]
    ])
    
    await callback_query.message.answer(info_text, reply_markup=keyboard)
    await callback_query.answer()

async def callback_start_duel(callback_query: CallbackQuery):
    """Callback для початку дуелі"""
    await callback_query.message.answer(
        f"{EMOJI['vs']} <b>Дуель жартів!</b>\n\n"
        f"{EMOJI['fire']} Щоб почати дуель, використай команду:\n"
        f"<code>/duel</code>\n\n"
        f"{EMOJI['brain']} Як це працює:\n"
        f"1. Ти надсилаєш свій жарт\n"
        f"2. Бот знаходить опонента\n" 
        f"3. Інші користувачі голосують\n"
        f"4. Переможець отримує +15 балів!\n\n"
        f"{EMOJI['thinking']} <b>Готовий до батлу?</b>"
    )
    await callback_query.answer()

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
    dp.callback_query.register(callback_start_duel, F.data == "start_duel")
    
    logger.info("✅ Gamification handlers зареєстровані")