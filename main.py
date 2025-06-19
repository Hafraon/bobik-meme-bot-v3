#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ 🧠😂🔥
Повнофункціональний бот з гейміфікацією, модерацією та адмін-панеллю
"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

# Додавання поточної директорії до Python path
sys.path.insert(0, str(Path(__file__).parent))

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Aiogram imports
try:
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest
except ImportError as e:
    logger.error(f"❌ Помилка імпорту aiogram: {e}")
    logger.error("📦 Встановіть: pip install aiogram>=3.4.0")
    sys.exit(1)

class UkrainianTelegramBot:
    """Професійний клас україномовного Telegram-бота"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.scheduler_service = None
        self.is_running = False
        self.startup_time = datetime.now()
        
        # Обробка сигналів для коректного завершення
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обробка сигналів завершення"""
        logger.info(f"🛑 Отримано сигнал {signum}, завершуємо роботу...")
        self.is_running = False
    
    def print_banner(self):
        """Красивий банер запуску"""
        banner = """
🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥

    🚀 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ 🚀
             З ГЕЙМІФІКАЦІЄЮ ТА МОДЕРАЦІЄЮ

🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥🧠😂🔥
"""
        print(banner)
    
    def load_settings(self):
        """Завантаження налаштувань з fallback механізмом"""
        try:
            from config.settings import settings
            logger.info("✅ Налаштування завантажено з config.settings")
            return settings
        except ImportError:
            logger.info("⚠️ Використовую fallback налаштування")
            
            class FallbackSettings:
                # Основні налаштування
                BOT_TOKEN = os.getenv("BOT_TOKEN", "")
                ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
                DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
                CHANNEL_ID = os.getenv("CHANNEL_ID", "")
                OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
                
                # Налаштування бота
                DEBUG = os.getenv("DEBUG", "False").lower() == "true"
                LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
                TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
                ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
                
                # Гейміфікація
                POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
                POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
                POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
                POINTS_FOR_TOP_JOKE = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
                POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
                POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
                
                # Щоденна розсилка
                DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
                DAILY_BROADCAST_MINUTE = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
                
                # Дуелі
                DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))
                MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
                
                # Емодзі
                EMOJI = {
                    "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐",
                    "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
                    "crown": "👑", "rocket": "🚀", "vs": "⚔️", "calendar": "📅"
                }
            
            return FallbackSettings()
    
    def validate_settings(self, settings):
        """Валідація налаштувань"""
        logger.info("🔍 Перевірка налаштувань...")
        
        if not settings.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не знайдено!")
            return False
        
        if not settings.ADMIN_ID:
            logger.error("❌ ADMIN_ID не знайдено!")
            return False
        
        if not settings.DATABASE_URL:
            logger.error("❌ DATABASE_URL не знайдено!")
            return False
        
        logger.info("✅ Основні налаштування валідні")
        return True
    
    async def init_database(self):
        """Ініціалізація бази даних"""
        logger.info("💾 Ініціалізація БД...")
        
        try:
            from database import (
                init_db, 
                check_if_migration_needed,
                migrate_database,
                verify_database_integrity
            )
            
            # Перевірка необхідності міграції
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
                logger.warning("⚠️ БД має проблеми, але продовжуємо")
                return True
                
        except ImportError:
            logger.error("❌ Модуль database не знайдено")
            return False
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            return False
    
    async def create_bot(self, settings):
        """Створення та налаштування бота"""
        logger.info("🤖 Створення бота...")
        
        try:
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            )
            
            # Перевірка з'єднання
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 Бот підключений: @{bot_info.username} ({bot_info.first_name})")
            
            return True
            
        except TelegramNetworkError as e:
            logger.error(f"❌ Помилка мережі Telegram: {e}")
            return False
        except TelegramBadRequest as e:
            logger.error(f"❌ Неправильний токен бота: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Помилка створення бота: {e}")
            return False
    
    async def setup_dispatcher(self):
        """Налаштування диспетчера та middleware"""
        logger.info("🔧 Налаштування диспетчера...")
        
        try:
            self.dp = Dispatcher()
            
            # Підключення middleware
            try:
                from middlewares.auth import LoggingMiddleware, AntiSpamMiddleware, AuthMiddleware
                
                # Логування
                self.dp.message.middleware(LoggingMiddleware())
                self.dp.callback_query.middleware(LoggingMiddleware())
                
                # Антиспам
                self.dp.message.middleware(AntiSpamMiddleware(rate_limit=3))
                self.dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
                
                # Аутентифікація
                self.dp.message.middleware(AuthMiddleware())
                self.dp.callback_query.middleware(AuthMiddleware())
                
                logger.info("✅ Middleware підключено")
                
            except ImportError as e:
                logger.warning(f"⚠️ Middleware не підключено: {e}")
            
            # Підключення хендлерів
            try:
                from handlers import register_handlers
                register_handlers(self.dp)
                logger.info("✅ Хендлери підключено")
                
            except ImportError as e:
                logger.error(f"❌ Помилка підключення хендлерів: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка налаштування диспетчера: {e}")
            return False
    
    async def setup_scheduler(self, settings):
        """Налаштування планувальника задач"""
        logger.info("📅 Налаштування планувальника...")
        
        try:
            from services.scheduler import SchedulerService
            
            self.scheduler_service = SchedulerService(self.bot)
            await self.scheduler_service.start()
            
            logger.info("✅ Планувальник запущено")
            return True
            
        except ImportError:
            logger.warning("⚠️ Планувальник не знайдено, працюю без нього")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка планувальника: {e}")
            return True  # Не критична помилка
    
    async def startup_checks(self, settings):
        """Перевірки при запуску"""
        logger.info("🔍 Перевірки при запуску...")
        
        try:
            # Перевірка адміністратора
            from database import get_or_create_user
            
            admin_user = await get_or_create_user(
                telegram_id=settings.ADMIN_ID,
                username="admin",
                first_name="Адміністратор"
            )
            
            if admin_user:
                logger.info(f"✅ Адміністратор {settings.ADMIN_ID} підтверджений")
            else:
                logger.warning(f"⚠️ Не вдалося підтвердити адміністратора {settings.ADMIN_ID}")
            
            # Перевірка статистики
            from database import get_bot_statistics, update_bot_statistics
            
            stats = await get_bot_statistics()
            if stats:
                logger.info(f"📊 Статистика: {stats.get('total_users', 0)} користувачів")
            
            await update_bot_statistics()
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Помилка перевірок при запуску: {e}")
            return True  # Не критично
    
    async def run_bot(self):
        """Запуск бота"""
        logger.info("🚀 Запуск бота...")
        
        try:
            self.is_running = True
            
            logger.info("✅ Бот успішно запущено!")
            logger.info(f"📊 Час запуску: {self.startup_time}")
            logger.info("🛑 Для зупинки натисніть Ctrl+C")
            
            # Запуск polling
            await self.dp.start_polling(
                self.bot,
                skip_updates=True,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
        except KeyboardInterrupt:
            logger.info("🛑 Отримано сигнал зупинки від клавіатури")
        except Exception as e:
            logger.error(f"❌ Помилка під час роботи бота: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Коректне завершення роботи бота"""
        logger.info("🛑 Завершення роботи бота...")
        
        try:
            # Зупинка планувальника
            if self.scheduler_service:
                await self.scheduler_service.stop()
                logger.info("✅ Планувальник зупинено")
            
            # Закриття сесії бота
            if self.bot:
                await self.bot.session.close()
                logger.info("✅ Сесія бота закрита")
            
            self.is_running = False
            
            # Розрахунок часу роботи
            uptime = datetime.now() - self.startup_time
            logger.info(f"📊 Час роботи: {uptime}")
            logger.info("👋 Бот зупинено коректно")
            
        except Exception as e:
            logger.error(f"❌ Помилка при завершенні: {e}")
    
    async def main(self):
        """Головна функція запуску"""
        self.print_banner()
        
        try:
            # Крок 1: Завантаження налаштувань
            logger.info("▶️ 🔍 Завантаження налаштувань...")
            settings = self.load_settings()
            
            if not self.validate_settings(settings):
                logger.error("❌ Помилка валідації налаштувань")
                return False
            
            # Крок 2: Ініціалізація БД
            logger.info("▶️ 💾 Ініціалізація БД...")
            if not await self.init_database():
                logger.error("❌ Критична помилка БД")
                return False
            
            # Крок 3: Створення бота
            logger.info("▶️ 🤖 Створення бота...")
            if not await self.create_bot(settings):
                logger.error("❌ Не вдалося створити бота")
                return False
            
            # Крок 4: Налаштування диспетчера
            logger.info("▶️ 🔧 Налаштування диспетчера...")
            if not await self.setup_dispatcher():
                logger.error("❌ Помилка налаштування диспетчера")
                return False
            
            # Крок 5: Планувальник
            logger.info("▶️ 📅 Налаштування планувальника...")
            await self.setup_scheduler(settings)
            
            # Крок 6: Перевірки при запуску
            logger.info("▶️ 🔍 Перевірки при запуску...")
            await self.startup_checks(settings)
            
            # Крок 7: Запуск
            logger.info("▶️ 🚀 Запуск бота...")
            await self.run_bot()
            
            return True
            
        except Exception as e:
            logger.error(f"💥 КРИТИЧНА ПОМИЛКА: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

def main():
    """Точка входу в програму"""
    bot = UkrainianTelegramBot()
    
    try:
        result = asyncio.run(bot.main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Зупинка через Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Неочікувана помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()