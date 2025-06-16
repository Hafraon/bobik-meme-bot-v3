#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Реєстрація хендлерів україномовного бота 🧠😂🔥
"""

import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import EMOJI, TEXTS

logger = logging.getLogger(__name__)

async def cmd_start(message: Message):
    """Базова команда /start"""
    await message.answer(TEXTS["start"])
    logger.info(f"🧠 Користувач {message.from_user.id} запустив бота")

async def cmd_help(message: Message):
    """Базова команда /help"""
    await message.answer(TEXTS["help"])
    logger.info(f"😂 Користувач {message.from_user.id} подивився довідку")

async def cmd_test(message: Message):
    """Тестова команда для перевірки роботи"""
    await message.answer(
        f"{EMOJI['fire']} <b>Бот працює!</b>\n\n"
        f"{EMOJI['brain']} Тестова команда виконана успішно\n"
        f"{EMOJI['rocket']} Всі системи в нормі!"
    )
    logger.info(f"🔥 Користувач {message.from_user.id} виконав тест")

def register_handlers(dp: Dispatcher):
    """Реєстрація базових хендлерів"""
    try:
        # Основні команди
        dp.message.register(cmd_start, Command("start"))
        dp.message.register(cmd_help, Command("help"))
        dp.message.register(cmd_test, Command("test"))
        
        logger.info(f"{EMOJI['check']} Базові хендлери зареєстровано")
        
        # Спроба реєстрації додаткових хендлерів
        try:
            from .basic_commands import register_basic_handlers
            register_basic_handlers(dp)
            logger.info(f"{EMOJI['check']} Основні хендлери зареєстровано")
        except ImportError as e:
            logger.warning(f"{EMOJI['warning']} Основні хендлери недоступні: {e}")
        
        try:
            from .content_handlers import register_content_handlers
            register_content_handlers(dp)
            logger.info(f"{EMOJI['check']} Контент хендлери зареєстровано")
        except ImportError as e:
            logger.warning(f"{EMOJI['warning']} Контент хендлери недоступні: {e}")
        
        try:
            from .gamification_handlers import register_gamification_handlers
            register_gamification_handlers(dp)
            logger.info(f"{EMOJI['check']} Гейміфікація хендлери зареєстровано")
        except ImportError as e:
            logger.warning(f"{EMOJI['warning']} Гейміфікація хендлери недоступні: {e}")
        
        try:
            from .moderation_handlers import register_moderation_handlers
            register_moderation_handlers(dp)
            logger.info(f"{EMOJI['check']} Модерація хендлери зареєстровано")
        except ImportError as e:
            logger.warning(f"{EMOJI['warning']} Модерація хендлери недоступні: {e}")
        
        try:
            from .duel_handlers import register_duel_handlers
            register_duel_handlers(dp)
            logger.info(f"{EMOJI['check']} Дуель хендлери зареєстровано")
        except ImportError as e:
            logger.warning(f"{EMOJI['warning']} Дуель хендлери недоступні: {e}")
            
    except Exception as e:
        logger.error(f"{EMOJI['cross']} Помилка реєстрації хендлерів: {e}")
        # Продовжуємо з базовими хендлерами