#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Україномовний Telegram-бот - Головний файл запуску 🧠😂🔥
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Додавання поточної директорії до Python path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Імпорт налаштувань
from config.settings import settings, EMOJI

# Імпорт хендлерів
from handlers import register_handlers

# Імпорт middleware
from middlewares.auth import AuthMiddleware, AntiSpamMiddleware, LoggingMiddleware

# Імпорт сервісів
from services.scheduler import SchedulerService

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8') if Path('logs').exists() else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Клас україномовного Telegram-бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler = None
        
    async def create_bot(self) -> Bot:
        """Створення екземпляру бота"""
        return Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )
    
    async def create_dispatcher(self) -> Dispatcher:
        """Створення диспетчера з middleware та хендлерами"""
        # Створення диспетчера з пам'яттю
        dp = Dispatcher(storage=MemoryStorage())
        
        # Реєстрація middleware
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        dp.message.middleware(AntiSpamMiddleware(rate_limit=3))
        dp.callback_query.middleware(AntiSpamMiddleware(rate_limit=5))
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
        
        # Реєстрація всіх хендлерів
        register_handlers(dp)
        
        return dp
    
    async def on_startup(self):
        """Функція запуску бота"""
        try:
            logger.info(f"{EMOJI['rocket']} Запуск україномовного Telegram-бота...")
            
            # Ініціалізація бази даних
            try:
                from database.database import init_db
                await init_db()
                logger.info(f"{EMOJI['check']} База даних ініціалізована")
            except Exception as e:
                logger.error(f"{EMOJI['cross']} Помилка ініціалізації БД: {e}")
                # Продовжуємо без БД для налагодження
            
            # Перевірка підключення до Telegram
            me = await self.bot.get_me()
            logger.info(f"{EMOJI['brain']} Бот запущено: @{me.username} ({me.full_name})")
            
            # Запуск планувальника
            try:
                self.scheduler = SchedulerService(self.bot)
                await self.scheduler.start()
                logger.info(f"{EMOJI['calendar']} Планувальник запущено")
            except Exception as e:
                logger.warning(f"{EMOJI['warning']} Планувальник не запущено: {e}")
            
            # Повідомлення адміністратору про запуск
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['fire']} <b>Бот успішно запущено!</b>\n\n"
                    f"{EMOJI['brain']} <b>Ім'я:</b> @{me.username}\n"
                    f"{EMOJI['rocket']} <b>Режим:</b> Production\n"
                    f"{EMOJI['calendar']} <b>Час:</b> {asyncio.get_event_loop().time()}"
                )
            except Exception as e:
                logger.warning(f"Не вдалося повідомити адміністратора: {e}")
                
        except Exception as e:
            logger.error(f"{EMOJI['cross']} Критична помилка запуску: {e}")
            raise
    
    async def on_shutdown(self):
        """Функція зупинки бота"""
        try:
            logger.info(f"{EMOJI['thinking']} Зупинка бота...")
            
            # Зупинка планувальника
            if self.scheduler:
                await self.scheduler.stop()
                logger.info(f"{EMOJI['check']} Планувальник зупинено")
            
            # Повідомлення адміністратору
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['cross']} <b>Бот зупинено</b>\n\n"
                    f"{EMOJI['thinking']} До зустрічі!"
                )
            except Exception:
                pass
                
            # Закриття сесії бота
            await self.bot.session.close()
            logger.info(f"{EMOJI['check']} Бот зупинено")
            
        except Exception as e:
            logger.error(f"Помилка зупинки бота: {e}")
    
    async def run(self):
        """Головна функція запуску"""
        try:
            # Створення бота та диспетчера
            self.bot = await self.create_bot()
            self.dp = await self.create_dispatcher()
            
            # Реєстрація startup/shutdown хендлерів
            self.dp.startup.register(self.on_startup)
            self.dp.shutdown.register(self.on_shutdown)
            
            # Запуск веб-сервера для Railway
            try:
                from web_server import BotWebServer
                web_server = BotWebServer(self.bot)
                web_runner = await web_server.start_server()
            except ImportError:
                # Якщо веб-сервер недоступний, створюємо простий
                web_runner = await self._create_simple_web_server()
            except Exception as e:
                logger.warning(f"Веб-сервер не запущено: {e}")
                web_runner = None
            
            logger.info(f"{EMOJI['fire']} Запуск бота з веб-сервером...")
            
            # Створення задач для паралельного виконання
            tasks = [
                asyncio.create_task(self.dp.start_polling(
                    self.bot,
                    skip_updates=True,
                    allowed_updates=['message', 'callback_query']
                )),
                asyncio.create_task(self._keep_web_server_alive())
            ]
            
            # Очікування завершення будь-якої задачі
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # Скасування незавершених задач
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Очищення веб-сервера
            if web_runner:
                await web_runner.cleanup()
            
        except KeyboardInterrupt:
            logger.info(f"{EMOJI['hand']} Отримано сигнал зупинки")
        except Exception as e:
            logger.error(f"{EMOJI['cross']} Фатальна помилка: {e}")
            raise
        finally:
            if self.bot:
                await self.bot.session.close()
    
    async def _create_simple_web_server(self):
        """Створення простого веб-сервера"""
        try:
            from aiohttp import web
            
            async def health_check(request):
                return web.json_response({
                    "status": "healthy",
                    "bot": "running", 
                    "timestamp": datetime.now().isoformat()
                })
            
            app = web.Application()
            app.router.add_get('/health', health_check)
            app.router.add_get('/', lambda req: web.Response(text="🧠😂🔥 Україномовний бот працює!"))
            
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
            await site.start()
            
            logger.info(f"{EMOJI['rocket']} Простий веб-сервер запущено на порту {settings.PORT}")
            return runner
            
        except Exception as e:
            logger.error(f"Помилка запуску простого веб-сервера: {e}")
            return None
    
    async def _keep_web_server_alive(self):
        """Підтримання веб-сервера активним"""
        try:
            while True:
                await asyncio.sleep(60)  # Перевірка кожну хвилину
        except asyncio.CancelledError:
            logger.info(f"{EMOJI['thinking']} Веб-сервер зупиняється...")

async def main():
    """Точка входу"""
    try:
        # Валідація налаштувань
        if not settings.BOT_TOKEN:
            logger.error(f"{EMOJI['cross']} BOT_TOKEN не знайдено в змінних середовища!")
            sys.exit(1)
        
        if not settings.ADMIN_ID:
            logger.error(f"{EMOJI['cross']} ADMIN_ID не знайдено в змінних середовища!")
            sys.exit(1)
        
        logger.info(f"{EMOJI['star']} Налаштування валідовані успішно")
        
        # Створення та запуск бота
        bot = UkrainianBot()
        await bot.run()
        
    except Exception as e:
        logger.error(f"{EMOJI['cross']} Критична помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Для Windows сумісності
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Запуск
    asyncio.run(main())