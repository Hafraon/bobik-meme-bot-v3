#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ФІНАЛЬНА РЕЄСТРАЦІЯ ВСІХ ХЕНДЛЕРІВ 🧠😂🔥
"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    """
    Реєстрація всіх хендлерів бота в правильному порядку
    
    ВАЖЛИВО: Порядок реєстрації має значення!
    Більш специфічні хендлери мають реєструватися перед загальними.
    """
    
    logger.info("🚀 Починаю реєстрацію хендлерів...")
    
    # ===== 1. ОСНОВНІ КОМАНДИ =====
    try:
        from .basic_commands import register_basic_handlers
        register_basic_handlers(dp)
        logger.info("✅ Зареєстровано основні команди")
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту basic_commands: {e}")
        register_fallback_basic_handlers(dp)
    
    # ===== 2. АДМІН-ПАНЕЛЬ =====
    try:
        from .admin_panel_handlers import register_admin_handlers
        register_admin_handlers(dp)
        logger.info("✅ Зареєстровано адмін-панель")
    except ImportError as e:
        logger.warning(f"⚠️ Адмін-панель не завантажена: {e}")
    
    # ===== 3. КОНТЕНТ (МЕМИ/АНЕКДОТИ) =====
    try:
        from .content_handlers import register_content_handlers
        register_content_handlers(dp)
        logger.info("✅ Зареєстровано контент")
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту content_handlers: {e}")
        register_fallback_content_handlers(dp)
    
    # ===== 4. ГЕЙМІФІКАЦІЯ =====
    try:
        from .gamification_handlers import register_gamification_handlers
        register_gamification_handlers(dp)
        logger.info("✅ Зареєстровано гейміфікацію")
    except ImportError as e:
        logger.warning(f"⚠️ Гейміфікація не завантажена: {e}")
    
    # ===== 5. ДУЕЛІ =====
    try:
        from .duel_handlers import register_duel_handlers
        register_duel_handlers(dp)
        logger.info("✅ Зареєстровано дуелі")
    except ImportError as e:
        logger.warning(f"⚠️ Дуелі не завантажені: {e}")
    
    # ===== 6. МОДЕРАЦІЯ =====
    try:
        from .moderation_handlers import register_moderation_handlers
        register_moderation_handlers(dp)
        logger.info("✅ Зареєстровано модерацію")
    except ImportError as e:
        logger.warning(f"⚠️ Модерація не завантажена: {e}")
        # Модерація може бути частиною адмін-панелі
    
    # ===== 7. ІНШІ ХЕНДЛЕРИ =====
    try:
        # Тут можна додати інші спеціалізовані хендлери
        pass
    except ImportError as e:
        logger.warning(f"⚠️ Додаткові хендлери не завантажені: {e}")
    
    logger.info("🎯 Всі хендлери успішно зареєстровані!")

# ===== FALLBACK ХЕНДЛЕРИ =====

def register_fallback_basic_handlers(dp: Dispatcher):
    """Fallback основні хендлери"""
    from aiogram.filters import Command, CommandStart
    from aiogram.types import Message
    
    @dp.message(CommandStart())
    async def fallback_start(message: Message):
        await message.answer(
            "🧠😂🔥 <b>Вітаю!</b>\n\n"
            "Бот запущено у базовому режимі.\n"
            "Деякі функції можуть бути недоступні.\n\n"
            "Доступні команди:\n"
            "• /help - довідка\n"
            "• /meme - отримати мем\n"
            "• /anekdot - отримати анекдот"
        )
    
    @dp.message(Command("help"))
    async def fallback_help(message: Message):
        await message.answer(
            "❓ <b>Довідка</b>\n\n"
            "Доступні команди:\n"
            "• /start - головне меню\n"
            "• /meme - випадковий мем\n"
            "• /anekdot - український анекдот\n"
            "• /profile - ваш профіль\n"
            "• /top - таблиця лідерів\n"
            "• /duel - дуель жартів\n\n"
            "📝 Надішліть жарт боту щоб подати на модерацію!"
        )
    
    logger.info("✅ Fallback основні хендлери зареєстровано")

def register_fallback_content_handlers(dp: Dispatcher):
    """Fallback хендлери контенту"""
    from aiogram.filters import Command
    from aiogram.types import Message
    import random
    
    # Fallback жарти
    FALLBACK_JOKES = [
        "Що робить програміст коли не може заснути? Рахує овець у циклі while!",
        "Чому програмісти люблять темний режим? Тому що світло приваблює жуків!",
        "Що сказав HTML CSS? Без тебе я нічого не значу!",
        "Програміст заходить в бар і замовляє 1 пиво, 0 пив, -1 пиво, NULL пив...",
        "Чому програмісти плутають Хеллоуін і Різдво? Тому що 31 OCT = 25 DEC!"
    ]
    
    @dp.message(Command("meme"))
    async def fallback_meme(message: Message):
        joke = random.choice(FALLBACK_JOKES)
        await message.answer(
            f"🔥 <b>Мем:</b>\n\n{joke}\n\n"
            f"💡 <i>Це fallback контент. Додайте власні меми!</i>"
        )
    
    @dp.message(Command("anekdot"))
    async def fallback_anekdot(message: Message):
        joke = random.choice(FALLBACK_JOKES)
        await message.answer(
            f"😂 <b>Анекдот:</b>\n\n{joke}\n\n"
            f"💡 <i>Це fallback контент. Додайте власні анекдоти!</i>"
        )
    
    @dp.message(Command("submit"))
    async def fallback_submit(message: Message):
        await message.answer(
            "📝 <b>Подача контенту</b>\n\n"
            "Функція подачі контенту недоступна в базовому режимі.\n"
            "Для повного функціоналу потрібна БД та модерація.\n\n"
            "💡 Просто надішліть свій жарт боту!"
        )
    
    logger.info("✅ Fallback контент хендлери зареєстровано")

# ===== ДІАГНОСТИКА =====

def check_handlers_status():
    """Перевірити статус завантаження хендлерів"""
    handlers_status = {
        "basic_commands": False,
        "admin_panel": False,
        "content_handlers": False,
        "gamification": False,
        "duel_handlers": False,
        "moderation": False
    }
    
    # Перевірити basic_commands
    try:
        from . import basic_commands
        handlers_status["basic_commands"] = True
    except ImportError:
        pass
    
    # Перевірити admin_panel
    try:
        from . import admin_panel_handlers
        handlers_status["admin_panel"] = True
    except ImportError:
        pass
    
    # Перевірити content_handlers
    try:
        from . import content_handlers
        handlers_status["content_handlers"] = True
    except ImportError:
        pass
    
    # Перевірити gamification
    try:
        from . import gamification_handlers
        handlers_status["gamification"] = True
    except ImportError:
        pass
    
    # Перевірити duel_handlers
    try:
        from . import duel_handlers
        handlers_status["duel_handlers"] = True
    except ImportError:
        pass
    
    # Перевірити moderation
    try:
        from . import moderation_handlers
        handlers_status["moderation"] = True
    except ImportError:
        pass
    
    return handlers_status

def log_handlers_status():
    """Залогувати статус хендлерів"""
    status = check_handlers_status()
    
    logger.info("📋 Статус хендлерів:")
    for handler_name, is_loaded in status.items():
        status_icon = "✅" if is_loaded else "❌"
        logger.info(f"  {status_icon} {handler_name}")
    
    loaded_count = sum(status.values())
    total_count = len(status)
    
    logger.info(f"📊 Завантажено: {loaded_count}/{total_count} хендлерів")
    
    if loaded_count == total_count:
        logger.info("🎉 Всі хендлери завантажені успішно!")
    elif loaded_count >= total_count // 2:
        logger.warning("⚠️ Деякі хендлери не завантажені, але бот працездатний")
    else:
        logger.error("❌ Критично мало хендлерів! Перевірте імпорти")
    
    return status

# ===== ЕКСПОРТ =====

__all__ = [
    'register_handlers',
    'check_handlers_status',
    'log_handlers_status',
    'register_fallback_basic_handlers',
    'register_fallback_content_handlers'
]

# Виконати діагностику при імпорті
if __name__ != "__main__":
    log_handlers_status()