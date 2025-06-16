#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Реєстрація всіх хендлерів бота 🧠😂🔥
"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів з обробкою помилок"""
    
    handlers_to_register = [
        ("basic_commands", "register_basic_handlers", "Основні команди"),
        ("content_handlers", "register_content_handlers", "Контент хендлери"),
        ("gamification_handlers", "register_gamification_handlers", "Гейміфікація"),
        ("moderation_handlers", "register_moderation_handlers", "Модерація"),
        ("duel_handlers", "register_duel_handlers", "Дуелі")
    ]
    
    registered_count = 0
    
    for module_name, func_name, description in handlers_to_register:
        try:
            # Динамічний імпорт модулю
            module = __import__(f"handlers.{module_name}", fromlist=[func_name])
            register_func = getattr(module, func_name)
            
            # Реєстрація хендлерів
            register_func(dp)
            logger.info(f"✅ {description} - зареєстровано")
            registered_count += 1
            
        except ImportError as e:
            logger.warning(f"⚠️ Не вдалося імпортувати {module_name}: {e}")
        except AttributeError as e:
            logger.warning(f"⚠️ Функція {func_name} не знайдена в {module_name}: {e}")
        except Exception as e:
            logger.error(f"❌ Помилка реєстрації {description}: {e}")
    
    logger.info(f"🎯 Зареєстровано {registered_count}/{len(handlers_to_register)} груп хендлерів")
    
    if registered_count == 0:
        logger.warning("⚠️ Жодних хендлерів не зареєстровано!")
        # Реєструємо базовий хендлер як fallback
        register_fallback_handlers(dp)

def register_fallback_handlers(dp: Dispatcher):
    """Реєстрація базових хендлерів як fallback"""
    from aiogram import F
    from aiogram.filters import Command
    from aiogram.types import Message
    
    @dp.message(Command("start"))
    async def cmd_start_fallback(message: Message):
        await message.answer(
            "🧠😂🔥 <b>Вітаю в україномовному боті!</b>\n\n"
            "⚠️ Бот запущено в базовому режимі\n"
            "🔧 Деякі функції можуть бути недоступні\n\n"
            "📞 Зверніться до адміністратора для налаштування"
        )
    
    @dp.message(Command("help"))
    async def cmd_help_fallback(message: Message):
        await message.answer(
            "❓ <b>Довідка</b>\n\n"
            "Доступні команди:\n"
            "• /start - запуск бота\n"
            "• /help - ця довідка\n\n"
            "🔧 Для повного функціоналу потрібно налаштувати всі модулі"
        )
    
    @dp.message(F.text)
    async def fallback_handler(message: Message):
        await message.answer(
            "🤔 Не розумію цю команду\n"
            "Використай /help для допомоги"
        )
    
    logger.info("🔧 Fallback хендлери зареєстровано")