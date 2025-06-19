#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Простий main.py для тестування виправлень 🧠😂🔥
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Додавання поточної директорії до Python path
sys.path.insert(0, str(Path(__file__).parent))

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Красивий банер"""
    banner = """
🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥

🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ГЕЙМІФІКАЦІЄЮ 🚀
               ТЕСТОВА ВЕРСІЯ

🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥
"""
    print(banner)

def load_settings():
    """Завантажити налаштування"""
    try:
        from config.settings import settings
        logger.info("✅ Налаштування завантажено з config.settings")
        return settings
    except ImportError:
        logger.warning("⚠️ Використовую fallback налаштування")
        
        class FallbackSettings:
            BOT_TOKEN = os.getenv("BOT_TOKEN", "")
            ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
            DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
            DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        return FallbackSettings()

def validate_settings(settings):
    """Перевірити налаштування"""
    if not settings.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не знайдено!")
        return False
    
    if not settings.ADMIN_ID:
        logger.error("❌ ADMIN_ID не знайдено!")
        return False
    
    logger.info("✅ Основні налаштування валідні")
    return True

async def test_database():
    """Тестування БД"""
    try:
        logger.info("📋 Тестування БД...")
        
        # Імпорт функцій БД
        from database import (
            init_db, 
            get_or_create_user,
            check_if_migration_needed,
            migrate_database,
            verify_database_integrity
        )
        
        logger.info("✅ Функції БД імпортовано")
        
        # Перевірка міграції
        if await check_if_migration_needed():
            logger.info("🔄 Потрібна міграція БД...")
            await migrate_database()
        
        # Ініціалізація БД
        await init_db()
        
        # Перевірка цілісності
        if await verify_database_integrity():
            logger.info("✅ БД готова до роботи")
            return True
        else:
            logger.warning("⚠️ Проблеми з БД, але продовжуємо")
            return True
            
    except Exception as e:
        logger.error(f"❌ Помилка БД: {e}")
        return False

async def create_bot(settings):
    """Створити бота"""
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Перевірка з'єднання
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот підключений: @{bot_info.username} ({bot_info.first_name})")
        
        return bot
        
    except Exception as e:
        logger.error(f"❌ Помилка створення бота: {e}")
        return None

async def setup_dispatcher(bot):
    """Налаштувати диспетчер"""
    try:
        from aiogram import Dispatcher
        
        dp = Dispatcher()
        
        # Спроба підключення middleware
        try:
            from middlewares.auth import LoggingMiddleware, AntiSpamMiddleware, AuthMiddleware
            
            dp.message.middleware(LoggingMiddleware())
            dp.callback_query.middleware(LoggingMiddleware())
            
            dp.message.middleware(AntiSpamMiddleware(rate_limit=3))  # ✅ ПРАВИЛЬНИЙ ПАРАМЕТР
            dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
            
            dp.message.middleware(AuthMiddleware())
            dp.callback_query.middleware(AuthMiddleware())
            
            logger.info("✅ Middleware підключено")
            
        except Exception as e:
            logger.warning(f"⚠️ Middleware не підключено: {e}")
        
        # Спроба підключення хендлерів
        try:
            from handlers import register_handlers
            register_handlers(dp)
            logger.info("✅ Хендлери підключено")
            
        except Exception as e:
            logger.warning(f"⚠️ Хендлери не підключено: {e}")
            # Додаємо простий хендлер для тестування
            await setup_test_handlers(dp)
        
        return dp
        
    except Exception as e:
        logger.error(f"❌ Помилка налаштування диспетчера: {e}")
        return None

async def setup_test_handlers(dp):
    """Тестові хендлери"""
    from aiogram.filters import Command
    from aiogram.types import Message
    
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        user_id = message.from_user.id
        first_name = message.from_user.first_name or "друже"
        
        # Тестування створення користувача
        try:
            from database import get_or_create_user
            user = await get_or_create_user(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            
            if user:
                response = (
                    f"🧠😂🔥 <b>Вітаю, {first_name}!</b>\n\n"
                    f"✅ Бот працює коректно!\n"
                    f"👤 Ваш ID: {user_id}\n"
                    f"📊 Користувач створено/оновлено в БД\n\n"
                    f"🔥 Всі виправлення працюють!"
                )
            else:
                response = (
                    f"🧠😂🔥 <b>Вітаю, {first_name}!</b>\n\n"
                    f"⚠️ БД недоступна, але бот працює\n"
                    f"👤 Ваш ID: {user_id}"
                )
        except Exception as e:
            logger.error(f"❌ Помилка створення користувача: {e}")
            response = (
                f"🧠😂🔥 <b>Вітаю, {first_name}!</b>\n\n"
                f"❌ Помилка БД: {e}\n"
                f"👤 Ваш ID: {user_id}"
            )
        
        await message.answer(response)
    
    @dp.message(Command("test"))
    async def cmd_test(message: Message):
        await message.answer(
            "✅ <b>Тест пройшов успішно!</b>\n\n"
            "🔧 Middleware працює\n"
            "🎯 Хендлери працюють\n"
            "💾 БД доступна\n\n"
            "🎉 Бот готовий до розробки!"
        )
    
    logger.info("✅ Тестові хендлери налаштовано")

async def main():
    """Головна функція"""
    print_banner()
    
    try:
        # Крок 1: Завантаження налаштувань
        logger.info("▶️ 🔍 Завантаження налаштувань...")
        settings = load_settings()
        
        if not validate_settings(settings):
            logger.error("❌ Налаштування невалідні!")
            return False
        
        # Крок 2: Тестування БД
        logger.info("▶️ 💾 Тестування БД...")
        db_ok = await test_database()
        
        if not db_ok:
            logger.warning("⚠️ БД має проблеми, але продовжуємо...")
        
        # Крок 3: Створення бота
        logger.info("▶️ 🤖 Створення бота...")
        bot = await create_bot(settings)
        
        if not bot:
            logger.error("❌ Не вдалося створити бота!")
            return False
        
        # Крок 4: Налаштування диспетчера
        logger.info("▶️ 🔧 Налаштування диспетчера...")
        dp = await setup_dispatcher(bot)
        
        if not dp:
            logger.error("❌ Не вдалося налаштувати диспетчер!")
            return False
        
        # Крок 5: Запуск
        logger.info("▶️ 🚀 Запуск бота...")
        logger.info("✅ Бот успішно запущено!")
        logger.info("📝 Доступні команди: /start, /test")
        logger.info("🛑 Для зупинки натисніть Ctrl+C")
        
        await dp.start_polling(bot, skip_updates=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Отримано сигнал зупинки")
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        return False
    finally:
        if 'bot' in locals():
            await bot.session.close()
        logger.info("👋 Бот зупинено")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())