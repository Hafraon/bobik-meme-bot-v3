#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ПОВНІСТЮ ВИПРАВЛЕНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ 🚀

ІНТЕГРАЦІЯ ВСІХ КОМПОНЕНТІВ:
✅ Config загрузка з fallback
✅ Database ініціалізація
✅ Handlers реєстрація з fallback
✅ Services автоматизації
✅ Правильний entry point для Railway
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import traceback
import signal

# Telegram Bot API
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, BotCommand

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class AutomatedUkrainianTelegramBot:
    """Повністю автоматизований україномовний Telegram бот"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.startup_time = datetime.now()
        self.db_available = False
        self.automation_active = False
        self.scheduler = None
        self.broadcast_system = None
        self.shutdown_event = asyncio.Event()
        
        # Системні змінні
        self.bot_token = os.getenv("BOT_TOKEN")
        self.admin_id = int(os.getenv("ADMIN_ID", "603047391"))
        
        if not self.bot_token:
            logger.error("❌ BOT_TOKEN не знайдено!")
            raise ValueError("BOT_TOKEN обов'язковий для роботи бота")
        
        logger.info("🤖 AutomatedUkrainianTelegramBot ініціалізовано")

    def is_admin(self, user_id: int) -> bool:
        """Перевірка чи користувач є адміністратором"""
        try:
            from config.settings import ALL_ADMIN_IDS
            return user_id in ALL_ADMIN_IDS
        except ImportError:
            return user_id == self.admin_id

    async def load_config(self) -> Dict[str, Any]:
        """Завантаження конфігурації з fallback"""
        logger.info("🔧 Завантаження конфігурації...")
        
        try:
            from config.settings import (
                BOT_TOKEN, ADMIN_ID, DATABASE_URL, DEBUG,
                WEBHOOK_URL, WEBHOOK_PORT
            )
            
            config = {
                'bot_token': BOT_TOKEN,
                'admin_id': ADMIN_ID,
                'database_url': DATABASE_URL,
                'debug': DEBUG,
                'webhook_url': WEBHOOK_URL,
                'webhook_port': WEBHOOK_PORT
            }
            
            logger.info("✅ Конфігурація завантажена з config.settings")
            return config
            
        except ImportError as e:
            logger.warning(f"⚠️ Fallback конфігурація: {e}")
            
            # Fallback конфігурація з environment variables
            config = {
                'bot_token': os.getenv('BOT_TOKEN'),
                'admin_id': int(os.getenv('ADMIN_ID', 0)),
                'database_url': os.getenv('DATABASE_URL', 'sqlite:///bot.db'),
                'debug': os.getenv('DEBUG', 'False').lower() == 'true',
                'webhook_url': os.getenv('WEBHOOK_URL'),
                'webhook_port': int(os.getenv('PORT', 8000))
            }
            
            logger.info("✅ Fallback конфігурація завантажена")
            return config

    async def initialize_bot(self, config: Dict[str, Any]) -> bool:
        """Ініціалізація бота"""
        logger.info("🤖 Ініціалізація бота...")
        
        try:
            self.bot = Bot(
                token=config['bot_token'],
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            # Перевірка з'єднання
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Бот створено: @{bot_info.username} (ID: {bot_info.id})")
            
            # Створення диспетчера
            self.dp = Dispatcher()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення бота: {e}")
            return False

    async def initialize_database(self) -> bool:
        """Ініціалізація бази даних"""
        logger.info("💾 Ініціалізація бази даних...")
        
        try:
            # Спроба використання повнофункціональної БД
            from database import init_db, get_db_session
            
            success = await init_db()
            if success:
                logger.info("✅ База даних ініціалізована успішно")
                self.db_available = True
                return True
            else:
                logger.warning("⚠️ БД не ініціалізована, працюємо без неї")
                self.db_available = False
                return True
                
        except ImportError as e:
            logger.warning(f"⚠️ БД модулі не знайдені: {e}")
            self.db_available = False
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            self.db_available = False
            return True  # Продовжуємо роботу без БД

    async def register_handlers(self) -> bool:
        """Реєстрація всіх handlers"""
        logger.info("🎮 Реєстрація handlers...")
        
        try:
            from handlers import register_handlers
            register_handlers(self.dp)
            logger.info("✅ Handlers зареєстровані успішно")
            return True
            
        except ImportError as e:
            logger.error(f"❌ Помилка імпорту handlers: {e}")
            # Реєструємо мінімальні fallback handlers
            await self.register_fallback_handlers()
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка реєстрації handlers: {e}")
            await self.register_fallback_handlers()
            return True

    async def register_fallback_handlers(self):
        """Мінімальні fallback handlers"""
        logger.info("🆘 Реєстрація fallback handlers...")
        
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                "🧠😂🔥 <b>Україномовний бот запущено!</b>\n\n"
                "🔧 <i>Працює в базовому режимі</i>\n\n"
                "📋 <b>Доступні команди:</b>\n"
                "• /start - це повідомлення\n"
                "• /help - довідка\n"
                "• /status - статус бота\n\n"
                "✨ Для повного функціоналу налаштуйте БД та handlers"
            )
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: Message):
            await message.answer(
                "📚 <b>Довідка по боту</b>\n\n"
                "🤖 Це україномовний Telegram бот\n"
                "🔧 Зараз працює в базовому режимі\n\n"
                "💡 Адміністратор може налаштувати:\n"
                "• База даних для збереження\n"
                "• Додаткові команди та функції\n"
                "• Автоматизація та планувальник"
            )
        
        @self.dp.message(Command("status"))
        async def cmd_status(message: Message):
            if not self.is_admin(message.from_user.id):
                await message.answer("❌ Тільки для адміністраторів")
                return
            
            uptime = datetime.now() - self.startup_time
            status_text = (
                f"📊 <b>Статус бота</b>\n\n"
                f"⏰ Uptime: {uptime.days}д {uptime.seconds//3600}г {(uptime.seconds//60)%60}м\n"
                f"💾 БД: {'✅ Активна' if self.db_available else '❌ Недоступна'}\n"
                f"🤖 Автоматизація: {'✅ Активна' if self.automation_active else '❌ Неактивна'}\n"
                f"👑 Адмін: {message.from_user.id}\n"
                f"🚀 Режим: Fallback"
            )
            await message.answer(status_text)
        
        logger.info("✅ Fallback handlers зареєстровано")

    async def initialize_automation(self) -> bool:
        """Ініціалізація системи автоматизації"""
        logger.info("🤖 Ініціалізація автоматизації...")
        
        try:
            # Спроба завантаження планувальника
            from services.automated_scheduler import create_automated_scheduler
            
            self.scheduler = await create_automated_scheduler(self.bot)
            if self.scheduler:
                logger.info("✅ Планувальник створено")
                self.automation_active = True
            else:
                logger.warning("⚠️ Планувальник не створено")
                
        except ImportError as e:
            logger.warning(f"⚠️ Планувальник недоступний: {e}")
            
        try:
            # Спроба завантаження системи розсилок
            from services.broadcast_system import create_broadcast_system
            
            self.broadcast_system = await create_broadcast_system(self.bot)
            if self.broadcast_system:
                logger.info("✅ Система розсилок створена")
                
        except ImportError as e:
            logger.warning(f"⚠️ Система розсилок недоступна: {e}")
            
        return True

    async def setup_bot_commands(self):
        """Налаштування меню команд бота"""
        logger.info("📋 Налаштування меню команд...")
        
        commands = [
            BotCommand(command="start", description="🚀 Почати роботу з ботом"),
            BotCommand(command="help", description="📚 Довідка та інструкції"),
            BotCommand(command="meme", description="😂 Отримати мем"),
            BotCommand(command="anekdot", description="🎭 Отримати анекдот"),
            BotCommand(command="profile", description="👤 Мій профіль та бали"),
            BotCommand(command="top", description="🏆 Рейтинг користувачів"),
            BotCommand(command="duel", description="⚔️ Почати дуель"),
            BotCommand(command="submit", description="📝 Подати свій контент"),
        ]
        
        try:
            await self.bot.set_my_commands(commands)
            logger.info("✅ Меню команд налаштовано")
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося налаштувати меню: {e}")

    def setup_signal_handlers(self):
        """Налаштування обробників сигналів для graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Отримано сигнал {signum}, ініціалізація shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logger.info("✅ Signal handlers налаштовано")

    async def cleanup(self):
        """Очищення ресурсів"""
        logger.info("🧹 Початок cleanup...")
        
        try:
            # Зупинка планувальника
            if self.scheduler and hasattr(self.scheduler, 'stop'):
                await self.scheduler.stop()
                logger.info("✅ Планувальник зупинено")
            
            # Закриття сесії бота
            if self.bot and hasattr(self.bot, 'session'):
                await self.bot.session.close()
                logger.info("✅ Bot session закрито")
                
        except Exception as e:
            logger.error(f"⚠️ Помилка cleanup: {e}")
        
        logger.info("✅ Cleanup завершено")

    async def run(self):
        """Основний метод запуску бота"""
        logger.info("🚀 Запуск AutomatedUkrainianTelegramBot...")
        
        try:
            # Налаштування signal handlers
            self.setup_signal_handlers()
            
            # 1. Завантаження конфігурації
            config = await self.load_config()
            
            # 2. Ініціалізація бота
            if not await self.initialize_bot(config):
                raise Exception("Не вдалося ініціалізувати бота")
            
            # 3. Ініціалізація БД
            await self.initialize_database()
            
            # 4. Реєстрація handlers
            await self.register_handlers()
            
            # 5. Ініціалізація автоматизації
            await self.initialize_automation()
            
            # 6. Налаштування команд
            await self.setup_bot_commands()
            
            # 7. Інформація про успішний запуск
            logger.info("🎯 Бот повністю ініціалізований!")
            logger.info(f"💾 БД: {'✅' if self.db_available else '❌'}")
            logger.info(f"🤖 Автоматизація: {'✅' if self.automation_active else '❌'}")
            
            # 8. Запуск планувальника
            if self.scheduler and hasattr(self.scheduler, 'start'):
                await self.scheduler.start()
                logger.info("🚀 Планувальник запущено")
            
            # 9. Запуск polling з graceful shutdown
            logger.info("🔄 Запуск polling...")
            
            # Створюємо задачу для моніторингу shutdown
            shutdown_task = asyncio.create_task(self.shutdown_event.wait())
            polling_task = asyncio.create_task(
                self.dp.start_polling(self.bot, skip_updates=True)
            )
            
            # Чекаємо завершення одної з задач
            done, pending = await asyncio.wait(
                [shutdown_task, polling_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Скасовуємо незавершені задачі
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            logger.info("🛑 Polling зупинено")
            
        except Exception as e:
            logger.error(f"💥 Критична помилка: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            await self.cleanup()

    async def main(self):
        """Entry point функція для Railway launcher"""
        try:
            await self.run()
        except KeyboardInterrupt:
            logger.info("🛑 Зупинка через Ctrl+C")
        except Exception as e:
            logger.error(f"💥 Неочікувана помилка: {e}")
            raise

# ===== ФУНКЦІЇ ДЛЯ RAILWAY LAUNCHER =====

async def main():
    """Головна функція для запуску Railway launcher"""
    logger.info("🎯 Railway launcher - створення bot instance...")
    
    try:
        bot_instance = AutomatedUkrainianTelegramBot()
        await bot_instance.main()
    except Exception as e:
        logger.error(f"💥 Помилка запуску: {e}")
        raise

# ===== FALLBACK ФУНКЦІЇ =====

async def run_fallback_bot():
    """🆘 Fallback бот якщо основний не працює"""
    logger.info("🆘 Запуск fallback бота...")
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error("❌ BOT_TOKEN не знайдено!")
            return False
        
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer("🧠😂🔥 Fallback режим - бот працює!")
        
        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            await message.answer("✅ Статус: Fallback режим активний")
        
        logger.info("✅ Fallback бот готовий")
        await dp.start_polling(bot, skip_updates=True)
        return True
        
    except Exception as e:
        logger.error(f"💥 Критична помилка fallback бота: {e}")
        return False

# ===== ENTRY POINT =====

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Зупинка через Ctrl+C")
    except Exception as e:
        logger.error(f"💥 Неочікувана помилка: {e}")
        sys.exit(1)