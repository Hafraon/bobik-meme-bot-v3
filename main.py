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
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Наші модулі
from config.settings import settings, EMOJI
from database.database import init_db
from handlers import register_handlers
from middlewares.auth import AuthMiddleware, AntiSpamMiddleware, LoggingMiddleware
from services.scheduler import SchedulerService

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8') if Path('logs').exists() else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Головний клас україномовного бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler = None
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
    
    async def setup_middleware(self):
        """Налаштування middleware"""
        try:
            # Логування активності
            self.dp.message.middleware(LoggingMiddleware())
            self.dp.callback_query.middleware(LoggingMiddleware())
            
            # Аутентифікація та оновлення активності
            self.dp.message.middleware(AuthMiddleware())
            self.dp.callback_query.middleware(AuthMiddleware())
            
            # Захист від спаму
            self.dp.message.middleware(AntiSpamMiddleware(rate_limit=3))
            self.dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
            
            logger.info("🛡️ Middleware налаштовано")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка налаштування middleware: {e}")
            return False
    
    async def setup_handlers(self):
        """Реєстрація всіх хендлерів"""
        try:
            register_handlers(self.dp)
            logger.info("🎯 Хендлери зареєстровано")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка реєстрації хендлерів: {e}")
            return False
    
    async def setup_database(self):
        """Ініціалізація бази даних"""
        try:
            await init_db()
            logger.info("💾 База даних ініціалізована")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            return False
    
    async def setup_scheduler(self):
        """Налаштування планувальника задач"""
        try:
            self.scheduler = SchedulerService(self.bot)
            await self.scheduler.start()
            logger.info("⏰ Планувальник запущено")
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
                    "version": "1.0.0"
                })
            
            # Webhook endpoint (якщо потрібно)
            async def webhook_handler(request):
                return web.Response(text="Webhook endpoint")
            
            # Додавання маршрутів
            self.app.router.add_get('/health', health_check)
            self.app.router.add_post('/webhook', webhook_handler)
            
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
                            <p>📊 <a href="/health">Health Check</a></p>
                        </body>
                    </html>
                    """,
                    content_type='text/html'
                )
            
            self.app.router.add_get('/', index)
            
            logger.info("🌐 Веб-додаток створено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення веб-додатку: {e}")
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
    
    async def shutdown(self):
        """Коректне завершення роботи"""
        logger.info("🛑 Завершення роботи бота...")
        
        try:
            if self.scheduler:
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
            logger.info(f"   💾 База даних: {settings.DATABASE_URL.split('@')[0]}@***")
            logger.info(f"   🧠 OpenAI: {'✅ Налаштовано' if settings.OPENAI_API_KEY else '❌ Відсутнє'}")
            
            # Поетапна ініціалізація
            steps = [
                ("🤖 Створення бота", self.create_bot()),
                ("💾 Ініціалізація БД", self.setup_database()),
                ("🛡️ Налаштування middleware", self.setup_middleware()),
                ("🎯 Реєстрація хендлерів", self.setup_handlers()),
                ("⏰ Запуск планувальника", self.setup_scheduler()),
                ("🌐 Створення веб-додатку", self.create_webapp()),
                ("🌐 Запуск веб-сервера", self.start_webapp())
            ]
            
            for step_name, step_coro in steps:
                logger.info(f"▶️ {step_name}...")
                result = await step_coro
                if not result:
                    raise Exception(f"Помилка на етапі: {step_name}")
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
                    f"💾 <b>БД:</b> ✅ Підключена\n"
                    f"⏰ <b>Планувальник:</b> ✅ Активний\n"
                    f"🧠 <b>AI:</b> {'✅ Активний' if settings.OPENAI_API_KEY else '❌ Вимкнений'}\n\n"
                    f"📊 /admin_stats - статистика\n"
                    f"🛠️ /moderate - модерація"
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
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Запуск
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Програма завершена")