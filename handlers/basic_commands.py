#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Основні команди бота з інтеграцією гейміфікації 🧠😂🔥
"""

import logging
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

# Fallback імпорти
try:
    from config.settings import Settings
    settings = Settings()
    
    if not hasattr(settings, 'POINTS_FOR_SUBMISSION'):
        settings.POINTS_FOR_SUBMISSION = 10
    if not hasattr(settings, 'POINTS_FOR_DUEL_WIN'):
        settings.POINTS_FOR_DUEL_WIN = 15
        
except ImportError:
    import os
    class FallbackSettings:
        POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
        POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    settings = FallbackSettings()

# EMOJI константи
EMOJI = {
    "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", 
    "heart": "❤️", "trophy": "🏆", "crown": "👑", "rocket": "🚀",
    "party": "🎉", "profile": "👤", "top": "🔝", "calendar": "📅",
    "stats": "📊", "check": "✅", "vs": "⚔️", "help": "❓",
    "thinking": "🤔", "info": "ℹ️", "warning": "⚠️"
}

async def get_or_create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Отримання або створення користувача"""
    try:
        # Спроба отримання з БД
        from handlers.gamification_handlers import get_or_create_user as db_get_user
        return await db_get_user(user_id, username, first_name, last_name)
    except ImportError:
        # Fallback - логування
        logger.info(f"👤 Користувач {first_name} (ID:{user_id}) використовує бота")

async def get_user_stats(user_id: int):
    """Отримання статистики користувача"""
    try:
        from handlers.gamification_handlers import get_user_stats as db_get_stats
        return await db_get_stats(user_id)
    except ImportError:
        return None

async def cmd_start(message: Message):
    """Обробка команди /start з створенням профілю"""
    user = message.from_user
    
    # Створення або оновлення користувача
    await get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Отримання статистики користувача
    user_stats = await get_user_stats(user.id)
    user_data = user_stats.get("user") if user_stats else None
    
    # Персоналізоване привітання
    if user_data and hasattr(user_data, 'points') and user_data.points > 0:
        greeting_extra = (
            f"\n\n{EMOJI['star']} <b>Твій прогрес:</b>\n"
            f"{EMOJI['fire']} Балів: {user_data.points}\n"
            f"{EMOJI['crown']} Ранг: {user_data.rank}"
        )
    else:
        greeting_extra = f"\n\n{EMOJI['party']} <b>Вперше тут? Отримуй бали за активність і ставай легендою гумору!</b>"
    
    # Контекстне привітання за часом
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        time_greeting = f"{EMOJI['fire']} Доброго ранку!"
    elif 12 <= current_hour < 18:
        time_greeting = f"{EMOJI['laugh']} Гарного дня!"
    elif 18 <= current_hour < 23:
        time_greeting = f"{EMOJI['star']} Доброго вечора!"
    else:
        time_greeting = f"{EMOJI['thinking']} Доброї ночі!"
    
    # Клавіатура швидких дій з акцентом на бали
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем (+1 бал)", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот (+1 бал)", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI['fire']} Надіслати жарт (+{settings.POINTS_FOR_SUBMISSION})", 
                callback_data="submit_content"
            )
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['top']} ТОП користувачів", callback_data="show_leaderboard")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['calendar']} Щоденна розсилка", callback_data="toggle_daily"),
            InlineKeyboardButton(text=f"{EMOJI['vs']} Дуель жартів", callback_data="start_duel")
        ]
    ])
    
    start_text = (
        f"{time_greeting}\n\n"
        f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті мемів та анекдотів!</b>\n\n"
        f"{EMOJI['star']} <b>Що я вмію:</b>\n"
        f"{EMOJI['laugh']} /meme - випадковий мем (+1 бал)\n"
        f"{EMOJI['brain']} /anekdot - український анекдот (+1 бал)\n"
        f"{EMOJI['fire']} /submit - надіслати свій жарт (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
        f"{EMOJI['calendar']} /daily - щоденна розсилка (+2 бали)\n"
        f"{EMOJI['profile']} /profile - твій профіль та бали\n"
        f"{EMOJI['top']} /top - таблиця лідерів\n"
        f"{EMOJI['vs']} /duel - дуель жартів (+{settings.POINTS_FOR_DUEL_WIN} за перемогу)\n"
        f"{EMOJI['help']} /help - допомога\n"
        f"{greeting_extra}"
    )
    
    await message.answer(start_text, reply_markup=keyboard)
    
    logger.info(f"🧠 Користувач {user.id} ({user.first_name}) запустив бота")

async def cmd_help(message: Message):
    """Обробка команди /help з інформацією про бали"""
    user = message.from_user
    
    # Клавіатура з корисними посиланнями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Спробувати мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Спробувати анекдот", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Почати заробляти бали", callback_data="submit_content")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['top']} Таблиця лідерів", callback_data="show_leaderboard")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['info']} Як заробити бали?", callback_data="earn_points_info")
        ]
    ])
    
    help_text = (
        f"{EMOJI['help']} <b>ДОВІДКА ПО БОТУ</b> {EMOJI['help']}\n\n"
        f"{EMOJI['brain']} <b>ОСНОВНІ КОМАНДИ:</b>\n"
        f"• /meme - отримати випадковий мем (+1 бал)\n"
        f"• /anekdot - отримати український анекдот (+1 бал)\n"
        f"• /submit - надіслати свій мем або анекдот (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
        f"• /daily - підписатися на щоденну розсилку (+2 бали)\n\n"
        f"{EMOJI['fire']} <b>ГЕЙМІФІКАЦІЯ:</b>\n"
        f"• /profile - переглянути свій профіль та бали\n"
        f"• /top - таблиця лідерів з топ-10\n"
        f"• /duel - започаткувати дуель жартів\n\n"
        f"{EMOJI['star']} <b>СИСТЕМА БАЛІВ:</b>\n"
        f"• +1 бал - за перегляд контенту\n"
        f"• +5 балів - за лайк мему/анекдоту\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів - за надісланий жарт\n"
        f"• +20 балів - якщо жарт схвалено\n"
        f"• +50 балів - якщо жарт потрапив до ТОПу\n"
        f"• +{settings.POINTS_FOR_DUEL_WIN} балів - за перемогу в дуелі\n\n"
        f"{EMOJI['crown']} <b>РАНГИ:</b>\n"
        f"🤡 Новачок → 😄 Сміхун → 😂 Гуморист → 🎭 Комік\n"
        f"👑 Мастер Рофлу → 🏆 Король Гумору → 🌟 Легенда Мемів → 🚀 Геній\n\n"
        f"{EMOJI['rocket']} <b>Дякуємо за використання бота!</b>"
    )
    
    await message.answer(help_text, reply_markup=keyboard)
    
    logger.info(f"😂 Користувач {user.id} подивився довідку")

async def cmd_stats(message: Message):
    """Обробка команди /stats - загальна статистика бота"""
    try:
        # Спроба отримання статистики з БД
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
                    f"{EMOJI['crown']} <b>Лідер гумору:</b>\n"
                    f"👤 {top_user.first_name or 'Невідомий'}\n"
                    f"{EMOJI['fire']} Балів: {top_user.points}\n"
                    f"{EMOJI['star']} Ранг: {top_user.rank}\n\n"
                    f"{EMOJI['thinking']} <b>Хочеш потрапити до топу?</b>\n"
                    f"Надсилай жарти та будь активним!"
                )
            
    except ImportError:
        # Fallback статистика
        stats_text = (
            f"{EMOJI['stats']} <b>СТАТИСТИКА БОТА</b> {EMOJI['stats']}\n\n"
            f"{EMOJI['profile']} Бот працює в fallback режимі\n"
            f"{EMOJI['brain']} Базові функції доступні\n"
            f"{EMOJI['fire']} Додай повну БД для детальної статистики\n\n"
            f"{EMOJI['thinking']} <b>Спробуй:</b>\n"
            f"• /meme - отримати мем\n"
            f"• /profile - свій профіль\n"
            f"• /duel - почати дуель"
        )
    
    # Клавіатура для швидких дій
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Мій профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['top']} Повний ТОП", callback_data="show_leaderboard")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['vs']} Почати дуель", callback_data="start_duel"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Отримати мем", callback_data="get_meme")
        ]
    ])
    
    await message.answer(stats_text, reply_markup=keyboard)

async def cmd_info(message: Message):
    """Команда /info - інформація про бота"""
    info_text = (
        f"{EMOJI['info']} <b>ПРО БОТА</b>\n\n"
        f"{EMOJI['brain']} <b>Україномовний бот мемів та анекдотів</b>\n\n"
        f"{EMOJI['star']} <b>Особливості:</b>\n"
        f"🎮 Повна гейміфікація з балами та рангами\n"
        f"⚔️ Дуелі жартів з голосуванням\n"
        f"🛡️ Модерація контенту від користувачів\n"
        f"📅 Щоденна автоматична розсилка\n"
        f"🤖 AI підтримка для генерації контенту\n\n"
        f"{EMOJI['fire']} <b>Технології:</b>\n"
        f"• Python 3.9+ + aiogram 3.4+\n"
        f"• PostgreSQL + SQLAlchemy\n"
        f"• Railway для хостингу\n"
        f"• OpenAI API для AI\n\n"
        f"{EMOJI['heart']} <b>Зроблено з любов'ю для української спільноти!</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Спробувати мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['profile']} Мій профіль", callback_data="show_profile")
        ]
    ])
    
    await message.answer(info_text, reply_markup=keyboard)

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_get_meme(callback_query):
    """Callback для отримання мему"""
    try:
        from handlers.content_handlers import send_meme
        await send_meme(callback_query.message, from_callback=True)
    except ImportError:
        await callback_query.message.answer("😅 Меми поки не доступні. Спробуй пізніше!")
    await callback_query.answer()

async def callback_get_joke(callback_query):
    """Callback для отримання анекдоту"""
    try:
        from handlers.content_handlers import send_joke
        await send_joke(callback_query.message, from_callback=True)
    except ImportError:
        await callback_query.message.answer("😅 Анекдоти поки не доступні. Спробуй пізніше!")
    await callback_query.answer()

async def callback_show_profile(callback_query):
    """Callback для показу профілю"""
    try:
        from handlers.gamification_handlers import show_profile
        await show_profile(callback_query.message, callback_query.from_user.id)
    except ImportError:
        await callback_query.message.answer("😅 Профілі поки не доступні. Спробуй пізніше!")
    await callback_query.answer()

async def callback_show_leaderboard(callback_query):
    """Callback для показу таблиці лідерів"""
    try:
        from handlers.gamification_handlers import show_leaderboard
        await show_leaderboard(callback_query.message)
    except ImportError:
        await callback_query.message.answer("😅 Таблиця лідерів поки не доступна. Спробуй пізніше!")
    await callback_query.answer()

async def callback_toggle_daily(callback_query):
    """Callback для перемикання щоденної розсилки"""
    try:
        from handlers.gamification_handlers import toggle_daily_subscription
        await toggle_daily_subscription(callback_query.message, callback_query.from_user.id)
    except ImportError:
        await callback_query.message.answer("😅 Щоденна розсилка поки не доступна. Спробуй пізніше!")
    await callback_query.answer()

async def callback_start_duel(callback_query):
    """Callback для початку дуелі"""
    await callback_query.message.answer(
        f"{EMOJI['vs']} <b>Дуель жартів!</b>\n\n"
        f"{EMOJI['fire']} Щоб почати дуель, використай команду:\n"
        f"<code>/duel</code>\n\n"
        f"{EMOJI['brain']} Як це працює:\n"
        f"1. Ти надсилаєш свій жарт\n"
        f"2. Бот знаходить опонента\n"
        f"3. Інші користувачі голосують\n"
        f"4. Переможець отримує +{settings.POINTS_FOR_DUEL_WIN} балів!\n\n"
        f"{EMOJI['thinking']} <b>Готовий до батлу?</b>"
    )
    await callback_query.answer()

async def callback_submit_content(callback_query):
    """Callback для початку подачі контенту з інформацією про бали"""
    await callback_query.message.answer(
        f"{EMOJI['fire']} <b>Як надіслати свій контент:</b>\n\n"
        f"{EMOJI['brain']} <b>Для анекдоту:</b>\n"
        f"Напиши /submit і одразу текст анекдоту\n\n"
        f"{EMOJI['laugh']} <b>Для мему:</b>\n"
        f"Надішли /submit і прикріпи картинку з підписом\n\n"
        f"{EMOJI['star']} <b>Нагороди:</b>\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів за подачу\n"
        f"• +20 балів при схваленні\n"
        f"• +50 балів якщо потрапиш до ТОПу!\n\n"
        f"{EMOJI['thinking']} <b>Приклад:</b>\n"
        f"<code>/submit Чому програмісти п'ють каву? Бо без неї код не компілюється! {EMOJI['brain']}</code>"
    )
    await callback_query.answer()

async def callback_earn_points_info(callback_query):
    """Callback з інформацією про заробіток балів"""
    info_text = (
        f"{EMOJI['fire']} <b>ЯК ЗАРОБИТИ БАЛИ:</b>\n\n"
        f"{EMOJI['brain']} <b>+1 бал</b> - за перегляд мему/анекдоту\n"
        f"{EMOJI['heart']} <b>+5 балів</b> - за лайк контенту\n"
        f"{EMOJI['fire']} <b>+{settings.POINTS_FOR_SUBMISSION} балів</b> - за надісланий жарт\n"
        f"{EMOJI['check']} <b>+20 балів</b> - якщо жарт схвалено\n"
        f"{EMOJI['trophy']} <b>+50 балів</b> - якщо жарт у ТОПі\n"
        f"{EMOJI['vs']} <b>+{settings.POINTS_FOR_DUEL_WIN} балів</b> - за перемогу в дуелі\n"
        f"{EMOJI['calendar']} <b>+2 бали</b> - за щоденну активність\n\n"
        f"{EMOJI['rocket']} <b>Ранги залежать від балів:</b>\n"
        f"🤡 Новачок (0+) → 😄 Сміхун (50+) → 😂 Гуморист (150+)\n"
        f"🎭 Комік (350+) → 👑 Мастер Рофлу (750+) → 🏆 Король Гумору (1500+)\n"
        f"🌟 Легенда Мемів (3000+) → 🚀 Гумористичний Геній (5000+)\n\n"
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

def register_basic_handlers(dp: Dispatcher):
    """Реєстрація основних хендлерів"""
    
    # Команди
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_stats, Command("stats"))
    dp.message.register(cmd_info, Command("info"))
    
    # Callback запити
    dp.callback_query.register(callback_get_meme, F.data == "get_meme")
    dp.callback_query.register(callback_get_joke, F.data == "get_joke")
    dp.callback_query.register(callback_show_profile, F.data == "show_profile")
    dp.callback_query.register(callback_show_leaderboard, F.data == "show_leaderboard")
    dp.callback_query.register(callback_toggle_daily, F.data == "toggle_daily")
    dp.callback_query.register(callback_start_duel, F.data == "start_duel")
    dp.callback_query.register(callback_submit_content, F.data == "submit_content")
    dp.callback_query.register(callback_earn_points_info, F.data == "earn_points_info")
    
    logger.info("✅ Basic handlers зареєстровані")