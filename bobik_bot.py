#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Головний файл україномовного Telegram-бота 🧠😂🔥
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Додаємо поточну папку до Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Імпорти конфігурації
from config.settings import settings, EMOJI

# Імпорти компонентів
from database.database import init_db
from handlers import register_handlers
from middlewares.auth import AuthMiddleware, AntiSpamMiddleware, LoggingMiddleware
from services.scheduler import SchedulerService
from services.content_generator import auto_generate_content_if_needed

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class UkrainianTelegramBot:
    """Клас україномовного Telegram-бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler_service = None
    
    async def create_bot(self):
        """Створення екземпляру бота"""
        try:
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML
                )
            )
            
            # Перевірка з'єднання
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 Бот ініціалізовано: @{bot_info.username}")
            
            return self.bot
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації бота: {e}")
            raise
    
    async def setup_dispatcher(self):
        """Налаштування диспетчера"""
        self.dp = Dispatcher()
        
        # Підключення middleware
        self.dp.message.middleware(AuthMiddleware())
        self.dp.callback_query.middleware(AuthMiddleware())
        self.dp.message.middleware(AntiSpamMiddleware(rate_limit=3))
        self.dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
        self.dp.message.middleware(LoggingMiddleware())
        self.dp.callback_query.middleware(LoggingMiddleware())
        
        # Реєстрація хендлерів
        register_handlers(self.dp)
        
        logger.info("✅ Диспетчер налаштовано")
    
    async def setup_database(self):
        """Ініціалізація бази даних"""
        try:
            await init_db()
            logger.info("💾 База даних ініціалізована")
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            raise
    
    async def setup_scheduler(self):
        """Налаштування планувальника"""
        try:
            self.scheduler_service = SchedulerService(self.bot)
            await self.scheduler_service.start()
            logger.info("⏰ Планувальник запущено")
        except Exception as e:
            logger.error(f"❌ Помилка планувальника: {e}")
            # Не критична помилка, продовжуємо без планувальника
    
    async def setup_ai_content(self):
        """Налаштування AI генерації контенту"""
        try:
            if settings.OPENAI_API_KEY:
                await auto_generate_content_if_needed()
                logger.info("🤖 AI генерація контенту активна")
            else:
                logger.info("⚠️ OpenAI API ключ не налаштовано - AI вимкнений")
        except Exception as e:
            logger.warning(f"⚠️ Помилка AI: {e}")
    
    async def start_polling(self):
        """Запуск polling"""
        try:
            logger.info(f"🚀 Бот запущено в режимі polling")
            logger.info(f"🇺🇦 Всі повідомлення українською мовою")
            logger.info(f"👤 Адміністратор: {settings.ADMIN_ID}")
            
            # Повідомлення адміністратору про запуск
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['fire']} <b>Бот запущено!</b>\n\n"
                    f"{EMOJI['rocket']} Усі системи працюють\n"
                    f"{EMOJI['brain']} AI {'активний' if settings.OPENAI_API_KEY else 'вимкнений'}\n"
                    f"{EMOJI['calendar']} Планувальник {'активний' if self.scheduler_service else 'вимкнений'}\n"
                    f"{EMOJI['star']} Готовий до роботи!"
                )
            except Exception as e:
                logger.warning(f"Не вдалося повідомити адміністратора: {e}")
            
            # Запуск polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"❌ Помилка під час polling: {e}")
            raise
    
    async def shutdown(self):
        """Коректне завершення роботи"""
        logger.info("🛑 Завершення роботи бота...")
        
        try:
            # Зупинка планувальника
            if self.scheduler_service:
                await self.scheduler_service.stop()
            
            # Закриття сесії бота
            if self.bot:
                await self.bot.session.close()
            
            logger.info("✅ Бот завершив роботу")
            
        except Exception as e:
            logger.error(f"❌ Помилка при завершенні: {e}")

async def main():
    """Головна функція запуску"""
    print("🧠😂🔥" * 20)
    print("🚀 ЗАПУСК УКРАЇНОМОВНОГО TELEGRAM-БОТА 🚀")
    print("🧠😂🔥" * 20)
    print()
    
    # Створення екземпляру бота
    ukrainian_bot = UkrainianTelegramBot()
    
    try:
        # Ініціалізація компонентів
        await ukrainian_bot.create_bot()
        await ukrainian_bot.setup_database()
        await ukrainian_bot.setup_dispatcher()
        await ukrainian_bot.setup_scheduler()
        await ukrainian_bot.setup_ai_content()
        
        # Запуск polling
        await ukrainian_bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("👋 Отримано сигнал завершення (Ctrl+C)")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        sys.exit(1)
    finally:
        await ukrainian_bot.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До побачення!")
    except Exception as e:
        print(f"💥 Помилка запуску: {e}")
        sys.exit(1)