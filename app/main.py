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
import signal
from datetime import datetime
from pathlib import Path

# Додавання поточної директорії до Python path
sys.path.insert(0, str(Path(__file__).parent))

# Aiogram imports з підтримкою різних версій
try:
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.client.session.aiohttp import AiohttpSession
except ImportError as e:
    print(f"❌ Помилка імпорту aiogram: {e}")
    print("📦 Встановіть: pip install aiogram>=3.4.0")
    sys.exit(1)

# Налаштування з fallback механізмами
settings = None
EMOJI = {}

def load_settings():
    """Завантаження налаштувань з різних можливих джерел"""
    global settings, EMOJI
    
    # Спроба 1: Нова структура config/settings.py
    try:
        from config.settings import Settings
        settings = Settings()
        
        # Додаємо недостатні атрибути якщо їх немає
        if not hasattr(settings, 'ADMIN_ID'):
            settings.ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        if not hasattr(settings, 'DATABASE_URL'):
            settings.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        if not hasattr(settings, 'DEBUG'):
            settings.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        print("✅ Завантажено налаштування з config.settings")
        
    except ImportError:
        # Спроба 2: Старий варіант settings.py
        try:
            from settings import settings as old_settings, EMOJI as old_emoji
            settings = old_settings
            EMOJI = old_emoji
            print("✅ Завантажено налаштування з settings.py")
        except ImportError:
            # Спроба 3: Fallback налаштування
            print("⚠️ Використовую fallback налаштування")
            
            class FallbackSettings:
                def __init__(self):
                    self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
                    self.ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
                    self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
                    self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
                    self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
                    self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
                    self.CHANNEL_ID = os.getenv("CHANNEL_ID", "")
                    
                    # Гейміфікація
                    self.POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
                    self.POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
                    self.POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
                    self.POINTS_FOR_TOP_JOKE = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
                    self.POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
                    self.POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
                    
                    # Обмеження
                    self.MAX_JOKE_LENGTH = int(os.getenv("MAX_JOKE_LENGTH", "1000"))
                    self.MAX_MEME_CAPTION_LENGTH = int(os.getenv("MAX_MEME_CAPTION_LENGTH", "200"))
                    
                    # Дуелі
                    self.DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))
                    self.MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
                    
                    # Щоденна розсилка
                    self.DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
                    self.DAILY_BROADCAST_MINUTE = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
            
            settings = FallbackSettings()
    
    # Завантаження EMOJI якщо не завантажено
    if not EMOJI:
        EMOJI = {
            "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", 
            "heart": "❤️", "trophy": "🏆", "crown": "👑", "rocket": "🚀",
            "party": "🎉", "boom": "💥", "like": "👍", "dislike": "👎",
            "thinking": "🤔", "cool": "😎", "wink": "😉", "eye": "👁️",
            "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
            "new": "🆕", "top": "🔝", "vs": "⚔️", "time": "⏰",
            "calendar": "📅", "stats": "📊", "profile": "👤", "help": "❓"
        }

# Налаштування логування
def setup_logging():
    """Налаштування системи логування"""
    
    # Створення директорії для логів
    os.makedirs('logs', exist_ok=True)
    
    # Рівень логування
    log_level = getattr(logging, getattr(settings, 'LOG_LEVEL', 'INFO'), logging.INFO)
    
    # Налаштування форматування
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольний handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Файловий handler
    file_handler = logging.FileHandler('logs/bot.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Налаштування root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Зменшення рівня логування для зовнішніх бібліотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Основний клас україномовного бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler = None
        self._shutdown_event = asyncio.Event()
    
    async def validate_environment(self):
        """Валідація оточення та налаштувань"""
        logger.info("🔍 Перевірка налаштувань...")
        
        errors = []
        
        # Перевірка обов'язкових змінних
        if not settings.BOT_TOKEN:
            errors.append("BOT_TOKEN не налаштовано")
        
        if not settings.ADMIN_ID:
            errors.append("ADMIN_ID не налаштовано")
        
        # Перевірка структури файлів
        required_dirs = ['handlers', 'database', 'config']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                errors.append(f"Папка '{dir_name}' не знайдена")
        
        if errors:
            logger.error("❌ Помилки конфігурації:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("✅ Налаштування валідні")
        return True
    
    async def create_bot(self):
        """Створення бота з налаштуваннями"""
        try:
            # Створення сесії
            session = AiohttpSession()
            
            # Створення бота
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                session=session,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    link_preview_is_disabled=True
                )
            )
            
            # Перевірка підключення
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 Бот підключений: @{bot_info.username} ({bot_info.first_name})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення бота: {e}")
            return False
    
    async def setup_database(self):
        """Ініціалізація бази даних"""
        try:
            # Спроба імпорту database модуля
            try:
                from database.database import init_db
                await init_db()
                logger.info("💾 База даних ініціалізована")
                return True
            except ImportError:
                logger.warning("⚠️ Модуль database.database не знайдено, пропускаю ініціалізацію БД")
                return True
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            return False
    
    async def setup_dispatcher(self):
        """Налаштування диспетчера та хендлерів"""
        try:
            self.dp = Dispatcher()
            
            # Реєстрація middleware (якщо є)
            try:
                from middlewares.auth import AuthMiddleware, AntiSpamMiddleware, LoggingMiddleware
                
                self.dp.message.middleware(LoggingMiddleware())
                self.dp.callback_query.middleware(LoggingMiddleware())
                
                self.dp.message.middleware(AntiSpamMiddleware(rate_limit=3))
                self.dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
                
                self.dp.message.middleware(AuthMiddleware())
                self.dp.callback_query.middleware(AuthMiddleware())
                
                logger.info("🔧 Middleware підключено")
            except ImportError:
                logger.warning("⚠️ Middleware не знайдено, працюю без них")
            
            # Реєстрація хендлерів
            try:
                from handlers import register_handlers
                register_handlers(self.dp)
                logger.info("🎯 Хендлери зареєстровані")
                return True
            except ImportError:
                logger.error("❌ Не вдалося завантажити хендлери")
                # Спроба fallback реєстрації
                return await self.setup_fallback_handlers()
                
        except Exception as e:
            logger.error(f"❌ Помилка налаштування диспетчера: {e}")
            return False
    
    async def setup_fallback_handlers(self):
        """Fallback реєстрація базових хендлерів"""
        try:
            from aiogram.filters import Command
            
            # Базовий /start хендлер
            @self.dp.message(Command("start"))
            async def cmd_start(message):
                await message.answer(
                    f"{EMOJI.get('fire', '🔥')} <b>Вітаю!</b>\n\n"
                    f"Бот запущено у fallback режимі.\n"
                    f"Додайте хендлери для повної функціональності."
                )
            
            logger.info("🔄 Fallback хендлери зареєстровані")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка fallback хендлерів: {e}")
            return False
    
    async def setup_scheduler(self):
        """Налаштування планувальника (опціонально)"""
        try:
            from services.scheduler import SchedulerService
            self.scheduler = SchedulerService(self.bot)
            await self.scheduler.start()
            logger.info("⏰ Планувальник запущено")
            return True
        except ImportError:
            logger.info("ℹ️ Планувальник не знайдено, працюю без автоматичних задач")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка планувальника: {e}")
            return True  # Не критична помилка
    
    async def notify_admin_startup(self):
        """Повідомлення адміністратору про запуск"""
        if not self.bot or not settings.ADMIN_ID:
            return
        
        try:
            startup_message = (
                f"{EMOJI.get('rocket', '🚀')} <b>БОТ ЗАПУЩЕНО!</b>\n\n"
                f"{EMOJI.get('check', '✅')} Всі системи працюють\n"
                f"{EMOJI.get('brain', '🧠')} Гейміфікація активна\n"
                f"{EMOJI.get('fire', '🔥')} Модерація налаштована\n"
                f"{EMOJI.get('vs', '⚔️')} Дуелі готові\n\n"
                f"{EMOJI.get('calendar', '📅')} Час запуску: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            )
            
            await self.bot.send_message(settings.ADMIN_ID, startup_message)
            logger.info("📤 Повідомлення адміністратору надіслано")
            
        except Exception as e:
            logger.error(f"Не вдалося повідомити адміністратора: {e}")
    
    async def start_polling(self):
        """Запуск бота в режимі polling"""
        try:
            logger.info("🚀 Запуск бота в режимі polling...")
            
            # Відправка повідомлення адміністратору
            await self.notify_admin_startup()
            
            # Налаштування graceful shutdown
            def signal_handler(signum, frame):
                logger.info(f"📶 Отримано сигнал {signum}")
                self._shutdown_event.set()
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Запуск polling з graceful shutdown
            polling_task = asyncio.create_task(
                self.dp.start_polling(
                    self.bot,
                    skip_updates=True,
                    allowed_updates=["message", "callback_query", "inline_query"]
                )
            )
            
            shutdown_task = asyncio.create_task(self._shutdown_event.wait())
            
            # Очікування завершення
            done, pending = await asyncio.wait(
                [polling_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Скасування невиконаних задач
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"❌ Помилка під час роботи бота: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Коректне завершення роботи бота"""
        logger.info("🔄 Завершення роботи бота...")
        
        try:
            # Повідомлення адміністратору
            if self.bot and settings.ADMIN_ID:
                try:
                    await self.bot.send_message(
                        settings.ADMIN_ID,
                        f"{EMOJI.get('cross', '❌')} <b>БОТ ЗУПИНЕНО</b>\n\n"
                        f"{EMOJI.get('time', '⏰')} Час зупинки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                    )
                except:
                    pass
            
            # Зупинка планувальника
            if self.scheduler:
                await self.scheduler.stop()
                logger.info("⏰ Планувальник зупинено")
            
            # Закриття сесії бота
            if self.bot:
                await self.bot.session.close()
                logger.info("🤖 Сесія бота закрита")
        
        except Exception as e:
            logger.error(f"❌ Помилка при завершенні: {e}")
    
    async def run(self):
        """Основний метод запуску бота"""
        logger.info(f"{EMOJI.get('rocket', '🚀')} Запуск україномовного Telegram-бота")
        
        # Послідовна ініціалізація компонентів
        steps = [
            ("🔍 Валідація оточення", self.validate_environment),
            ("🤖 Створення бота", self.create_bot),
            ("💾 Ініціалізація БД", self.setup_database),
            ("🔧 Налаштування диспетчера", self.setup_dispatcher),
            ("⏰ Запуск планувальника", self.setup_scheduler),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"▶️ {step_name}...")
            try:
                result = await step_func()
                if result is False:
                    logger.error(f"❌ Невдалий крок: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ Помилка в кроці '{step_name}': {e}")
                return False
        
        logger.info(f"{EMOJI.get('party', '🎉')} Всі компоненти ініціалізовано!")
        
        # Запуск основного циклу
        await self.start_polling()
        return True

async def main():
    """Головна функція запуску"""
    
    # Вітальне повідомлення
    print("🧠😂🔥" * 20)
    print("🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ГЕЙМІФІКАЦІЄЮ 🚀")
    print("🧠😂🔥" * 20)
    print()
    
    # Завантаження налаштувань
    load_settings()
    
    # Налаштування логування
    setup_logging()
    
    # Запуск бота
    bot = UkrainianBot()
    try:
        success = await bot.run()
        if not success:
            logger.error("❌ Бот не зміг запуститися")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Перевірка версії Python
        if sys.version_info < (3, 8):
            print("❌ Потрібен Python 3.8 або новіший")
            sys.exit(1)
        
        # Запуск через asyncio
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 До побачення!")
    except Exception as e:
        print(f"\n❌ Критична помилка запуску: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)