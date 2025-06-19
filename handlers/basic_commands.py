#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Основні команди бота (ВИПРАВЛЕНО виклик get_or_create_user) 🧠😂🔥
"""

import logging
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config.settings import settings, EMOJI, TEXTS

logger = logging.getLogger(__name__)

async def cmd_start(message: Message):
    """Команда /start з автоматичним адмін-меню"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "друже"
    
    # 🔥 ВИПРАВЛЕНО: Створюємо/оновлюємо користувача в БД
    try:
        from database import get_or_create_user
        # ✅ ПРАВИЛЬНИЙ ВИКЛИК - telegram_id як перший аргумент
        user = await get_or_create_user(
            telegram_id=user_id,  # ✅ ВИПРАВЛЕНО: був user_id=user_id
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        if user:
            logger.info(f"✅ Користувач {user_id} успішно створено/оновлено")
        else:
            logger.warning(f"⚠️ Не вдалося створити користувача {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Помилка створення користувача {user_id}: {e}")
    
    # 🔥 ПЕРЕВІРЯЄМО ЧИ ЦЕ АДМІН І ПОКАЗУЄМО АДМІН-МЕНЮ
    try:
        from handlers.admin_panel_handlers import auto_show_admin_menu_on_start
        admin_menu_shown = await auto_show_admin_menu_on_start(message)
        
        if admin_menu_shown:
            # ✅ Для адміна показуємо тільки коротке основне меню
            keyboard = get_main_menu_keyboard()
            await message.answer(
                f"{EMOJI.get('brain', '🧠')} <b>Основне меню користувачів:</b>",
                reply_markup=keyboard
            )
            logger.info(f"👑 Адмін {user_id} ({first_name}) запустив бота з адмін-меню")
            return
    except ImportError:
        logger.warning("⚠️ Адмін-панель не доступна, працюю без неї")
    except Exception as e:
        logger.error(f"❌ Помилка адмін-панелі: {e}")
    
    # 👤 ЗВИЧАЙНЕ ПРИВІТАННЯ ДЛЯ КОРИСТУВАЧІВ
    keyboard = get_main_menu_keyboard()
    
    # Контекстне привітання за часом дня
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        time_greeting = "Доброго ранку"
    elif 12 <= current_hour < 18:
        time_greeting = "Гарного дня"
    elif 18 <= current_hour < 23:
        time_greeting = "Доброго вечора"
    else:
        time_greeting = "Доброї ночі"
    
    welcome_text = (
        f"{EMOJI.get('brain', '🧠')}{EMOJI.get('laugh', '😂')}{EMOJI.get('fire', '🔥')} <b>{time_greeting}, {first_name}!</b>\n\n"
        f"Ласкаво просимо до українського бота мемів та анекдотів!\n\n"
        f"{EMOJI.get('star', '⭐')} <b>Що я вмію:</b>\n"
        f"• {EMOJI.get('laugh', '😂')} Мемi та анекдоти\n"
        f"• {EMOJI.get('fire', '🔥')} Система балів та рангів\n"
        f"• {EMOJI.get('vs', '⚔️')} Дуелі жартів\n"
        f"• {EMOJI.get('calendar', '📅')} Щоденна розсилка гумору\n\n"
        f"🎮 <b>За активність ви отримуєте бали:</b>\n"
        f"• +1 бал за перегляд контенту\n"
        f"• +5 балів за лайк/дизлайк\n"
        f"• +10 балів за подачу жарту\n"
        f"• +15 балів за перемогу в дуелі\n\n"
        f"Почніть з кнопок нижче! 👇"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)
    logger.info(f"🎉 Користувач {user_id} ({first_name}) запустив бота")

def get_main_menu_keyboard():
    """Головне меню користувача"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😂 Мем (+1)", callback_data="get_meme"),
            InlineKeyboardButton(text="🧠 Анекдот (+1)", callback_data="get_anekdot")
        ],
        [
            InlineKeyboardButton(text="👤 Профіль", callback_data="show_profile"),
            InlineKeyboardButton(text="🏆 Лідери", callback_data="show_leaderboard")
        ],
        [
            InlineKeyboardButton(text="🔥 Надіслати жарт (+10)", callback_data="submit_content"),
            InlineKeyboardButton(text="⚔️ Дуель (+15)", callback_data="start_duel")
        ],
        [
            InlineKeyboardButton(text="📅 Щоденна розсилка (+2)", callback_data="toggle_daily"),
            InlineKeyboardButton(text="❓ Допомога", callback_data="show_help")
        ]
    ])

async def cmd_help(message: Message):
    """Команда /help - довідка"""
    help_text = (
        f"{EMOJI.get('brain', '🧠')} <b>Довідка по боту</b>\n\n"
        f"<b>📋 Команди:</b>\n"
        f"• /start - головне меню\n"
        f"• /meme - випадковий мем\n"
        f"• /anekdot - український анекдот\n"
        f"• /profile - ваш профіль\n"
        f"• /top - таблиця лідерів\n"
        f"• /submit - надіслати жарт\n"
        f"• /duel - дуель жартів\n"
        f"• /daily - підписка на розсилку\n\n"
        f"<b>🎮 Система балів:</b>\n"
        f"• +1 - перегляд мему/анекдоту\n"
        f"• +5 - лайк або дизлайк\n"
        f"• +10 - подача жарту на модерацію\n"
        f"• +20 - схвалення вашого жарту\n"
        f"• +15 - перемога в дуелі\n"
        f"• +2 - щоденна активність\n\n"
        f"<b>🏆 Ранги:</b>\n"
        f"🤡 Новачок (0+ балів)\n"
        f"😄 Сміхун (50+ балів)\n"
        f"😂 Гуморист (150+ балів)\n"
        f"🎭 Комік (350+ балів)\n"
        f"👑 Мастер Рофлу (750+ балів)\n"
        f"🏆 Король Гумору (1500+ балів)\n"
        f"🌟 Легенда Мемів (3000+ балів)\n"
        f"🚀 Гумористичний Геній (5000+ балів)\n\n"
        f"💬 З питаннями звертайтесь до адміністратора!"
    )
    
    await message.answer(help_text)

def register_basic_handlers(dp: Dispatcher):
    """Реєстрація основних хендлерів"""
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    
    logger.info("✅ Основні хендлери зареєстровано!")