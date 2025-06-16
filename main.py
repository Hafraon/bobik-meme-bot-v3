#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Україномовний Telegram-бот - Головний файл запуску 🧠😂🔥
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Додаємо поточну папку до Python path
sys.path.insert(0, str(Path(__file__).parent))

# Aiogram imports
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web

# Наші модулі (під твою плоску структуру)
try:
    from settings import settings, EMOJI  # Замість config.settings
except ImportError:
    # Fallback налаштування якщо файл відсутній
    import os
    class FallbackSettings:
        BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    settings = FallbackSettings()
    EMOJI = {"brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", "check": "✅", "cross": "❌"}

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8') if Path.cwd().is_dir() else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Головний клас україномовного бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.app = None
        
    async def create_bot(self):
        """Створення бота та диспетчера"""
        try:
            # Створення сесії з налаштуваннями
            session = AiohttpSession()
            
            # Створення бота
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                session=session,
                parse_mode=ParseMode.HTML
            )
            
            # Створення диспетчера
            self.dp = Dispatcher()
            
            logger.info(f"🤖 Бот створено успішно!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення бота: {e}")
            return False
    
    async def setup_handlers(self):
        """Реєстрація всіх хендлерів"""
        try:
            # Імпортуємо хендлери які існують
            handlers_registered = 0
            
            # Спроба імпортувати basic_commands
            try:
                from basic_commands import register_basic_handlers
                register_basic_handlers(self.dp)
                handlers_registered += 1
                logger.info("✅ Основні команди зареєстровано")
            except ImportError:
                logger.warning("⚠️ basic_commands не знайдено")
            
            # Спроба імпортувати content_handlers
            try:
                from content_handlers import register_content_handlers
                register_content_handlers(self.dp)
                handlers_registered += 1
                logger.info("✅ Контент хендлери зареєстровано")
            except ImportError:
                logger.warning("⚠️ content_handlers не знайдено")
            
            # Спроба імпортувати gamification_handlers
            try:
                from gamification_handlers import register_gamification_handlers
                register_gamification_handlers(self.dp)
                handlers_registered += 1
                logger.info("✅ Гейміфікація зареєстровано")
            except ImportError:
                logger.warning("⚠️ gamification_handlers не знайдено")
            
            # Спроба імпортувати moderation_handlers
            try:
                from moderation_handlers import register_moderation_handlers
                register_moderation_handlers(self.dp)
                handlers_registered += 1
                logger.info("✅ Модерація зареєстровано")
            except ImportError:
                logger.warning("⚠️ moderation_handlers не знайдено")
            
            # Спроба імпортувати duel_handlers
            try:
                from duel_handlers import register_duel_handlers
                register_duel_handlers(self.dp)
                handlers_registered += 1
                logger.info("✅ Дуелі зареєстровано")
            except ImportError:
                logger.warning("⚠️ duel_handlers не знайдено")
            
            # Якщо нічого не зареєстровано, додаємо базові хендлери
            if handlers_registered == 0:
                logger.warning("⚠️ Використовуємо fallback хендлери")
                self.register_fallback_handlers()
                handlers_registered = 1
            
            logger.info(f"🎯 Зареєстровано {handlers_registered} груп хендлерів")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка реєстрації хендлерів: {e}")
            return False
    
    def register_fallback_handlers(self):
        """Базові хендлери як fallback"""
        from aiogram import F
        from aiogram.filters import Command
        from aiogram.types import Message
        
        @self.dp.message(Command("start"))
        async def cmd_start_fallback(message: Message):
            await message.answer(
                f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті!</b>\n\n"
                f"{EMOJI['star']} Бот запущено у базовому режимі\n"
                f"{EMOJI['check']} Основні функції активні\n"
                f"{EMOJI['fire']} Адмін: {settings.ADMIN_ID}\n\n"
                f"Доступні команди:\n"
                f"• /start - запуск\n"
                f"• /help - допомога\n"
                f"• /status - статус бота"
            )
        
        @self.dp.message(Command("help"))
        async def cmd_help_fallback(message: Message):
            await message.answer(
                f"{EMOJI['star']} <b>Допомога</b>\n\n"
                f"Базові команди:\n"
                f"• /start - запуск бота\n"
                f"• /help - ця довідка\n"
                f"• /status - статус\n\n"
                f"{EMOJI['fire']} Бот працює в базовому режимі"
            )
        
        @self.dp.message(Command("status"))
        async def cmd_status_fallback(message: Message):
            await message.answer(
                f"{EMOJI['check']} <b>Статус бота</b>\n\n"
                f"🤖 Бот: активний\n"
                f"👥 Адмін: {settings.ADMIN_ID}\n"
                f"💾 БД: {settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else 'Local'}@***\n"
                f"🧠 AI: {'✅' if settings.OPENAI_API_KEY else '❌'}\n"
                f"🔥 Режим: базовий"
            )
        
        @self.dp.message(F.text)
        async def fallback_handler(message: Message):
            if not message.text.startswith('/'):
                await message.answer(
                    f"{EMOJI['star']} Використай /help для допомоги"
                )
    
    async def setup_database(self):
        """Ініціалізація бази даних"""
        try:
            # Спроба ініціалізувати БД якщо є модуль
            try:
                from database import init_db  # Замість database.database
                await init_db()
                logger.info("💾 База даних ініціалізована")
            except ImportError:
                logger.warning("⚠️ Модуль database не знайдено, пропускаємо ініціалізацію БД")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            return False
    
    async def setup_scheduler(self):
        """Налаштування планувальника задач"""
        try:
            # Спроба запустити планувальник якщо є модуль
            try:
                from scheduler import SchedulerService  # Замість services.scheduler
                self.scheduler = SchedulerService(self.bot)
                await self.scheduler.start()
                logger.info("⏰ Планувальник запущено")
            except ImportError:
                logger.warning("⚠️ Модуль scheduler не знайдено, пропускаємо планувальник")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка запуску планувальника: {e}")
            return False
    
    async def create_webapp(self):
        """Створення веб-додатку для Railway"""
        try:
            # Створення aiohttp додатку
            self.app = web.Application()
            
            # Health check endpoint
            async def health_check(request):
                return web.json_response({
                    "status": "healthy",
                    "bot": "ukrainian_telegram_bot",
                    "version": "1.0.0",
                    "admin_id": settings.ADMIN_ID
                })
            
            # Статична сторінка
            async def index(request):
                return web.Response(
                    text=f"""
                    <html>
                        <head><title>🧠😂🔥 Україномовний Telegram-бот</title></head>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1>🧠😂🔥 Україномовний Telegram-бот</h1>
                            <p>✅ Бот активний та працює!</p>
                            <p>🤖 Версія: 1.0.0</p>
                            <p>👥 Адмін: {settings.ADMIN_ID}</p>
                            <p>📊 <a href="/health">Health Check</a></p>
                        </body>
                    </html>
                    """,
                    content_type='text/html'
                )
            
            self.app.router.add_get('/', index)
            self.app.router.add_get('/health', health_check)
            
            logger.info("🌐 Веб-додаток створено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення веб-додатку: {e}")
            return False
    
    async def start_webapp(self):
        """Запуск веб-сервера для Railway"""
        try:
            port = int(os.getenv("PORT", 8000))
            
            # Запуск веб-сервера у фоновому режимі
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            logger.info(f"🌐 Веб-сервер запущено на порту {port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка запуску веб-сервера: {e}")
            return False
    
    async def start_polling(self):
        """Запуск бота в режимі polling"""
        try:
            logger.info(f"🚀 Запуск бота в режимі polling...")
            
            # Видалення webhook якщо був
            await self.bot.delete_webhook(drop_pending_updates=True)
            
            # Запуск polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
        except Exception as e:
            logger.error(f"❌ Помилка polling: {e}")
            raise
    
    async def shutdown(self):
        """Коректне завершення роботи"""
        logger.info("🛑 Завершення роботи бота...")
        
        try:
            if hasattr(self, 'scheduler') and self.scheduler:
                await self.scheduler.stop()
                logger.info("⏰ Планувальник зупинено")
            
            if self.bot:
                await self.bot.session.close()
                logger.info("🤖 Сесія бота закрита")
            
            logger.info("✅ Бот завершено коректно")
            
        except Exception as e:
            logger.error(f"❌ Помилка завершення: {e}")
    
    async def run(self):
        """Головний метод запуску"""
        logger.info("🧠😂🔥 ЗАПУСК УКРАЇНОМОВНОГО TELEGRAM-БОТА 🧠😂🔥")
        
        try:
            # Перевірка налаштувань
            if not settings.BOT_TOKEN:
                raise ValueError("BOT_TOKEN не налаштовано!")
            if not settings.ADMIN_ID:
                raise ValueError("ADMIN_ID не налаштовано!")
            
            logger.info(f"🔧 Налаштування:")
            logger.info(f"   📱 Адмін ID: {settings.ADMIN_ID}")
            logger.info(f"   💾 База даних: {settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else 'Local'}@***")
            logger.info(f"   🧠 OpenAI: {'✅ Налаштовано' if getattr(settings, 'OPENAI_API_KEY', None) else '❌ Відсутнє'}")
            
            # Поетапна ініціалізація
            steps = [
                ("🤖 Створення бота", self.create_bot()),
                ("💾 Ініціалізація БД", self.setup_database()),
                ("🎯 Реєстрація хендлерів", self.setup_handlers()),
                ("⏰ Запуск планувальника", self.setup_scheduler()),
                ("🌐 Створення веб-додатку", self.create_webapp()),
                ("🌐 Запуск веб-сервера", self.start_webapp())
            ]
            
            for step_name, step_coro in steps:
                logger.info(f"▶️ {step_name}...")
                result = await step_coro
                if not result:
                    logger.warning(f"⚠️ {step_name} - пропущено через помилку")
                else:
                    logger.info(f"✅ {step_name} - завершено")
            
            # Отримання інформації про бота
            bot_info = await self.bot.get_me()
            logger.info(f"🎉 Бот @{bot_info.username} готовий до роботи!")
            
            # Повідомлення адміністратору про запуск
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"🚀 <b>Бот запущено успішно!</b>\n\n"
                    f"🤖 <b>Бот:</b> @{bot_info.username}\n"
                    f"💾 <b>БД:</b> {'✅ Підключена' if hasattr(self, 'database_ok') else '⚠️ Базовий режим'}\n"
                    f"⏰ <b>Планувальник:</b> {'✅ Активний' if hasattr(self, 'scheduler') else '⚠️ Вимкнений'}\n"
                    f"🧠 <b>AI:</b> {'✅ Активний' if getattr(settings, 'OPENAI_API_KEY', None) else '❌ Вимкнений'}\n\n"
                    f"📊 Доступні команди:\n"
                    f"• /start - перевірка роботи\n"
                    f"• /help - довідка\n"
                    f"• /status - статус бота"
                )
            except Exception as e:
                logger.warning(f"Не вдалося повідомити адміністратора: {e}")
            
            # Запуск основного циклу
            await self.start_polling()
            
        except Exception as e:
            logger.error(f"💥 Критична помилка: {e}")
            raise
        finally:
            await self.shutdown()

def setup_signal_handlers(bot_instance):
    """Налаштування обробників сигналів"""
    def signal_handler(signum, frame):
        logger.info(f"🛑 Отримано сигнал {signum}")
        # Створюємо задачу на завершення
        loop = asyncio.get_event_loop()
        loop.create_task(bot_instance.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Головна функція"""
    try:
        # Створення екземпляру бота
        bot_instance = UkrainianBot()
        
        # Налаштування обробників сигналів
        setup_signal_handlers(bot_instance)
        
        # Запуск бота
        await bot_instance.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Фатальна помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Створення директорій якщо не існують
    try:
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
    except:
        pass  # Ігноруємо помилки створення директорій
    
    # Запуск
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Програма завершена")
    except Exception as e:
        print(f"💥 Критична помилка запуску: {e}")
        sys.exit(1)