#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Україномовний Telegram-бот з гейміфікацією 🧠😂🔥
Повна версія з мемами, анекдотами, балами, рангами, дуелями та модерацією
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Додавання поточної директорії до Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings, EMOJI, validate_settings
from database.database import init_db
from handlers import register_handlers
from middlewares.auth import AuthMiddleware, AntiSpamMiddleware, LoggingMiddleware

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Основний клас україномовного бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler = None
    
    async def create_bot(self):
        """Створення бота з налаштуваннями"""
        self.bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True
            )
        )
        
        # Перевірка підключення до Telegram API
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 Бот підключений: @{bot_info.username} ({bot_info.first_name})")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка підключення до Telegram API: {e}")
            return False
    
    async def setup_dispatcher(self):
        """Налаштування диспетчера з middleware"""
        self.dp = Dispatcher()
        
        # Реєстрація middleware (порядок важливий!)
        self.dp.message.middleware(LoggingMiddleware())  # Логування першим
        self.dp.callback_query.middleware(LoggingMiddleware())
        
        self.dp.message.middleware(AntiSpamMiddleware(rate_limit=3))  # Анти-спам
        self.dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
        
        self.dp.message.middleware(AuthMiddleware())  # Аутентифікація останньою
        self.dp.callback_query.middleware(AuthMiddleware())
        
        # Реєстрація хендлерів
        register_handlers(self.dp)
        
        logger.info("🔧 Диспетчер налаштовано")
    
    async def setup_scheduler(self):
        """Налаштування планувальника для щоденної розсилки"""
        try:
            from services.scheduler import SchedulerService
            self.scheduler = SchedulerService(self.bot)
            await self.scheduler.start()
            logger.info("⏰ Планувальник запущено")
        except ImportError:
            logger.warning("⚠️ Планувальник не знайдено, пропускаємо")
        except Exception as e:
            logger.error(f"❌ Помилка запуску планувальника: {e}")
    
    async def setup_database(self):
        """Ініціалізація бази даних"""
        try:
            await init_db()
            logger.info("💾 База даних ініціалізована")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            return False
    
    async def start_polling(self):
        """Запуск бота в режимі polling"""
        try:
            logger.info("🚀 Запуск бота в режимі polling...")
            
            # Відправка повідомлення адміністратору про запуск
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['rocket']} <b>БОТ ЗАПУЩЕНО!</b>\n\n"
                    f"{EMOJI['check']} Всі системи працюють\n"
                    f"{EMOJI['brain']} Гейміфікація активна\n"
                    f"{EMOJI['fire']} Модерація налаштована\n"
                    f"{EMOJI['vs']} Дуелі готові\n\n"
                    f"{EMOJI['calendar']} Час запуску: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                )
            except Exception as e:
                logger.error(f"Не вдалося повідомити адміністратора: {e}")
            
            # Запуск polling
            await self.dp.start_polling(
                self.bot,
                skip_updates=True,  # Пропускаємо старі повідомлення
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
        except KeyboardInterrupt:
            logger.info("👋 Отримано сигнал зупинки")
        except Exception as e:
            logger.error(f"❌ Помилка під час роботи бота: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Коректне завершення роботи бота"""
        logger.info("🔄 Завершення роботи бота...")
        
        try:
            # Зупинка планувальника
            if self.scheduler:
                await self.scheduler.stop()
                logger.info("⏰ Планувальник зупинено")
            
            # Повідомлення адміністратору
            if self.bot:
                try:
                    await self.bot.send_message(
                        settings.ADMIN_ID,
                        f"{EMOJI['cross']} <b>БОТ ЗУПИНЕНО</b>\n\n"
                        f"{EMOJI['time']} Час зупинки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                    )
                except:
                    pass
                
                # Закриття сесії бота
                await self.bot.session.close()
                logger.info("🤖 Сесія бота закрита")
        
        except Exception as e:
            logger.error(f"❌ Помилка при завершенні: {e}")
    
    async def run(self):
        """Основний метод запуску бота"""
        logger.info(f"{EMOJI['rocket']} Запуск україномовного Telegram-бота")
        
        # Перевірка налаштувань
        if not validate_settings():
            logger.error("❌ Некоректні налаштування!")
            sys.exit(1)
        
        # Ініціалізація компонентів
        steps = [
            ("🤖 Створення бота", self.create_bot),
            ("💾 Ініціалізація БД", self.setup_database),
            ("🔧 Налаштування диспетчера", self.setup_dispatcher),
            ("⏰ Запуск планувальника", self.setup_scheduler),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"▶️ {step_name}...")
            try:
                result = await step_func()
                if result is False:  # Для функцій що повертають bool
                    logger.error(f"❌ Невдалий крок: {step_name}")
                    sys.exit(1)
            except Exception as e:
                logger.error(f"❌ Помилка в кроці '{step_name}': {e}")
                sys.exit(1)
        
        logger.info(f"{EMOJI['party']} Всі компоненти ініціалізовано!")
        
        # Запуск основного циклу
        await self.start_polling()

async def main():
    """Головна функція"""
    
    # Створення директорій для логів
    os.makedirs('logs', exist_ok=True)
    
    # Вітальне повідомлення
    print("🧠😂🔥" * 20)
    print("🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ГЕЙМІФІКАЦІЄЮ 🚀")
    print("🧠😂🔥" * 20)
    print()
    
    # Перевірка обов'язкових змінних
    if not settings.BOT_TOKEN:
        print("❌ Помилка: BOT_TOKEN не налаштовано!")
        print("📝 Додайте BOT_TOKEN до змінних середовища")
        sys.exit(1)
    
    if not settings.ADMIN_ID:
        print("❌ Помилка: ADMIN_ID не налаштовано!")
        print("📝 Додайте ADMIN_ID до змінних середовища")
        sys.exit(1)
    
    # Запуск бота
    bot = UkrainianBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Запуск через asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До побачення!")
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        sys.exit(1)