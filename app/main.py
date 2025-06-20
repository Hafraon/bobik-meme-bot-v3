#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ПОВНОЮ АВТОМАТИЗАЦІЄЮ 🤖

ВИПРАВЛЕННЯ:
✅ Додано правильні typing імпорти
✅ Виправлено aiohttp session cleanup
✅ Покращена обробка БД помилок
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any  # ✅ ДОДАНО: List з typing
import signal

# Telegram Bot API
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class AutomatedUkrainianTelegramBot:
    """Україномовний бот з повною автоматизацією"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
        self.db_available = False
        self.handlers_status = {}
        self.shutdown_event = asyncio.Event()
        
        # Системи автоматизації
        self.scheduler = None
        self.broadcast_system = None
        self.automation_active = False
        
    def is_admin(self, user_id: int) -> bool:
        """Перевірка чи користувач є адміністратором"""
        try:
            from config.settings import settings
            admin_ids = [settings.ADMIN_ID]
            if hasattr(settings, 'ADDITIONAL_ADMINS'):
                admin_ids.extend(settings.ADDITIONAL_ADMINS)
            return user_id in admin_ids
        except ImportError:
            admin_id = int(os.getenv('ADMIN_ID', 0))
            return user_id == admin_id

    async def load_settings(self):
        """Завантаження налаштувань"""
        logger.info("🔍 Завантаження налаштувань...")
        
        try:
            from config.settings import settings
            logger.info("✅ Settings loaded from config.settings")
            return settings
        except ImportError:
            logger.warning("⚠️ Using fallback settings from environment")
            import types
            fallback_settings = types.SimpleNamespace()
            fallback_settings.BOT_TOKEN = os.getenv('BOT_TOKEN')
            fallback_settings.ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
            fallback_settings.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
            fallback_settings.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
            return fallback_settings

    async def initialize_bot(self, settings):
        """Ініціалізація бота"""
        logger.info("🤖 Створення бота...")
        
        if not settings.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не встановлено!")
            return False
        
        try:
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            # Перевірка з'єднання
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Bot created: @{bot_info.username}")
            
            self.dp = Dispatcher()
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot creation failed: {e}")
            return False

    async def initialize_database(self):
        """Ініціалізація бази даних"""
        logger.info("💾 Ініціалізація БД...")
        
        try:
            # Спроба імпорту database модуля
            import database
            logger.info("✅ Database module imported successfully")
            
            # Перевірка доступності основних функцій
            required_functions = ['init_db', 'get_db_session']
            missing_functions = []
            
            for func_name in required_functions:
                if not hasattr(database, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                logger.warning(f"⚠️ Missing database functions: {missing_functions}")
                return False
            
            # Ініціалізація БД
            if hasattr(database, 'init_db'):
                db_result = await database.init_db()
                if db_result:
                    logger.info("✅ Database initialized successfully")
                    self.db_available = True
                    return True
                else:
                    logger.warning("⚠️ Database initialization returned False")
                    return False
            else:
                logger.warning("⚠️ init_db function not found")
                return False
                
        except ImportError as e:
            logger.warning(f"⚠️ Database module not available: {e}")
            logger.warning("⚠️ Working without full database support")
            return False
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            return False

    async def initialize_automation(self):
        """Ініціалізація системи автоматизації"""
        logger.info("🤖 Ініціалізація системи автоматизації...")
        
        try:
            from services.automated_scheduler import AutomatedScheduler
            from services.broadcast_system import BroadcastSystem
            
            # Створення планувальника
            self.scheduler = AutomatedScheduler(self.bot, self.db_available)
            logger.info("✅ Automated scheduler створено")
            
            # Створення системи розсилок
            self.broadcast_system = BroadcastSystem(self.bot, self.db_available)
            logger.info("✅ Broadcast system створено")
            
            # Запуск автоматизації
            if await self.scheduler.start():
                self.automation_active = True
                logger.info("🤖 Повна автоматизація активна!")
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА - бот працює самостійно!")
                return True
            else:
                logger.warning("⚠️ Не вдалося запустити планувальник")
                return False
                
        except ImportError as e:
            logger.warning(f"⚠️ Automation services not available: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Automation initialization error: {e}")
            return False

    async def register_handlers(self):
        """Реєстрація всіх хендлерів з автоматизацією"""
        try:
            logger.info("🔧 Реєстрація хендлерів з автоматизацією...")
            
            # Реєстрація через handlers/__init__.py
            from handlers import register_handlers
            register_handlers(self.dp)
            
            # Додаткові основні хендлери з автоматизацією
            await self.register_automation_handlers()
            
            logger.info("✅ All handlers registered with automation support")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers registration failed: {e}")
            return False

    async def register_automation_handlers(self):
        """Хендлери з підтримкою автоматизації"""
        from aiogram import F
        from aiogram.filters import Command
        from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
        
        @self.dp.message(Command("start"))
        async def automated_start(message: Message):
            """Розширена команда /start з автоматизацією"""
            user_id = message.from_user.id
            first_name = message.from_user.first_name or "Друже"
            
            # Реєстрація користувача в БД (якщо доступна)
            if self.db_available:
                try:
                    from database import get_or_create_user
                    await get_or_create_user(
                        telegram_id=user_id,
                        username=message.from_user.username,
                        first_name=first_name
                    )
                except Exception as e:
                    logger.warning(f"⚠️ User registration failed: {e}")
            
            # Основне меню
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
                    InlineKeyboardButton(text="🛡️ Модерація", callback_data="moderation")
                ],
                [
                    InlineKeyboardButton(text="👥 Користувачі", callback_data="users"),
                    InlineKeyboardButton(text="📝 Контент", callback_data="content")
                ],
                [
                    InlineKeyboardButton(text="🔥 Трендове", callback_data="trending"),
                    InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings")
                ],
                [
                    InlineKeyboardButton(text="🚀 Масові дії", callback_data="bulk_actions"),
                    InlineKeyboardButton(text="📦 Бекап", callback_data="backup")
                ]
            ])
            
            # Додавання кнопки автоматизації для адміна
            if self.is_admin(user_id):
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(text="🤖 Автоматизація", callback_data="automation"),
                    InlineKeyboardButton(text="📢 Розсилки", callback_data="broadcasts")
                ])
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(text="❌ Вимкнути адмін меню", callback_data="disable_admin_menu")
                ])
            
            text = (
                f"🤖 <b>Вітаю, {first_name}!</b>\n\n"
                f"🧠😂🔥 <b>АВТОМАТИЗАЦІЯ АКТИВНА</b>\n\n"
                f"✅ Планувальник запущено\n"
                f"📝 Завдань у черзі: {len(self.scheduler.get_jobs()) if self.scheduler else 0}\n\n"
                f"🎯 <b>Автоматичні функції:</b>\n"
                f"• Щоденні розсилки контенту\n"
                f"• Автоматичне завершення дуелей\n"
                f"• Нагадування та сповіщення\n"
                f"• Очистка та оптимізація\n"
                f"• Тижневі та місячні звіти\n\n"
                f"📋 Оберіть дію з меню:"
            )
            
            await message.answer(text, reply_markup=keyboard)
            
            # Повідомлення адміну про запуск
            if self.is_admin(user_id) and self.automation_active:
                admin_text = (
                    f"✅ <b>Бот запущено в професійному режимі!</b>\n\n"
                    f"🤖 <b>Автоматизація:</b>\n"
                    f"📅 Налаштовано всі автоматичні завдання\n"
                    f"💾 База даних: {'Підключена' if self.db_available else 'Fallback'}\n"
                    f"🎯 Доступні функції: профіль, статистика, топ користувачів\n\n"
                    f"🔧 <b>Адмін функції:</b>\n"
                    f"/automation_status - статус планувальника\n"
                    f"/broadcast_now - ручна розсилка\n"
                    f"/scheduler_info - інформація про завдання"
                )
                await message.answer(admin_text)

        @self.dp.message(Command("automation_status"))
        async def automation_status(message: Message):
            """Статус автоматизації (тільки адмін)"""
            if not self.is_admin(message.from_user.id):
                await message.answer("❌ Недостатньо прав")
                return
            
            if self.scheduler:
                jobs = self.scheduler.get_jobs()
                status_text = (
                    f"🤖 <b>СТАТУС АВТОМАТИЗАЦІЇ</b>\n\n"
                    f"⚡ Планувальник: {'Активний' if self.automation_active else 'Неактивний'}\n"
                    f"📅 Завдань: {len(jobs)}\n"
                    f"💾 База даних: {'Підключена' if self.db_available else 'Fallback'}\n"
                    f"⏰ Запущено: {self.startup_time.strftime('%H:%M:%S')}\n\n"
                    f"📋 <b>Активні завдання:</b>\n"
                )
                
                for job in jobs[:5]:  # Показуємо перші 5
                    status_text += f"• {job.name}\n"
                
                if len(jobs) > 5:
                    status_text += f"... та ще {len(jobs) - 5} завдань"
                    
            else:
                status_text = "❌ Планувальник не ініціалізований"
            
            await message.answer(status_text)

        # Callback обробник
        @self.dp.callback_query(F.data.startswith(("stats", "moderation", "users", "content", "trending", "settings", "bulk_actions", "backup", "automation", "broadcasts", "disable_admin_menu")))
        async def enhanced_callback_handler(callback: CallbackQuery):
            """Розширений callback обробник з автоматизацією"""
            await callback.answer()
            
            data = callback.data
            user_id = callback.from_user.id
            
            if data == "automation" and self.is_admin(user_id):
                if self.scheduler:
                    jobs = self.scheduler.get_jobs()
                    text = (
                        f"🤖 <b>АВТОМАТИЗАЦІЯ</b>\n\n"
                        f"⚡ Статус: {'Активна' if self.automation_active else 'Неактивна'}\n"
                        f"📅 Завдань: {len(jobs)}\n"
                        f"🚀 Запущено: {self.startup_time.strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"📋 <b>Поточні завдання:</b>\n"
                    )
                    
                    for job in jobs:
                        next_run = job.next_run_time
                        if next_run:
                            text += f"• {job.name}: {next_run.strftime('%H:%M')}\n"
                        else:
                            text += f"• {job.name}: не заплановано\n"
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔄 Перезапустити", callback_data="restart_automation")],
                        [InlineKeyboardButton(text="⏸️ Призупинити", callback_data="pause_automation")],
                        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
                    ])
                    
                    await callback.message.edit_text(text, reply_markup=keyboard)
                else:
                    await callback.message.edit_text("❌ Планувальник не ініціалізований")
            
            elif data == "broadcasts" and self.is_admin(user_id):
                text = (
                    f"📢 <b>СИСТЕМА РОЗСИЛОК</b>\n\n"
                    f"🎯 Автоматичні розсилки:\n"
                    f"• 🌅 Ранкова (9:00) - найкращий контент\n"
                    f"• 🌆 Вечірня (20:00) - статистика дня\n"
                    f"• 📊 Тижнева (неділя 18:00) - дайджест\n"
                    f"• 🏆 Місячна (1 число) - підсумки\n\n"
                    f"📋 Ручні дії:"
                )
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📤 Розіслати зараз", callback_data="broadcast_now")],
                    [InlineKeyboardButton(text="📊 Статистика розсилок", callback_data="broadcast_stats")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
                ])
                
                await callback.message.edit_text(text, reply_markup=keyboard)
            
            elif data == "stats":
                stats_text = (
                    f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
                    f"⏰ Час роботи: {datetime.now() - self.startup_time}\n"
                    f"💾 БД: {'Підключена' if self.db_available else 'Недоступна'}\n"
                    f"🤖 Автоматизація: {'Активна' if self.automation_active else 'Неактивна'}\n"
                    f"📅 Планувальник: {len(self.scheduler.get_jobs()) if self.scheduler else 0} завдань\n\n"
                    f"🎯 Використовуйте інші кнопки для деталей!"
                )
                await callback.message.edit_text(stats_text)
            
            else:
                await callback.message.edit_text(f"🔧 Функція '{data}' в розробці!\n\n🤖 Автоматизація активна та працює у фоні.")
        
        logger.info("✅ Automation handlers зареєстровано")

    async def cleanup(self):
        """Правильне закриття ресурсів"""
        logger.info("🧹 Cleanup resources...")
        
        try:
            # Закриття планувальника
            if self.scheduler:
                await self.scheduler.stop()
                logger.info("✅ Scheduler stopped")
            
            # Закриття aiohttp сесії бота (виправлення помилки Unclosed client session)
            if self.bot and hasattr(self.bot, 'session') and self.bot.session:
                await self.bot.session.close()
                logger.info("✅ Bot session closed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

    async def main(self):
        """Головна функція"""
        logger.info("🤖 Starting Automated Ukrainian Telegram Bot...")
        
        try:
            # Завантаження налаштувань
            settings = await self.load_settings()
            
            # Ініціалізація бота
            if not await self.initialize_bot(settings):
                logger.error("❌ Failed to initialize bot")
                return False
            
            # Ініціалізація БД
            db_success = await self.initialize_database()
            if not db_success:
                logger.warning("⚠️ Working without full database support")
            
            # Ініціалізація автоматизації
            automation_success = await self.initialize_automation()
            if automation_success:
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА!")
            else:
                logger.warning("⚠️ Working without automation")
            
            # Реєстрація хендлерів
            if not await self.register_handlers():
                logger.error("❌ Failed to register handlers")
                return False
            
            logger.info("✅ Bot fully initialized with automation support")
            
            # Обробник сигналів для graceful shutdown
            def signal_handler():
                logger.info("🛑 Received shutdown signal")
                self.shutdown_event.set()
            
            if sys.platform != 'win32':
                signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
                signal.signal(signal.SIGINT, lambda s, f: signal_handler())
            
            # Запуск polling з graceful shutdown
            try:
                await self.dp.start_polling(self.bot)
            except KeyboardInterrupt:
                logger.info("⏹️ Bot stopped by user")
            
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            return False
        finally:
            # Cleanup ресурсів
            await self.cleanup()

async def main():
    """Точка входу"""
    bot = AutomatedUkrainianTelegramBot()
    await bot.main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Program interrupted")
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        sys.exit(1)