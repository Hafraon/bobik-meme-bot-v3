#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Україномовний Telegram-бот - Спрощений запуск 🧠😂🔥
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
from aiohttp import web

# Імпорт налаштувань
from config.settings import settings, EMOJI

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Клас україномовного Telegram-бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.web_runner = None
        self.start_time = datetime.now()
        
    async def create_bot(self) -> Bot:
        """Створення екземпляру бота"""
        return Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )
    
    async def create_dispatcher(self) -> Dispatcher:
        """Створення диспетчера з базовими хендлерами"""
        dp = Dispatcher(storage=MemoryStorage())
        
        # Реєстрація базових хендлерів
        await self.register_basic_handlers(dp)
        
        return dp
    
    async def register_basic_handlers(self, dp: Dispatcher):
        """Реєстрація базових хендлерів"""
        from aiogram.filters import Command
        from aiogram.types import Message
        
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті!</b>\n\n"
                f"{EMOJI['rocket']} Бот успішно запущено!\n"
                f"{EMOJI['fire']} Використай /help для довідки\n"
                f"{EMOJI['test']} Команда /test для перевірки"
            )
            logger.info(f"🧠 Користувач {message.from_user.id} запустив бота")

        @dp.message(Command("help"))
        async def cmd_help(message: Message):
            await message.answer(
                f"{EMOJI['help']} <b>ДОВІДКА ПО БОТУ</b>\n\n"
                f"{EMOJI['star']} <b>Доступні команди:</b>\n"
                f"• /start - запуск бота\n"
                f"• /help - ця довідка\n"
                f"• /test - тест функціоналу\n"
                f"• /status - статус бота\n\n"
                f"{EMOJI['heart']} Більше функцій буде додано незабаром!"
            )

        @dp.message(Command("test"))
        async def cmd_test(message: Message):
            await message.answer(
                f"{EMOJI['fire']} <b>Тест пройдено успішно!</b>\n\n"
                f"{EMOJI['check']} Бот працює\n"
                f"{EMOJI['rocket']} Веб-сервер активний\n"
                f"{EMOJI['brain']} Всі системи в нормі!"
            )

        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            uptime = datetime.now() - self.start_time
            await message.answer(
                f"{EMOJI['stats']} <b>СТАТУС БОТА</b>\n\n"
                f"{EMOJI['fire']} Час роботи: {str(uptime).split('.')[0]}\n"
                f"{EMOJI['rocket']} Порт: {settings.PORT}\n"
                f"{EMOJI['check']} Статус: Активний\n"
                f"{EMOJI['brain']} Version: 2.0.0"
            )

        logger.info(f"{EMOJI['check']} Базові хендлери зареєстровано")
    
    async def create_web_server(self):
        """Створення простого веб-сервера"""
        async def health_check(request):
            uptime = datetime.now() - self.start_time
            return web.json_response({
                "status": "healthy",
                "bot": "running",
                "uptime_seconds": int(uptime.total_seconds()),
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            })
        
        async def root_handler(request):
            uptime = datetime.now() - self.start_time
            html = f"""
            <!DOCTYPE html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <title>{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} Україномовний Бот</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; margin: 0; padding: 20px; 
                        min-height: 100vh; display: flex; 
                        align-items: center; justify-content: center;
                    }}
                    .container {{ 
                        background: rgba(255,255,255,0.1); 
                        padding: 40px; border-radius: 20px; 
                        text-align: center; backdrop-filter: blur(10px);
                    }}
                    h1 {{ font-size: 3em; margin-bottom: 20px; }}
                    .status {{ margin: 20px 0; font-size: 1.2em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']}</h1>
                    <h2>Україномовний Telegram-бот</h2>
                    <div class="status">
                        <strong>{EMOJI['rocket']} Статус:</strong> Активний<br>
                        <strong>{EMOJI['fire']} Час роботи:</strong> {str(uptime).split('.')[0]}<br>
                        <strong>{EMOJI['check']} Порт:</strong> {settings.PORT}
                    </div>
                    <p><a href="/health" style="color: #FFD700;">/health</a> - Health check</p>
                    <p>{EMOJI['heart']} Зроблено для української мем-спільноти</p>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type='text/html')
        
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
        await site.start()
        
        logger.info(f"{EMOJI['rocket']} Веб-сервер запущено на порту {settings.PORT}")
        return runner
    
    async def on_startup(self):
        """Функція запуску бота"""
        try:
            logger.info(f"{EMOJI['rocket']} Запуск україномовного Telegram-бота...")
            
            # Перевірка підключення до Telegram
            me = await self.bot.get_me()
            logger.info(f"{EMOJI['brain']} Бот запущено: @{me.username} ({me.full_name})")
            
            # Повідомлення адміністратору про запуск
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['fire']} <b>Бот успішно запущено!</b>\n\n"
                    f"{EMOJI['brain']} <b>Ім'я:</b> @{me.username}\n"
                    f"{EMOJI['rocket']} <b>Режим:</b> Production\n"
                    f"{EMOJI['check']} <b>Статус:</b> Активний"
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
            
            # Повідомлення адміністратору
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['cross']} <b>Бот зупинено</b>\n{EMOJI['thinking']} До зустрічі!"
                )
            except Exception:
                pass
                
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
            
            # Запуск веб-сервера
            self.web_runner = await self.create_web_server()
            
            logger.info(f"{EMOJI['fire']} Запуск бота з веб-сервером...")
            
            # Створення задач для паралельного виконання
            polling_task = asyncio.create_task(
                self.dp.start_polling(
                    self.bot,
                    skip_updates=True,
                    allowed_updates=['message', 'callback_query']
                )
            )
            
            # Підтримання веб-сервера активним
            web_task = asyncio.create_task(self._keep_alive())
            
            # Очікування завершення будь-якої задачі
            done, pending = await asyncio.wait(
                [polling_task, web_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Скасування незавершених задач
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except KeyboardInterrupt:
            logger.info(f"{EMOJI['hand']} Отримано сигнал зупинки")
        except Exception as e:
            logger.error(f"{EMOJI['cross']} Фатальна помилка: {e}")
            raise
        finally:
            # Очищення ресурсів
            if self.web_runner:
                await self.web_runner.cleanup()
            if self.bot:
                await self.bot.session.close()
    
    async def _keep_alive(self):
        """Підтримання системи активною"""
        try:
            while True:
                await asyncio.sleep(60)  # Перевірка кожну хвилину
        except asyncio.CancelledError:
            logger.info(f"{EMOJI['thinking']} Завершення фонової задачі...")

async def main():
    """Точка входу"""
    try:
        # Валідація налаштувань
        if not settings.BOT_TOKEN:
            logger.error(f"{EMOJI['cross']} BOT_TOKEN не знайдено!")
            sys.exit(1)
        
        if not settings.ADMIN_ID:
            logger.error(f"{EMOJI['cross']} ADMIN_ID не знайдено!")
            sys.exit(1)
        
        logger.info(f"{EMOJI['star']} Налаштування валідовані успішно")
        logger.info(f"{EMOJI['rocket']} Порт: {settings.PORT}")
        logger.info(f"{EMOJI['brain']} Адмін: {settings.ADMIN_ID}")
        
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