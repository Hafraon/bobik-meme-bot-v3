#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Україномовний Telegram-бот з мемами та анекдотами 🧠😂🔥
Автор: BobikFun Team
Версія: 1.0.0
"""

import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings
from database.database import init_db
from handlers import register_handlers
from middlewares.auth import AuthMiddleware
from services.scheduler import SchedulerService

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Основна функція запуску бота"""
    try:
        # Ініціалізація бота
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Ініціалізація диспетчера
        dp = Dispatcher()
        
        # Підключення middleware
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        
        # Ініціалізація бази даних
        await init_db()
        logger.info("🔥 База даних ініціалізована!")
        
        # Реєстрація хендлерів
        register_handlers(dp)
        logger.info("😂 Хендлери зареєстровані!")
        
        # Запуск планувальника
        scheduler = SchedulerService(bot)
        await scheduler.start()
        logger.info("🧠 Планувальник запущено!")
        
        # Перевірка підключення до бота
        bot_info = await bot.get_me()
        logger.info(f"🔥 Бот запущено: @{bot_info.username}")
        
        # Надсилання повідомлення адміністратору
        try:
            await bot.send_message(
                settings.ADMIN_ID,
                "🧠😂🔥 <b>Бот успішно запущено!</b>\n\n"
                f"🤖 <b>Ім'я:</b> {bot_info.first_name}\n"
                f"📛 <b>Username:</b> @{bot_info.username}\n"
                f"⏰ <b>Час запуску:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
        except Exception as e:
            logger.warning(f"Не вдалося надіслати повідомлення адміністратору: {e}")
        
        # Запуск polling
        logger.info("😂 Початок polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"🔥 Помилка запуску бота: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🧠 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"😂 Критична помилка: {e}")
        sys.exit(1)