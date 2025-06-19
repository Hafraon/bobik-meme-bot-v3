#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ОСНОВНІ КОМАНДИ БОТА З ПОВНОЮ ІНТЕГРАЦІЄЮ 🧠😂🔥
"""

import logging
from datetime import datetime
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)

# Fallback налаштування
try:
    from config.settings import settings, EMOJI, TEXTS
    POINTS_FOR_VIEW = getattr(settings, 'POINTS_FOR_VIEW', 1)
    POINTS_FOR_DAILY_ACTIVITY = getattr(settings, 'POINTS_FOR_DAILY_ACTIVITY', 2)
except ImportError:
    import os
    POINTS_FOR_VIEW = int(os.getenv("POINTS_FOR_VIEW", "1"))
    POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
    
    EMOJI = {
        "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐",
        "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
        "crown": "👑", "rocket": "🚀", "vs": "⚔️", "calendar": "📅",
        "profile": "👤", "trophy": "🏆", "gem": "💎", "heart": "❤️"
    }
    
    TEXTS = {
        "welcome": "Ласкаво просимо до українського бота мемів та анекдотів!",
        "help": "Довідка з використання бота"
    }

# ===== ГОЛОВНА КОМАНДА /start =====

async def cmd_start(message: Message):
    """Команда /start з повною інтеграцією всіх функцій"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "друже"
    username = message.from_user.username
    
    # Створюємо/оновлюємо користувача в БД
    user = None
    try:
        from database import get_or_create_user
        user = await get_or_create_user(
            telegram_id=user_id,
            username=username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        if user:
            logger.info(f"✅ Користувач {user_id} ({first_name}) успішно створено/оновлено")
        else:
            logger.warning(f"⚠️ Не вдалося створити користувача {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Помилка створення користувача {user_id}: {e}")
    
    # Перевірити чи це адмін і показати адмін-меню
    admin_menu_shown = False
    try:
        from handlers.admin_panel_handlers import auto_show_admin_menu_on_start
        admin_menu_shown = await auto_show_admin_menu_on_start(message)
    except ImportError:
        logger.debug("⚠️ Адмін-панель не доступна")
    except Exception as e:
        logger.error(f"❌ Помилка адмін-панелі: {e}")
    
    # Отримати статистику користувача для персоналізованого привітання
    user_stats = await get_user_welcome_stats(user_id)
    
    # Створити персоналізоване привітання
    welcome_text = await create_personalized_welcome(
        first_name, user_stats, admin_menu_shown
    )
    
    # Показати головне меню
    keyboard = get_main_menu_keyboard(user_stats)
    
    await message.answer(welcome_text, reply_markup=keyboard)
    
    # Нарахувати бали за щоденну активність (якщо перший раз сьогодні)
    await award_daily_activity_points(user_id)
    
    logger.info(f"🎉 Користувач {user_id} ({first_name}) запустив бота")

async def get_user_welcome_stats(user_id: int) -> dict:
    """Отримати статистику користувача для привітання"""
    try:
        from database import get_user_by_id
        
        user = await get_user_by_id(user_id)
        if user:
            return {
                "points": user.points,
                "rank": user.rank,
                "is_new_user": user.points == 0,
                "days_since_registration": (datetime.utcnow() - user.created_at).days,
                "total_content": user.jokes_approved + user.memes_approved,
                "duels_won": user.duels_won
            }
    except Exception as e:
        logger.debug(f"Не вдалося отримати статистику користувача: {e}")
    
    return {
        "points": 0,
        "rank": "🤡 Новачок",
        "is_new_user": True,
        "days_since_registration": 0,
        "total_content": 0,
        "duels_won": 0
    }

async def create_personalized_welcome(first_name: str, user_stats: dict, is_admin: bool) -> str:
    """Створити персоналізоване привітання"""
    # Контекстне привітання за часом дня
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        time_greeting = "Доброго ранку"
        time_emoji = "🌅"
    elif 12 <= current_hour < 18:
        time_greeting = "Гарного дня"
        time_emoji = "☀️"
    elif 18 <= current_hour < 23:
        time_greeting = "Доброго вечора"
        time_emoji = "🌆"
    else:
        time_greeting = "Доброї ночі"
        time_emoji = "🌙"
    
    # Основне привітання
    text = f"{time_emoji} <b>{time_greeting}, {first_name}!</b>\n\n"
    
    if is_admin:
        text += f"{EMOJI['crown']} Адмін-режим активовано!\n\n"
    
    # Персоналізація для нових користувачів
    if user_stats["is_new_user"]:
        text += f"{EMOJI['star']} Ласкаво просимо до найкращого українського бота мемів та анекдотів!\n\n"
        text += f"🎮 <b>Як це працює:</b>\n"
        text += f"• Дивіться меми та анекдоти (+{POINTS_FOR_VIEW} бал)\n"
        text += f"• Ставте лайки та дизлайки (+5 балів)\n"
        text += f"• Надсилайте свої жарти (+10 балів)\n"
        text += f"• Беріть участь в дуелях (+15 балів за перемогу)\n"
        text += f"• Підписуйтесь на щоденну розсилку (+{POINTS_FOR_DAILY_ACTIVITY} балів щодня)\n\n"
        text += f"🏆 Збирайте бали, підвищуйте ранг та ставайте легендою гумору!\n\n"
    else:
        # Персоналізація для постійних користувачів
        text += f"🎭 З поверненням! Ваш прогрес:\n"
        text += f"💰 Бали: {user_stats['points']:,}\n"
        text += f"🏆 Ранг: {user_stats['rank']}\n"
        
        if user_stats["total_content"] > 0:
            text += f"📝 Схвалено контенту: {user_stats['total_content']}\n"
        
        if user_stats["duels_won"] > 0:
            text += f"⚔️ Дуелів виграно: {user_stats['duels_won']}\n"
        
        text += f"📅 З нами: {user_stats['days_since_registration']} днів\n\n"
        
        # Мотиваційні повідомлення
        if user_stats["points"] < 50:
            text += f"🎯 Ще трохи до наступного рангу!\n"
        elif user_stats["points"] >= 1000:
            text += f"🌟 Ви справжня легенда гумору!\n"
        else:
            text += f"🔥 Продовжуйте в тому ж дусі!\n"
        
        text += "\n"
    
    text += f"Оберіть що вас цікавить: 👇"
    
    return text

def get_main_menu_keyboard(user_stats: dict) -> InlineKeyboardMarkup:
    """Головне меню з урахуванням статистики користувача"""
    keyboard = []
    
    # Перший рядок - основний контент
    keyboard.append([
        InlineKeyboardButton(
            text=f"{EMOJI['laugh']} Мем (+{POINTS_FOR_VIEW})",
            callback_data="get_meme"
        ),
        InlineKeyboardButton(
            text=f"{EMOJI['brain']} Анекдот (+{POINTS_FOR_VIEW})",
            callback_data="get_anekdot"
        )
    ])
    
    # Другий рядок - профіль та лідери
    keyboard.append([
        InlineKeyboardButton(
            text=f"{EMOJI['profile']} Профіль",
            callback_data="show_profile"
        ),
        InlineKeyboardButton(
            text=f"{EMOJI['trophy']} Лідери",
            callback_data="show_leaderboard"
        )
    ])
    
    # Третій рядок - інтерактив
    keyboard.append([
        InlineKeyboardButton(
            text=f"{EMOJI['fire']} Надіслати жарт (+10)",
            callback_data="submit_content"
        ),
        InlineKeyboardButton(
            text=f"{EMOJI['vs']} Дуель (+15)",
            callback_data="start_duel"
        )
    ])
    
    # Четвертий рядок - налаштування
    keyboard.append([
        InlineKeyboardButton(
            text=f"{EMOJI['calendar']} Щоденна розсилка (+{POINTS_FOR_DAILY_ACTIVITY})",
            callback_data="toggle_daily"
        ),
        InlineKeyboardButton(
            text=f"{EMOJI['info']} Допомога",
            callback_data="show_help"
        )
    ])
    
    # П'ятий рядок - додаткові функції для досвідчених користувачів
    if not user_stats["is_new_user"]:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{EMOJI['gem']} Досягнення",
                callback_data="show_achievements"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['rocket']} Статистика",
                callback_data="show_detailed_stats"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def award_daily_activity_points(user_id: int):
    """Нарахувати бали за щоденну активність"""
    try:
        from database import get_user_by_id, update_user_points
        
        user = await get_user_by_id(user_id)
        if user:
            # Перевірити чи це перший /start сьогодні
            today = datetime.utcnow().date()
            last_active_date = user.last_active.date() if user.last_active else None
            
            if last_active_date != today:
                # Нарахувати бали за щоденну активність
                await update_user_points(user_id, POINTS_FOR_DAILY_ACTIVITY, "щоденна активність")
                logger.info(f"💰 Користувач {user_id}: +{POINTS_FOR_DAILY_ACTIVITY} балів за щоденну активність")
        
    except Exception as e:
        logger.debug(f"Не вдалося нарахувати щоденні бали: {e}")

# ===== КОМАНДА /help =====

async def cmd_help(message: Message):
    """Команда /help - повна довідка"""
    help_text = f"{EMOJI['info']} <b>ПОВНА ДОВІДКА ПО БОТУ</b>\n\n"
    
    # Основні команди
    help_text += f"📋 <b>Основні команди:</b>\n"
    help_text += f"• /start - головне меню та привітання\n"
    help_text += f"• /meme - випадковий мем\n"
    help_text += f"• /anekdot - український анекдот\n"
    help_text += f"• /submit [текст] - надіслати жарт\n"
    help_text += f"• /profile - ваш профіль та статистика\n"
    help_text += f"• /top - таблиця лідерів\n"
    help_text += f"• /duel [текст] - створити дуель жартів\n"
    help_text += f"• /daily - підписка на розсилку\n\n"
    
    # Система балів
    help_text += f"💰 <b>Система балів:</b>\n"
    help_text += f"• +{POINTS_FOR_VIEW} - перегляд мему/анекдоту\n"
    help_text += f"• +5 - лайк або дизлайк\n"
    help_text += f"• +10 - подача жарту на модерацію\n"
    help_text += f"• +20 - схвалення вашого жарту\n"
    help_text += f"• +15 - перемога в дуелі\n"
    help_text += f"• +{POINTS_FOR_DAILY_ACTIVITY} - щоденна активність\n"
    help_text += f"• +2 - голосування в дуелі\n\n"
    
    # Ранги
    help_text += f"🏆 <b>Система рангів:</b>\n"
    help_text += f"🤡 Новачок (0+ балів)\n"
    help_text += f"😄 Сміхун (50+ балів)\n"
    help_text += f"😂 Гуморист (150+ балів)\n"
    help_text += f"🎭 Комік (350+ балів)\n"
    help_text += f"👑 Мастер Рофлу (750+ балів)\n"
    help_text += f"🏆 Король Гумору (1500+ балів)\n"
    help_text += f"🌟 Легенда Мемів (3000+ балів)\n"
    help_text += f"🚀 Гумористичний Геній (5000+ балів)\n\n"
    
    # Дуелі
    help_text += f"⚔️ <b>Дуелі жартів:</b>\n"
    help_text += f"• Створюйте дуелі зі своїми жартами\n"
    help_text += f"• Інші користувачі голосують за найсмішніший\n"
    help_text += f"• Переможець отримує +15 балів\n"
    help_text += f"• Учасник отримує +5 балів\n"
    help_text += f"• Голосуючі отримують +2 бали\n\n"
    
    # Модерація
    help_text += f"🛡️ <b>Модерація контенту:</b>\n"
    help_text += f"• Весь контент перевіряється модераторами\n"
    help_text += f"• Схвалений контент бачать всі користувачі\n"
    help_text += f"• За схвалення ви отримуєте +20 балів\n"
    help_text += f"• Якісний контент може потрапити в ТОП\n\n"
    
    # Поради
    help_text += f"💡 <b>Поради для успіху:</b>\n"
    help_text += f"• Надсилайте оригінальні та смішні жарти\n"
    help_text += f"• Активно голосуйте в дуелях\n"
    help_text += f"• Підпишіться на щоденну розсилку\n"
    help_text += f"• Запрошуйте друзів до бота\n"
    help_text += f"• Слідкуйте за своїм рангом у профілі\n\n"
    
    help_text += f"💬 З питаннями звертайтесь до адміністратора!"
    
    # Клавіатура довідки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="back_to_main"),
            InlineKeyboardButton(text="👤 Мій профіль", callback_data="show_profile")
        ],
        [
            InlineKeyboardButton(text="🎮 Спробувати дуель", callback_data="start_duel"),
            InlineKeyboardButton(text="📝 Надіслати жарт", callback_data="submit_content")
        ]
    ])
    
    await message.answer(help_text, reply_markup=keyboard)

# ===== КОМАНДА /daily =====

async def cmd_daily(message: Message):
    """Команда /daily - управління щоденною розсилкою"""
    user_id = message.from_user.id
    
    try:
        from database import get_user_by_id, get_db_session
        
        user = await get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Користувач не знайдений. Використайте /start")
            return
        
        # Переключити підписку
        new_status = not user.daily_subscription
        
        with get_db_session() as session:
            user.daily_subscription = new_status
            session.commit()
        
        if new_status:
            response_text = (
                f"{EMOJI['check']} <b>Підписка активована!</b>\n\n"
                f"📅 Щодня о 9:00 ви отримуватимете:\n"
                f"• Кращий жарт дня\n"
                f"• Топовий мем\n"
                f"• +{POINTS_FOR_DAILY_ACTIVITY} балів за активність\n\n"
                f"🔕 Щоб відписатися, використайте /daily знову"
            )
            
            # Нарахувати бонусні бали за підписку
            from database import update_user_points
            await update_user_points(user_id, 5, "підписка на розсилку")
            
        else:
            response_text = (
                f"{EMOJI['cross']} <b>Підписка відключена</b>\n\n"
                f"😔 Ви більше не отримуватимете щоденну розсилку.\n\n"
                f"📅 Щоб підписатися знову, використайте /daily"
            )
        
        await message.answer(response_text)
        
        logger.info(f"📅 Користувач {user_id} {'підписався' if new_status else 'відписався'} від розсилки")
        
    except Exception as e:
        logger.error(f"❌ Помилка управління розсилкою: {e}")
        await message.answer("❌ Помилка при зміні налаштувань розсилки")

# ===== CALLBACK ХЕНДЛЕРИ =====

async def callback_back_to_main(callback_query: CallbackQuery):
    """Повернутися до головного меню"""
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name or "друже"
    
    user_stats = await get_user_welcome_stats(user_id)
    
    welcome_text = f"{EMOJI['fire']} <b>Головне меню</b>\n\n"
    welcome_text += f"Привіт, {first_name}!\n"
    welcome_text += f"💰 Ваші бали: {user_stats['points']:,}\n"
    welcome_text += f"🏆 Ваш ранг: {user_stats['rank']}\n\n"
    welcome_text += f"Що бажаєте зробити?"
    
    keyboard = get_main_menu_keyboard(user_stats)
    
    await callback_query.message.edit_text(welcome_text, reply_markup=keyboard)
    await callback_query.answer()

async def callback_show_help(callback_query: CallbackQuery):
    """Показати довідку через callback"""
    # Видалити попереднє повідомлення та надіслати нове
    await callback_query.message.delete()
    await cmd_help(callback_query.message)
    await callback_query.answer()

async def callback_toggle_daily(callback_query: CallbackQuery):
    """Переключити щоденну розсилку"""
    user_id = callback_query.from_user.id
    
    try:
        from database import get_user_by_id, get_db_session
        
        user = await get_user_by_id(user_id)
        if not user:
            await callback_query.answer("❌ Користувач не знайдений", show_alert=True)
            return
        
        # Переключити статус
        new_status = not user.daily_subscription
        
        with get_db_session() as session:
            user.daily_subscription = new_status
            session.commit()
        
        status_text = "підключено" if new_status else "відключено"
        points_text = f" (+5 балів)" if new_status else ""
        
        await callback_query.answer(
            f"📅 Щоденну розсилку {status_text}!{points_text}",
            show_alert=True
        )
        
        # Нарахувати бонусні бали за підписку
        if new_status:
            from database import update_user_points
            await update_user_points(user_id, 5, "підписка на розсилку")
        
        logger.info(f"📅 Користувач {user_id} {'підписався' if new_status else 'відписався'}")
        
    except Exception as e:
        logger.error(f"❌ Помилка toggle daily: {e}")
        await callback_query.answer("❌ Помилка налаштувань", show_alert=True)

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_basic_handlers(dp: Dispatcher):
    """Реєстрація основних хендлерів"""
    
    # Команди
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_daily, Command("daily"))
    
    # Callback запити
    dp.callback_query.register(callback_back_to_main, F.data == "back_to_main")
    dp.callback_query.register(callback_show_help, F.data == "show_help")
    dp.callback_query.register(callback_toggle_daily, F.data == "toggle_daily")
    
    logger.info("✅ Основні хендлери зареєстровано")

# ===== ЕКСПОРТ =====

__all__ = [
    'register_basic_handlers', 
    'cmd_start', 
    'cmd_help', 
    'cmd_daily',
    'get_main_menu_keyboard',
    'create_personalized_welcome'
]